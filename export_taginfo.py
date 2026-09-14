"""
export_taginfo.py

Télécharge la liste des tags (key/value) depuis l'API Taginfo de Geofabrik
(europe:france) pour une liste de clés OSM (shop, amenity, etc.)
et upsert le résultat dans une table PostgreSQL.

API utilisée :
  https://taginfo.geofabrik.de/{area}/api/4/tags/list?key={key}
"""

import time
import requests
import psycopg
from psycopg.sql import SQL, Identifier

API_URL = "https://taginfo.geofabrik.de/europe:france/api/4/tags/list"
LIST_CLASS = ["amenity", "shop", "craft", "office", "tourism", "leisure", "healthcare"]

# Ordre de préférence des langues pour la description
LANG_PRIORITY = ["fr", "en"]


def fetch_tags_for_key():
    session = requests.Session()
    all_data = []

    for key in LIST_CLASS:
        resp = session.get(API_URL, params={"key": key}, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        all_data.extend(payload.get("data", []))
        time.sleep(0.2)

    return all_data


def pick_description(entry: dict) -> str:
    wiki = entry.get("wiki") or {}
    for lang in LANG_PRIORITY:
        lang_entry = wiki.get(lang)
        if lang_entry and lang_entry.get("description"):
            return lang_entry["description"]
    return ""


def normalize_rows(raw_entries):
    rows = []
    for entry in raw_entries:
        rows.append({
            "key": entry.get("key"),
            "value": entry.get("value") or "",
            "description": pick_description(entry),
            "count_all": entry.get("count_all", 0),
        })
    return rows


def write_postgres(rows, pg_table, pg_dsn):
    create_sql = SQL("""
        CREATE TABLE IF NOT EXISTS {table} (
            class       TEXT NOT NULL,
            subclass    TEXT NOT NULL,
            description TEXT,
            count_all   INTEGER,
            PRIMARY KEY (class, subclass)
        );
    """).format(table=Identifier(pg_table))

    upsert_sql = SQL("""
        INSERT INTO {table} (class, subclass, description, count_all)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (class, subclass) DO UPDATE SET
            description = EXCLUDED.description,
            count_all   = EXCLUDED.count_all;
    """).format(table=Identifier(pg_table))

    with psycopg.connect(**pg_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(create_sql)
            cur.executemany(
                upsert_sql,
                [(r["key"], r["value"], r["description"], r["count_all"]) for r in rows],
            )
        conn.commit()

    print(f"[OK] {len(rows)} lignes insérées/mises à jour dans la table {pg_table}")


def export_taginfo(pg_table, pg_dsn):
    raw_entries = fetch_tags_for_key()
    rows = normalize_rows(raw_entries)
    print(f"{len(rows)} lignes au total")
    write_postgres(rows, pg_table, pg_dsn)