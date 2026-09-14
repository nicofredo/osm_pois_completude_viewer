"""
update.py

Everything needed to keep the POIs schema up to date with OSM:
- authenticating against Geofabrik's internal replication feed
- fetching state files / change files
- applying diffs with osm2pgsql --append
- refreshing the history/stats tables after each applied diff

Entry point: loop_update_until_up_to_date(headers)
"""

import os
import subprocess

import requests

import config
from db import get_connection
from create import insert_boundaries_stats_to_history_tables


def get_geofabrik_cookie():
    script_path = config.OAUTH_COOKIE_CLIENT_PY_PATH
    output_path = os.path.join(config.DATA_DIR, config.COOKIE_FILENAME)
    username = config.OSM_USERNAME
    password = config.OSM_PASSWORD
    consumer_url = config.CONSUMER_URL

    result = subprocess.run(
        [
            "python", script_path,
            "-o", output_path,
            "-u", username,
            "-p", password,
            "-c", consumer_url
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise RuntimeError(f"oauth_cookie_client.py failed with exit code {result.returncode}")

    print(f"Cookie généré : {output_path}")
    return output_path


def load_cookie_header() -> str:
    with open(os.path.join(config.DATA_DIR, config.COOKIE_FILENAME), "r") as f:
        return f.read().strip()


def get_last_replication_sequence_number(replication_base_url: str, headers):
    url = f"{replication_base_url}/state.txt"
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    for line in response.text.splitlines():
        line = line.strip()
        if line.startswith("sequenceNumber="):
            return int(line.split("=", 1)[1])

    raise ValueError(f"sequenceNumber not found in {url}")


def get_state_parameters(url: str, headers, write: bool = True, path=None):
    path = path or config.CHANGE_FILE_SUBFOLDER

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    if write:
        filename = str(int(''.join(url.split("/")).replace('.state.txt', '')[-9:])) + '.state.txt'  # e.g. '4765.state.txt'
        with open(os.path.join(path, filename), "wb") as f:
            f.write(response.content)

    for line in response.text.splitlines():
        line = line.strip()
        if line.startswith("sequenceNumber="):
            sequence_number = int(line.split("=", 1)[1])
        elif line.startswith("timestamp"):
            timestamp = line.split("=", 1)[1].replace('\\', '')
    return {"sequenceNumber": sequence_number, "timestamp": timestamp}


def update_state_parameters_to_db(state: dict, postgres_schema):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE {postgres_schema}.osm2pgsql_properties SET value = %(seq)s WHERE property = 'replication_sequence_number'",
                {"seq": str(state['sequenceNumber'])}
            )
            cur.execute(f"SELECT value FROM {postgres_schema}.osm2pgsql_properties WHERE PROPERTY = 'replication_sequence_number'")
            print('replication_sequence_number', cur.fetchone()[0])

            cur.execute(f"UPDATE {postgres_schema}.osm2pgsql_properties SET value = '{state['timestamp']}' WHERE property = 'replication_timestamp'")
            cur.execute(f"SELECT value FROM {postgres_schema}.osm2pgsql_properties WHERE PROPERTY = 'replication_timestamp'")
            print('replication_timestamp', cur.fetchone()[0])


def get_local_sequence_number(postgres_schema):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT value FROM {postgres_schema}.osm2pgsql_properties WHERE property = 'updatable'")
            updatable = cur.fetchone()[0]
            if updatable != 'true':
                raise ValueError(f"{postgres_schema} is not updatable")
            cur.execute(f"SELECT value FROM {postgres_schema}.osm2pgsql_properties WHERE property = 'replication_sequence_number'")
            replication_sequence_number = int(cur.fetchone()[0])
            return replication_sequence_number


def download_change_file(url: str, headers, dest_dir: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    filename = str(int(''.join(url.split("/")).replace('.osc.gz', '')[-9:])) + '_brut.osc.gz'  # e.g. '4765_brut.osc.gz'
    filepath_before_simplification = os.path.join(dest_dir, filename)

    if os.path.exists(filepath_before_simplification):
        os.remove(filepath_before_simplification)

    with requests.get(url, headers=headers, stream=True, timeout=(30, 60)) as response:
        response.raise_for_status()
        with open(filepath_before_simplification, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    filename_simplified = str(int(''.join(url.split("/")).replace('.osc.gz', '')[-9:])) + '.osc.gz'  # e.g. '4765.osc.gz'
    filepath_simplified = os.path.join(dest_dir, filename_simplified)

    if os.path.exists(filepath_simplified):
        os.remove(filepath_simplified)

    try:
        subprocess.run([
            "osmium",
            "merge-changes",
            "--simplify",
            filepath_before_simplification,
            "-o",
            filepath_simplified,
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise

    os.remove(filepath_before_simplification)

    return filepath_simplified


def osm2pgsql_append(osc_path: str):
    env = os.environ.copy()
    env["PGPASSWORD"] = config.POSTGRES_PASSWORD
    cmd = [
        "osm2pgsql",
        "-U", config.POSTGRES_USER,
        "-d", config.POSTGRES_DB,
        "-H", config.POSTGRES_HOST,
        "-P", config.POSTGRES_PORT,
        "--schema", config.POSTGRES_SCHEMA_POIS,
        "--append",
        "--slim",
        osc_path,
    ]
    subprocess.run(cmd, env=env, check=True)
    print(str(osc_path.split('/')[-1]), "update finished")


def osm2pgsql_update_pois_and_generate_stats(headers):
    with get_connection() as conn:
        with conn.cursor() as cur:
            local_replication_sequence_number = get_local_sequence_number(config.POSTGRES_SCHEMA_POIS)
            cur.execute(f"select value from {config.POSTGRES_SCHEMA_POIS}.osm2pgsql_properties where property = 'replication_base_url';")
            replication_base_url = cur.fetchone()[0]

            last_replication_sequence_number = get_last_replication_sequence_number(replication_base_url, headers)
            update_available = last_replication_sequence_number > local_replication_sequence_number

    if update_available:
        print("update available")
        next_sequence_number = f"{local_replication_sequence_number + 1:09d}"
        state_file_url = f"{replication_base_url}/{next_sequence_number[0:3]}/{next_sequence_number[3:6]}/{next_sequence_number[6:9]}.state.txt"
        change_file_url = f"{replication_base_url}/{next_sequence_number[0:3]}/{next_sequence_number[3:6]}/{next_sequence_number[6:9]}.osc.gz"
        print(change_file_url)
        update_filepath = download_change_file(change_file_url, headers, config.CHANGE_FILE_SUBFOLDER)

        state = get_state_parameters(state_file_url, headers)
        osm2pgsql_append(update_filepath)
        update_state_parameters_to_db(state, config.POSTGRES_SCHEMA_POIS)

        insert_boundaries_stats_to_history_tables()
        print('insert history tables done')
        return True

    else:
        print(f'{config.POSTGRES_SCHEMA_POIS} No update available')
        return False


def loop_update_until_up_to_date(headers):
    update_available = True
    count_days = 0
    while update_available:
        update_available = osm2pgsql_update_pois_and_generate_stats(headers)
        count_days += 1
    print('Loop finished,', count_days, 'iteration(s)')
