import os
import time
import random

from secrets.constants import db, MY_IP, ORDERED_LOGS, ATTACKER_DATA, LOCAL_DIR, COMMANDS, LINE_NR_OLD, BLACKLIST_DATES
from utils import get_connection_details, get_geo_data


# there are 2 collections
# the first contains raw log data organized by {ip:port} tuple
# the last contains extracted data and


def drop_and_create_collection(collection_name: str):
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
    db.create_collection(collection_name)
    return db[collection_name]


def create_collection_if_doesnt_exist(collection_name: str):
    if collection_name in db.list_collection_names():
        return db[collection_name]
    db.create_collection(collection_name)
    return db[collection_name]


def organize_raw_data(log_file: str):
    """Function reads from the specified log file and inserts lines belonging to {ip:port} tuple in collection"""

    collection = drop_and_create_collection(ORDERED_LOGS)

    with open(log_file) as f:
        for line in f:
            # filter lines
            if line[0:4] != '2025':  # is not a proper log line
                continue

            if line.find(MY_IP) != -1:  # test communication
                continue

            parts = line.split(maxsplit=6)

            # get the attacker address
            if parts[3].find('ssh') == -1:
                attacker_addr = parts[3].strip(':')
                line = ' '.join(parts[:2]) + ' >>> ' + parts[6]
            else:
                attacker_addr = parts[5].strip(':')
                line = ' '.join(parts[:2]) + ' <<< ' + parts[6]

            # add to database:
            collection.update_one(
                {'_id': attacker_addr},
                {'$push': {'lines': line}},
                upsert=True
            )


def extract_connection_details():
    """Extract connection details like timestamps, valid handshake, packets sent"""

    collection = create_collection_if_doesnt_exist(ATTACKER_DATA)

    logs_collection = db[ORDERED_LOGS]

    for doc in logs_collection.find({}):
        ip, port = doc['_id'].rsplit('.', maxsplit=1)[:]
        connection_details = get_connection_details(doc['lines'])
        collection.update_one(
            {'_id': ip},
            {
                '$addToSet': {
                    'ports': port,
                    'connections': {
                        '$each': connection_details
                    }
                }
            },
            upsert=True
        )


def insert_ip_info():
    """Parse new ip`s and insert ip address information"""

    collection = db[ATTACKER_DATA]

    # create cursor
    cursor = collection.find({'geo': {'$exists': False}}).batch_size(50)

    for i, doc in enumerate(cursor):
        ip = doc['_id']

        geo_data = get_geo_data(ip)

        if geo_data:
            collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'geo': geo_data}}
            )

        print(f'Inserted {i + 1} IP`s')

        time.sleep(random.uniform(0.8, 1.2))  # sleep to avoid ip banning


def pipeline(files: list[str]):
    """Pipeline for attacker data extraction and processing"""

    for file in files:

        file_path = os.path.join(LOCAL_DIR, file)

        print(f'Parsing {file} file...\nOrganize logs data...')
        organize_raw_data(file_path)

        print('Extract connection details...\n')
        extract_connection_details()


def extract_commands():
    # load to new table in database
    collection = create_collection_if_doesnt_exist(COMMANDS)

    with open('logs/logs_commands.log') as f:

        for i, line in enumerate(f, start=1):
            if i < LINE_NR_OLD:        # skip old lines
                continue

            if line.find('Type') == -1:    # is not a command
                continue
            else:
                parts = line.strip('\n').split(' | ')
                if parts[0] in BLACKLIST_DATES:    # skip test command
                    continue
                else:
                    command_type = parts[2].split()[1].split('.')[1]
                    command = None
                    match command_type:
                        case 'CREDENTIALS':
                            username = parts[3].split(maxsplit=1)[1].strip("'")
                            password = parts[4].split(maxsplit=1)[1].strip("'")

                            command = {
                                '_id': parts[0],
                                'type': command_type,
                                'data': {
                                    'username': username,
                                    'password': password
                                }
                            }
                        case 'SHELL':
                            body = parts[3].split(maxsplit=1)[1].strip("'")

                            command = {
                                '_id': parts[0],
                                'type': command_type,
                                'data': {
                                    'body': body
                                }
                            }
                        case 'EXEC':
                            body = parts[3].split(maxsplit=1)[1].strip("b'").strip("'")

                            command = {
                                '_id': parts[0],
                                'type': command_type,
                                'data': {
                                    'body': body
                                }
                            }

                    if command:
                        # insert to collection
                        collection.update_one(
                            {'_id': command['_id']},
                            {'$setOnInsert': command},
                            upsert=True
                        )


if __name__ == '__main__':
    # pipeline(['logs/logs_ssh_traffic_2025-06-20_16_22_13.log'])
    # pipeline(['logs/logs_ssh_traffic_2025-06-20_20_18_12.log'])

    # files = [f for f in os.listdir(LOCAL_DIR)
    #          if os.path.isfile(os.path.join(LOCAL_DIR, f)) and not f.endswith('.etag') and f.find('ssh') != -1]
    #
    # pipeline(files)

    # insert_ip_info()

    extract_commands()
