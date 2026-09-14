"""
export.py

Generates the downstream artifacts consumed by the frontend / cloud storage:
- label point GeoJSONs for each boundary type
- pmtiles (boundaries + centroid stats) via ogr2ogr -> tippecanoe -> pmtiles
- update_timestamp.json, tags_list.json, history.json
"""

import json
import os
import subprocess
from datetime import date

import config
from db import get_connection


def generate_labels_boundaries_geojson(boundary, output_dir:str = config.DATA_DIR):
    env = os.environ.copy()
    env["PGPASSWORD"] = config.POSTGRES_PASSWORD

    try:
        subprocess.run([
            "ogr2ogr",
            "-f", "GeoJSON",
            f"{os.path.join(output_dir, boundary)}_labels.geojson",
            f"PG:dbname={config.POSTGRES_DB} user={config.POSTGRES_USER} host={config.POSTGRES_HOST} port={config.POSTGRES_PORT}",
            "-sql",
            f"""
            SELECT
                code,
                name,
                center
            FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{boundary}"""
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise

    print(f"[OK] generated {os.path.join(output_dir, boundary)}_labels.geojson")


def generate_labels_boundaries_pmtiles_from_geojson(boundary:str, minzoom:int, maxzoom:int, extra_args:list = [], geojson_dir:str = config.DATA_DIR):
    assert os.path.exists(f"{os.path.join(geojson_dir, boundary)}_labels.geojson")

    try:
        subprocess.run([
            "tippecanoe",
            "-o", f"{os.path.join(geojson_dir, boundary)}_labels.mbtiles",
            "-l", f"{boundary}_labels",
            "-Z", str(minzoom),
            "-z", str(maxzoom),
            *extra_args,
            f"{os.path.join(geojson_dir, boundary)}_labels.geojson"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise

    pmtiles_path = f"{os.path.join(geojson_dir, boundary)}_labels.pmtiles"
    if os.path.exists(pmtiles_path):
        os.remove(pmtiles_path)

    try:
        subprocess.run([
            "pmtiles", "convert",
            f"{os.path.join(geojson_dir, boundary)}_labels.mbtiles",
            f"{os.path.join(geojson_dir, boundary)}_labels.pmtiles",
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise

    os.remove(f"{os.path.join(geojson_dir, boundary)}_labels.mbtiles")

    print(f"[OK] generated {os.path.join(geojson_dir, boundary)}_labels.pmtiles")


def generate_pmtiles(boundary: str, type: str, minzoom: int, maxzoom: int, extra_args: list = []):
    assert type in ['boundaries', 'centroid']

    geom_type = {
        "boundaries": "t.geom_4326",
        "centroid": "t.center",
    }

    env = os.environ.copy()
    env["PGPASSWORD"] = config.POSTGRES_PASSWORD

    sql_query = f"""
    SELECT
        t.code,
        t.name,
        t.osm_id,
        COUNT(p.*)::INT AS nb_pois,
        COUNT(p.ref_fr_siret)::INT AS nb_siret,
        COUNT(p.name)::INT AS nb_name,
        SUM(
            CASE
                WHEN p.email IS NOT NULL
                OR p.contact_email IS NOT NULL THEN 1
                ELSE 0
            END
        )::int AS nb_email,
        SUM(
            CASE
                WHEN p.phone IS NOT NULL
                OR p.contact_phone IS NOT NULL
                OR p.mobile IS NOT NULL
                OR p.contact_mobile IS NOT NULL THEN 1
                ELSE 0
            END
        )::int AS nb_phone,
        SUM(
            CASE
                WHEN p.instagram IS NOT NULL
                OR p.contact_instagram IS NOT NULL
                OR p.facebook IS NOT NULL
                OR p.contact_facebook IS NOT NULL
                OR p.website IS NOT NULL
                OR p.contact_website IS NOT NULL THEN 1
                ELSE 0
            END
        )::INT AS nb_website,
        SUM(
            CASE
                WHEN p."timestamp"::TIMESTAMPTZ < u.value::TIMESTAMPTZ - INTERVAL '5 years'
                THEN 1
                ELSE 0
            END
        )::INT AS nb_pois_outdated,
        COUNT(p.opening_hours)::INT AS nb_opening_hours,
        COUNT(p.wheelchair)::INT AS nb_wheelchair,
        ROUND(AVG(EXTRACT(epoch FROM u.value::TIMESTAMPTZ - p."timestamp"::TIMESTAMPTZ)) / 86400::NUMERIC)::INT AS avg_days_since_pois_update,
        {geom_type[type]}
    FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{boundary} t
    LEFT JOIN {config.POSTGRES_SCHEMA_POIS}.pois p ON ST_INTERSECTS(p.geom_4326, t.geom_4326)
    CROSS JOIN (
        SELECT value
        FROM {config.POSTGRES_SCHEMA_POIS}.osm2pgsql_properties
        WHERE property = 'replication_timestamp'
        LIMIT 1
    ) u
    GROUP BY
        t.code,
        t.name,
        t.osm_id,
        {geom_type[type]}
    """

    try:
        subprocess.run([
            "ogr2ogr",
            "-f", "GeoJSON",
            f"{os.path.join(config.DATA_DIR, boundary)}_stats_{type}.geojson",
            f"PG:dbname={config.POSTGRES_DB} user={config.POSTGRES_USER} host={config.POSTGRES_HOST} port={config.POSTGRES_PORT}",
            "-sql", sql_query
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise

    try:
        subprocess.run([
            "tippecanoe",
            "-o", f"{os.path.join(config.DATA_DIR, boundary)}_stats_{type}.mbtiles",
            "-l", f"{boundary}_stats_{type}",
            "-Z", str(minzoom),
            "-z", str(maxzoom),
            *extra_args,
            f"{os.path.join(config.DATA_DIR, boundary)}_stats_{type}.geojson"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise

    pmtiles_path = f"{os.path.join(config.DATA_DIR, boundary)}_stats_{type}.pmtiles"
    if os.path.exists(pmtiles_path):
        os.remove(pmtiles_path)

    try:
        subprocess.run([
            "pmtiles", "convert",
            f"{os.path.join(config.DATA_DIR, boundary)}_stats_{type}.mbtiles",
            f"{os.path.join(config.DATA_DIR, boundary)}_stats_{type}.pmtiles",
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise

    os.remove(f"{os.path.join(config.DATA_DIR, boundary)}_stats_{type}.geojson")
    os.remove(f"{os.path.join(config.DATA_DIR, boundary)}_stats_{type}.mbtiles")

    print(f"[OK] generated {os.path.join(config.DATA_DIR, boundary)}_stats_{type}.pmtiles")


def generate_update_timestamp_json(output_path_json=None):
    output_path_json = output_path_json or os.path.join(config.DATA_DIR, "update_timestamp.json")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT value
                FROM {config.POSTGRES_SCHEMA_POIS}.osm2pgsql_properties
                WHERE property = 'replication_timestamp'
            """)
            row = cur.fetchone()
            updated_at = row[0] if row else None

    with open(output_path_json, "w") as f:
        json.dump({"updated_at": updated_at}, f)
    print(f"[OK] écrit dans {output_path_json}")


def generate_tags_list_json(output_path_json=None):
    output_path_json = output_path_json or os.path.join(config.DATA_DIR, 'tags_list.json')

    query = f"""
        SELECT json_build_object(
            'generated_timestamp', u.value,
            'data', json_agg(
                json_build_object(
                    'key', class,
                    'value', subclass,
                    'count', count,
                    'desc', description
                ) ORDER BY count DESC
            )
        )
        FROM (
            SELECT
                p.class,
                p.subclass,
                count(*) AS count,
                t.description
            FROM {config.POSTGRES_SCHEMA_POIS}.pois p
            JOIN {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.regions r
                ON ST_Intersects(p.geom_4326, r.geom_4326)
            LEFT JOIN {config.POSTGRES_TAGINFO_TABLE} t
                USING (class, subclass)
            GROUP BY p.class, p.subclass, t.description
        ) sub
        CROSS JOIN (
            SELECT value
            FROM {config.POSTGRES_SCHEMA_POIS}.osm2pgsql_properties
            WHERE property = 'replication_timestamp'
            LIMIT 1
        ) u
        GROUP BY u.value
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()
            result = row[0] if row else {}

    with open(output_path_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, default=str)

    print(f"[OK] écrit dans {output_path_json}")


def generate_history_json(target_date: date, output_path_json=None):
    output_path_json = output_path_json or os.path.join(config.DATA_DIR, 'history.json')

    print("Generating history.json...")

    query = f"""
        WITH history_timestamp AS (
            SELECT timestamp AS value
            FROM {config.POSTGRES_SCHEMA_STATS}.communes
            WHERE DATE(timestamp) = %(target_date)s
            ORDER BY timestamp
            LIMIT 1
        ),

        stats_communes AS (
            SELECT *
            FROM {config.POSTGRES_SCHEMA_STATS}.communes
            WHERE timestamp = (SELECT value FROM history_timestamp)
        ),

        stats_epci AS (
            SELECT *
            FROM {config.POSTGRES_SCHEMA_STATS}.epci
            WHERE timestamp = (SELECT value FROM history_timestamp)
        ),

        stats_departements AS (
            SELECT *
            FROM {config.POSTGRES_SCHEMA_STATS}.departements
            WHERE timestamp = (SELECT value FROM history_timestamp)
        ),

        stats_regions AS (
            SELECT *
            FROM {config.POSTGRES_SCHEMA_STATS}.regions
            WHERE timestamp = (SELECT value FROM history_timestamp)
        )

        SELECT json_build_object(
            'date', (SELECT DATE(value) FROM history_timestamp),
            'layers', json_build_object(
                'communes', (
                    SELECT json_object_agg(code, json_build_object(
                        'nb_pois', nb_pois,
                        'nb_siret', nb_siret,
                        'nb_name', nb_name,
                        'nb_email', nb_email,
                        'nb_phone', nb_phone,
                        'nb_opening_hours', nb_opening_hours,
                        'nb_wheelchair', nb_wheelchair,
                        'nb_website', nb_website
                    ))
                    FROM stats_communes
                ),
                'epci', (
                    SELECT json_object_agg(code, json_build_object(
                        'nb_pois', nb_pois,
                        'nb_siret', nb_siret,
                        'nb_name', nb_name,
                        'nb_email', nb_email,
                        'nb_phone', nb_phone,
                        'nb_opening_hours', nb_opening_hours,
                        'nb_wheelchair', nb_wheelchair,
                        'nb_website', nb_website
                    ))
                    FROM stats_epci
                ),
                'departements', (
                    SELECT json_object_agg(code, json_build_object(
                        'nb_pois', nb_pois,
                        'nb_siret', nb_siret,
                        'nb_name', nb_name,
                        'nb_email', nb_email,
                        'nb_phone', nb_phone,
                        'nb_opening_hours', nb_opening_hours,
                        'nb_wheelchair', nb_wheelchair,
                        'nb_website', nb_website
                    ))
                    FROM stats_departements
                ),
                'regions', (
                    SELECT json_object_agg(code, json_build_object(
                        'nb_pois', nb_pois,
                        'nb_siret', nb_siret,
                        'nb_name', nb_name,
                        'nb_email', nb_email,
                        'nb_phone', nb_phone,
                        'nb_opening_hours', nb_opening_hours,
                        'nb_wheelchair', nb_wheelchair,
                        'nb_website', nb_website
                    ))
                    FROM stats_regions
                )
            )
        );
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, {"target_date": target_date})
            row = cur.fetchone()
            result = row[0] if row else {}

    with open(output_path_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, default=str)

    print(f"[OK] écrit dans {output_path_json}")
