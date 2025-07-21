import os
from datetime import datetime
from typing import Tuple, Dict, Any

import requests
import time

from secrets.constants import BUCKET, LOCAL_DIR


def sync_s3_files(s3):

    os.makedirs(LOCAL_DIR, exist_ok=True)

    response = s3.list_objects_v2(Bucket=BUCKET)

    for obj in response.get('Contents', []):
        key = obj['Key']
        etag = obj['ETag'].strip('"')
        local_path = os.path.join(LOCAL_DIR, key.replace('/', '_'))
        meta_path = local_path + '.etag'

        # Check if local file exists and ETag matches
        if os.path.exists(local_path) and os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                local_etag = f.read().strip()
            if local_etag == etag:
                print(f"Up-to-date: {key}")
                continue  # skip download

        # Download file and save ETag
        print(f"Downloading: {key}")
        s3.download_file(BUCKET, key, local_path)

        with open(meta_path, 'w') as f:
            f.write(etag)


def file_text(file_path, n_lines):
    """Get the last n lines from a text file."""
    if n_lines is None:
        # Read the whole file
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    with open(file_path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        lines = []
        buf = bytearray()
        while end > 0 and len(lines) < n_lines:
            end -= 1
            f.seek(end)
            byte = f.read(1)
            if byte == b'\n':
                if buf:
                    lines.append(buf.decode('utf-8', errors='replace')[::-1] + '\n')
                    buf = bytearray()
            else:
                buf.extend(byte)
        if buf:
            lines.append(buf.decode('utf-8', errors='replace')[::-1])
        return ''.join(reversed(lines))


def file_text_doi(file_path: str):
    """Get a text file."""
    extention = file_path.rsplit('.', maxsplit=1)[1]
    if extention != 'png':
        # Read the whole file
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()


def get_connection_details(lines: list[str]) -> list[dict]:
    """Returns a list of the following schema:
        {
			start_time: time,
			end_time: time,
			no_packets_sent: int,
			valid_handshake: bool,
			disconnected: bool
		}
    """
    conn_list = []

    valid_count = 0

    def conn_create(time: str) -> dict:
        return {
                'valid_handshake': False,
                'disconnected': False,
                'no_packets_sent': 0,
                'bytes_transferred': 0,
                'start_time': time,       # put start connection time
                'end_time': time,
            }

    for line in lines:
        parts = line.split()
        timestamp = parts[0] + ' ' + parts[1]

        if '>>>' in parts and '[S],' in parts:      # attacker sends a SYN packet to initiate the connection
            valid_count = 1
            connection = conn_create(timestamp)
            conn_list.append(connection)                              # append to connection list

        elif valid_count == 1 and ('<<<' in parts and '[S.],' in parts):    # honeypot responds with SYN-ACK
            valid_count = 2
            conn_list[-1]['end_time'] = timestamp       # update end time

        elif valid_count == 2 and ('>>>' in parts and '[.],' in parts):
            conn_list[-1]['valid_handshake'] = True
            conn_list[-1]['end_time'] = timestamp
            valid_count = 3

        if '>>>' in parts and int(parts[-1]) > 0:
            if not conn_list:
                connection = conn_create(timestamp)
                conn_list.append(connection)
            conn_list[-1]['no_packets_sent'] += 1           # count messages with payload
            conn_list[-1]['bytes_transferred'] += int(parts[-1])     # add msg length

        if '[F.],' in parts or '[FP.],' in parts or '[R],' in parts:
            if not conn_list:
                connection = conn_create(timestamp)
                conn_list.append(connection)
            conn_list[-1]['disconnected'] = True
            conn_list[-1]['end_time'] = timestamp
            valid_count = 0

    return conn_list


def get_geo_data(ip: str) -> dict:
    url = f"https://ipwho.is/{ip}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            return build_geodata_object(data)
        else:
            print(f"API error for IP {ip}: {data.get('message', 'Unknown error')}")

    except requests.RequestException as e:
        print(f"Network error for IP {ip}: {e}")

    return {}


def build_geodata_object(data: dict) -> dict[str, Any]:
    return {
        'location': {
            'country': data.get('country', ''),
            'region': data.get('region', ''),
            'city': data.get('city', ''),
            'lat': data.get('latitude', ''),
            'long': data.get('longitude', ''),
        },
        'network': {
            'ip_type': data.get('type', ''),
            'asn': data.get('connection', {}).get('asn', ''),
            'org': data.get('connection', {}).get('org', ''),
            'isp': data.get('connection', {}).get('isp', ''),
            'domain': data.get('connection', {}).get('domain', ''),
        },
        'timezone_id': data.get('timezone', {}).get('id', ''),
    }
