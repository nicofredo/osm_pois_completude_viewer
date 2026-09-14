"""
create.py

Everything needed to build the database from scratch:
- importing INSEE administrative boundaries (regions/departements/epci/communes)
- importing OSM boundaries and POIs via osm2pgsql
- reconciling INSEE codes with OSM relation ids
- creating and populating the history/stats tables

Entry point: create_db()
"""

import os
import subprocess

import psycopg
import requests

import config
from db import get_connection, create_postgis_if_not_exists, create_schema_if_not_exists
from export_taginfo import export_taginfo


def import_boundaries_insee_to_pg(url, name, download=True, remove_file:bool=True):
    if download:
        with requests.get(url, stream=True, timeout=(30, 60)) as response:
            response.raise_for_status()
            with open(os.path.join(config.DATA_DIR, "temp.geojson"), "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 Mo
                    f.write(chunk)
        os.replace(os.path.join(config.DATA_DIR, "temp.geojson"), os.path.join(config.DATA_DIR, f"{name}.geojson"))
        print(f'{name}.geojson downloaded')
    else:
        assert os.path.exists(os.path.join(config.DATA_DIR, f'{name}.geojson'))

    env = os.environ.copy()
    env["PGPASSWORD"] = config.POSTGRES_PASSWORD

    subprocess.run(
        [
            "ogr2ogr", "-f", "PostgreSQL",
            f"PG:dbname={config.POSTGRES_DB} user={config.POSTGRES_USER} host={config.POSTGRES_HOST} port={config.POSTGRES_PORT}",
            os.path.join(config.DATA_DIR, f"{name}.geojson"),
            "-nln", f"{config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{name}",
        ],
        env=env,
        check=True,
    )

    if remove_file:
        os.remove(f'{name}.geojson')

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{name} DROP COLUMN ogc_fid")
            print(cur.statusmessage)
            cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{name} ADD PRIMARY KEY (code)")
            print(cur.statusmessage)
            cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{name} RENAME COLUMN wkb_geometry TO geom_4326")
            print(cur.statusmessage)
            cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{name} RENAME COLUMN nom TO name")
            print(cur.statusmessage)
            cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{name} ADD COLUMN center geometry(Point,4326) GENERATED ALWAYS AS (ST_SetSRID((ST_MaximumInscribedCircle(geom_4326)).center, 4326)) STORED")
            print(cur.statusmessage)

            if name == 'communes':
                cur.execute(f"DELETE FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.communes WHERE plm")
                print(cur.statusmessage)
                cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.communes DROP COLUMN plm")
                print(cur.statusmessage)
                cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.communes DROP COLUMN commune")
                print(cur.statusmessage)
                cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.communes ADD FOREIGN KEY (departement) REFERENCES {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.departements (code)")
                print(cur.statusmessage)
                cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.communes ADD FOREIGN KEY (region) REFERENCES {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.regions (code)")
                print(cur.statusmessage)
                cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.communes ADD FOREIGN KEY (epci) REFERENCES {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.epci (code)")
                print(cur.statusmessage)

                cur.execute(f"DELETE FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.communes WHERE code LIKE '97%' OR code LIKE '98%'")
                print(cur.statusmessage)

                cur.execute(f"DELETE FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.epci WHERE code NOT IN (SELECT DISTINCT epci FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.communes WHERE epci IS NOT NULL)")
                print(cur.statusmessage)
                cur.execute(f"DELETE FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.departements WHERE code NOT IN (SELECT DISTINCT departement FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.communes WHERE departement IS NOT NULL)")
                print(cur.statusmessage)
                cur.execute(f"DELETE FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.regions WHERE code NOT IN (SELECT DISTINCT region FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.communes WHERE region IS NOT NULL)")
                print(cur.statusmessage)


def osm2pgsql_import(updatable: bool, pbf_path, lua_path, pg_schema):
    cmd = [
        "osm2pgsql",
        "-U", config.POSTGRES_USER,
        "-d", config.POSTGRES_DB,
        "--schema", pg_schema,
        "-H", config.POSTGRES_HOST,
        "-P", config.POSTGRES_PORT,
        "-x",
        "-O", "flex",
        "-S", lua_path,
    ]

    if updatable:
        cmd.append("--slim")
        cmd += ["-C", "5000"]

    cmd += ["-c", pbf_path]

    env = os.environ.copy()
    env["PGPASSWORD"] = config.POSTGRES_PASSWORD

    subprocess.run(cmd, env=env, check=True)


def add_osm_id_to_insee_boundaries_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            for boundary_type in ['communes', 'epci', 'departements', 'regions']:
                cur.execute(f"ALTER TABLE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{boundary_type} ADD COLUMN osm_id INTEGER")
                cur.execute(f"UPDATE {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{boundary_type} c SET osm_id = e.osm_id FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN_OSM}.{boundary_type} e WHERE c.code = e.code")
                print(cur.statusmessage)
                cur.execute(f"SELECT COUNT(*) FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{boundary_type} WHERE osm_id IS NULL")
                print(cur.fetchone()[0], f'{boundary_type} sans osm_id A METTRE A JOUR MANUELLEMENT')
                cur.execute(f"SELECT code,name FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{boundary_type} WHERE osm_id IS NULL")
                rows = cur.fetchall()
                for row in rows:
                    print(row)
    # MANUALLY UPDATE BY FINDING CORRESPONDING OSM RELATION ID FOR EACH ROW AND UPDATING USING THE FOLLOWING SQL QUERY IN PGSQL:
    # UPDATE <POSTGRES_SCHEMA_LIMITES_ADMIN>.<boundary_type> SET osm_id = '<rel_id>' WHERE code = '<code>';
    # AND FINALLY CHECKING THAT NO osm_id IS NULL WITH :
    # SELECT COUNT(*) FROM <POSTGRES_SCHEMA_LIMITES_ADMIN>.<boundary_type> WHERE osm_id IS NULL;


def create_history_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # crée le schéma si besoin
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {config.POSTGRES_SCHEMA_STATS};")

            for territoire in ['communes', 'epci', 'departements', 'regions']:
                ddl = f"""
                    CREATE TABLE IF NOT EXISTS {config.POSTGRES_SCHEMA_STATS}.{territoire} (
                        timestamp                  TIMESTAMP WITH TIME ZONE NOT NULL,
                        code                       TEXT NOT NULL,
                        nb_pois                    INTEGER,
                        nb_siret                   INTEGER,
                        nb_name                    INTEGER,
                        nb_website                 INTEGER,
                        nb_email                   INTEGER,
                        nb_phone                   INTEGER,
                        nb_opening_hours           INTEGER,
                        nb_wheelchair              INTEGER,
                        avg_days_since_pois_update INTEGER,
                        PRIMARY KEY (timestamp, code)
                    );
                """
                cur.execute(ddl)
                print(f"Table {config.POSTGRES_SCHEMA_STATS}.{territoire} OK")
        conn.commit()


def insert_boundaries_stats_to_history_tables(pg_schema_pois=None):
    pg_schema_pois = pg_schema_pois or config.POSTGRES_SCHEMA_POIS

    with get_connection() as conn:
        with conn.cursor() as cur:
            for boundary_type in ('communes', 'epci', 'departements', 'regions'):
                cur.execute(f"""
                    INSERT INTO {config.POSTGRES_SCHEMA_STATS}.{boundary_type} (
                        timestamp,
                        code,
                        nb_pois,
                        nb_siret,
                        nb_name,
                        nb_email,
                        nb_phone,
                        nb_website,
                        nb_opening_hours,
                        nb_wheelchair,
                        avg_days_since_pois_update
                    )
                    SELECT
                        u.value::timestamptz AS timestamp,
                        t.code,
                        COUNT(p.*) AS nb_pois,
                        COUNT(p.ref_fr_siret) AS nb_siret,
                        COUNT(p.name) AS nb_name,
                        sum(
                            CASE
                                WHEN p.email IS NOT NULL OR p.contact_email IS NOT NULL THEN 1
                                ELSE 0
                            END
                        )::integer AS nb_email,
                        sum(
                            CASE
                                WHEN p.phone IS NOT NULL OR p.contact_phone IS NOT NULL OR p.mobile IS NOT NULL OR p.contact_mobile IS NOT NULL THEN 1
                                ELSE 0
                            END
                        )::integer AS nb_phone,
                        sum(
                            CASE
                                WHEN p.instagram IS NOT NULL OR p.contact_instagram IS NOT NULL OR p.facebook IS NOT NULL OR p.contact_facebook IS NOT NULL OR p.website IS NOT NULL OR p.contact_website IS NOT NULL THEN 1
                                ELSE 0
                            END
                        )::integer AS nb_website,
                        COUNT(p.opening_hours) AS nb_opening_hours,
                        COUNT(p.wheelchair) AS nb_wheelchair,
                        ROUND(AVG(EXTRACT(epoch FROM u.value::timestamptz - p."timestamp")) / 86400::numeric)::integer AS avg_days_since_pois_update
                    FROM {config.POSTGRES_SCHEMA_LIMITES_ADMIN}.{boundary_type} t
                    LEFT JOIN {pg_schema_pois}.pois p ON St_Intersects(p.geom_4326, t.geom_4326)
                    CROSS JOIN (
                        SELECT value
                        FROM {pg_schema_pois}.osm2pgsql_properties
                        WHERE property = 'replication_timestamp'
                        LIMIT 1
                    ) u
                    GROUP BY u.value, t.code
                    ON CONFLICT DO NOTHING;
                """)
                # print(cur.statusmessage)
                # print(f'insert stats {boundary_type} OK')


def create_db():
    create_postgis_if_not_exists()

    create_schema_if_not_exists(config.POSTGRES_SCHEMA_LIMITES_ADMIN)
    os.makedirs(config.DATA_DIR)
    import_boundaries_insee_to_pg(config.URL_REGIONS_INSEE_GEOJSON, 'regions')
    import_boundaries_insee_to_pg(config.URL_DEPARTEMENTS_INSEE_GEOJSON, 'departements')
    import_boundaries_insee_to_pg(config.URL_EPCI_INSEE_GEOJSON, 'epci')
    import_boundaries_insee_to_pg(config.URL_COMMUNES_INSEE_GEOJSON, 'communes')
    print('import boundaries from insee finished')

    create_schema_if_not_exists(config.POSTGRES_SCHEMA_LIMITES_ADMIN_OSM)
    osm2pgsql_import(updatable=False, pbf_path=config.PBF_PATH, lua_path=config.BOUNDARIES_LUA_FLEX, pg_schema=config.POSTGRES_SCHEMA_LIMITES_ADMIN_OSM)
    print('import boundaries from osm finished')

    add_osm_id_to_insee_boundaries_tables()
    # and then check if all boundaries from schema POSTGRES_SCHEMA_LIMITES_ADMIN have an osm_id, and manually add the missing ones if there are some

    ### creating the pois table
    create_schema_if_not_exists(config.POSTGRES_SCHEMA_POIS)
    osm2pgsql_import(updatable=True, pbf_path=config.PBF_PATH, lua_path=config.POIS_LUA_FLEX, pg_schema=config.POSTGRES_SCHEMA_POIS)
    print('import pois finished')

    create_history_tables()
    insert_boundaries_stats_to_history_tables()
    print('insert stats finished')

    # CREATE TAGINFO TABLE FOR TAGS DESCRIPTIONS
    export_taginfo(
        pg_table=config.POSTGRES_TAGINFO_TABLE,
        pg_dsn={
            "dbname": config.POSTGRES_DB,
            "user": config.POSTGRES_USER,
            "password": config.POSTGRES_PASSWORD,
            "host": config.POSTGRES_HOST,
            "port": config.POSTGRES_PORT,
        },
    )
