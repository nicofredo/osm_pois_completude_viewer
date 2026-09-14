"""
main.py

Orchestration entry point — equivalent to the old `if __name__ == '__main__':`
block, but now delegating to the create / update / export modules and
selected via CLI flags instead of comment/uncomment.

Examples
--------
    python main.py create                  # build the db from scratch
    python main.py update                  # pull OSM diffs until up to date
    python main.py export --include_labels   # labels + pmtiles + json, then upload
    python main.py update export           # typical daily cron job
    python main.py history --date 2026-01-01 --pbf data/france-260101-internal.osm.pbf
    python main.py all                     # update + export (default daily run)

Each step is also a plain function, so you can still import and call
create.create_db(), update.loop_update_until_up_to_date(...), etc. directly
from your own scripts / scheduler if you don't want the CLI.
"""

import argparse
import os
from datetime import date
from pathlib import Path

import boto3

import config
from create import (
    create_db,
    create_schema_if_not_exists,
    insert_boundaries_stats_to_history_tables,
    osm2pgsql_import,
)
from update import get_geofabrik_cookie, load_cookie_header, loop_update_until_up_to_date
from export import (
    generate_labels_boundaries_geojson,
    generate_labels_boundaries_pmtiles_from_geojson,
    generate_pmtiles,
    generate_update_timestamp_json,
    generate_tags_list_json,
    generate_history_json,
)

BOUNDARIES = ['communes', 'epci', 'departements', 'regions']

PMTILES_OPTIONS = {
    "regions":       {"minzoom": 0, "maxzoom": 9, "extra_args": []},
    "departements":  {"minzoom": 0, "maxzoom": 9, "extra_args": []},
    "epci":          {"minzoom": 3, "maxzoom": 9, "extra_args": []},
    "communes":      {"minzoom": 5, "maxzoom": 9, "extra_args": ["--no-tile-size-limit"]},
}

def upload_file_to_storage(file_path):
    session = boto3.Session(profile_name=config.STORAGE_PROFILE_NAME)
    s3 = session.client("s3", endpoint_url=config.STORAGE_ENDPOINT_URL)
    s3.upload_file(
        Filename=file_path,
        Bucket=config.STORAGE_BUCKET,
        Key=Path(file_path).name,
    )
    print(f"{file_path} uploaded to cloud storage")


def upload_outputs_to_storage(include_labels:bool = False):
    if include_labels:
        for boundary in BOUNDARIES:
            upload_file_to_storage(os.path.join(config.DATA_DIR, f"{boundary}_labels.geojson"))
        upload_file_to_storage(os.path.join(config.DATA_DIR, "communes_labels.pmtiles"))

    for boundary in BOUNDARIES:
        for type in ['boundaries', 'centroid']:
            upload_file_to_storage(os.path.join(config.DATA_DIR, f"{boundary}_stats_{type}.pmtiles"))

    upload_file_to_storage(os.path.join(config.DATA_DIR, "update_timestamp.json"))
    upload_file_to_storage(os.path.join(config.DATA_DIR, "tags_list.json"))


# -----------------------------------------------------------------
# STEPS
# -----------------------------------------------------------------

def run_create():
    """Build the database from scratch."""
    create_db()


def run_update():
    """Pull OSM replication diffs until the pois schema is up to date & for each iteration add stats to the stats table"""
    get_geofabrik_cookie()
    headers = {"Cookie": load_cookie_header()}
    loop_update_until_up_to_date(headers)


def run_export(include_labels:bool = False):
    """Generate labels geojson, pmtiles, and the small json artifacts, then upload."""
    if include_labels:
        for boundary in BOUNDARIES:
            generate_labels_boundaries_geojson(boundary)

        generate_labels_boundaries_pmtiles_from_geojson('communes',4,9,['-r1'])

    for boundary, options in PMTILES_OPTIONS.items():
        for type in ['boundaries', 'centroid']:
            extra_args = ["-r1"] + options["extra_args"] if type == "centroid" else options["extra_args"]
            generate_pmtiles(
                boundary=boundary,
                type=type,
                minzoom=options['minzoom'],
                maxzoom=options['maxzoom'],
                extra_args=extra_args,
            )

    generate_update_timestamp_json()
    generate_tags_list_json()
    upload_outputs_to_storage(include_labels = include_labels)


def run_history(target_date: date, historical_pbf_path: str="", upload:bool=True, with_import:bool=True):
    """
    Add a historical snapshot from an old pbf (e.g. Geofabrik's yearly
    archive for each January 1st), then generate + upload history.json.
    """
    if with_import:
        if not historical_pbf_path:
            raise KeyError('osm.pbf path not given')
        pg_schema = f"{config.POSTGRES_SCHEMA_POIS}_{target_date.strftime('%Y%m%d')}"
        create_schema_if_not_exists(pg_schema)

        osm2pgsql_import(updatable=False, pbf_path=historical_pbf_path, lua_path=config.POIS_LUA_FLEX, pg_schema=pg_schema)
        print('import pois finished')

        insert_boundaries_stats_to_history_tables(pg_schema_pois=pg_schema)
    generate_history_json(target_date)
    if upload:
        upload_file_to_storage(os.path.join(config.DATA_DIR, "history.json"))


# -----------------------------------------------------------------
# CLI
# -----------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="France OSM POIs pipeline")
    parser.add_argument(
        "steps",
        nargs="+",
        choices=["create", "update", "export", "history"],
        help="Which step(s) to run, in order",
    )
    parser.add_argument(
        "--include_labels",
        action="store_true",
        help=f"[export] Generate and send the labels geojson (for the initial export)"
    )
    parser.add_argument(
        "--date",
        type=lambda s: date.fromisoformat(s),
        help="[history] Date of replication of historical pbf import (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--pbf",
        help="[history] Path to the historical osm.pbf file (if not already imported)",
    )
    parser.add_argument(
        "--already_imported",
        action="store_true",
        help=f"[history] Skip pbf import if already imported"
    )
    parser.add_argument(
        "--not_upload_history",
        action="store_true",
        help=f"[history] Skip upload history json to distant storage"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    steps = args.steps

    if "all" in steps:
        steps = ["update", "export"]

    if "history" in steps and not args.date:
        raise SystemExit("--date YYYY-MM-DD is required for the 'history' step")

    if "history" in steps and not args.pbf and not args.already_imported:
        raise SystemExit("historical pbf is required for the 'history' step")

    for step in steps:
        if step == "create":
            run_create()
        elif step == "update":
            run_update()
        elif step == "history":
            run_history(target_date=args.date, historical_pbf_path=args.pbf, upload=not(args.not_upload_history), with_import=not(args.already_imported))
        elif step == "export":
            run_export(include_labels=args.include_labels)


if __name__ == '__main__':
    main()
