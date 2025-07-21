from secrets.constants import db, ATTACKER_DATA, COMMANDS


# used ✅
def no_total_connections() -> int:
    collection = db[ATTACKER_DATA]
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_connections": {"$sum": {"$size": "$connections"}}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

    if result:
        return result[0]["total_connections"]
    return 0


# used ✅
def no_good_connections() -> int:   # valid handshake
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {"$match": {"connections.valid_handshake": True}},
        {"$count": "total"}
    ]

    result = list(collection.aggregate(pipeline))

    if result:
        return result[0]["total"]
    return 0


# used ✅
def max_conn_on_ip():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$project": {"count": {"$size": "$connections"}}},
        {"$group": {"_id": None, "max_conn": {"$max": "$count"}}}
    ]

    result = list(collection.aggregate(pipeline))
    return result[0]["max_conn"] if result else 0


# used ✅
def avg_conn_on_ip():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$project": {"count": {"$size": "$connections"}}},
        {"$group": {"_id": None, "avg_conn": {"$avg": "$count"}}}
    ]

    result = list(collection.aggregate(pipeline))
    return result[0]["avg_conn"] if result else 0


# used ✅
def ip_connection_count_distribution():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {
            "$project": {
                "ip": "$_id",
                "conn_count": {"$size": "$connections"}
            }
        },
        {
            "$match": {
                "conn_count": {"$gt": 0}  # exclude 0 connections
            }
        },
        {
            "$bucket": {
                "groupBy": "$conn_count",
                "boundaries": [1, 2, 3, 5, 7, 10, 15, 20, 30, 40],
                "default": 50,
                "output": {
                    "ip_count": {"$sum": 1}
                }
            }
        }
    ]

    results = collection.aggregate(pipeline)
    # return [f'IPs with {doc["_id"]}+ connections: {doc["ip_count"]}' for doc in results]      # pretty result
    return [doc for doc in results]


# used ✅
def avg_good_connection_duration() -> int:  # return time duration
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {"$match": {"connections.valid_handshake": True}},
        {
            "$addFields": {
                "start": {
                    "$dateFromString": {
                        "dateString": {"$substrBytes": ["$connections.start_time", 0, 23]},
                        "format": "%Y-%m-%d %H:%M:%S.%L"
                    }
                },
                "end": {
                    "$dateFromString": {
                        "dateString": {"$substrBytes": ["$connections.end_time", 0, 23]},
                        "format": "%Y-%m-%d %H:%M:%S.%L"
                    }
                }
            }
        },
        {
            "$project": {
                "duration_ms": {
                    "$divide": [
                        {"$subtract": ["$end", "$start"]},
                        1
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "avg_duration": {"$avg": "$duration_ms"}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return int(result[0]["avg_duration"]) if result else 0


# used ✅
def max_good_connection_duration() -> int:      # return time duration
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {"$match": {"connections.valid_handshake": True}},
        {
            "$addFields": {
                "start": {
                    "$dateFromString": {
                        "dateString": {"$substrBytes": ["$connections.start_time", 0, 23]},
                        "format": "%Y-%m-%d %H:%M:%S.%L"
                    }
                },
                "end": {
                    "$dateFromString": {
                        "dateString": {"$substrBytes": ["$connections.end_time", 0, 23]},
                        "format": "%Y-%m-%d %H:%M:%S.%L"
                    }
                }
            }
        },
        {
            "$project": {
                "duration_ms": {
                    "$divide": [
                        {"$subtract": ["$end", "$start"]},
                        1
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "max_duration": {"$max": "$duration_ms"}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return int(result[0]["max_duration"]) if result else 0


# used ✅
def no_connections_on_country() -> list[dict]:      # return country name and no connections
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {
            "$group": {
                "_id": "$geo.location.country",
                "total_connections": {"$sum": 1}
            }
        },
        {"$sort": {"total_connections": -1}}
    ]

    result = list(collection.aggregate(pipeline))

    if result:
        return result
    return [{}]


# --------- On hours aggregation ---------
# used ✅
def no_connections_on_hours():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {"$match": {"connections.valid_handshake": True}},
        {
            "$addFields": {
                "clean_time": {
                    "$dateFromString": {
                        "dateString": {
                            "$substrBytes": ["$connections.start_time", 0, 23]
                        },
                        "format": "%Y-%m-%d %H:%M:%S.%L"
                    }
                }
            }
        },
        {
            "$addFields": {
                "hour": {"$hour": "$clean_time"},
                "date": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$clean_time"}
                }
            }
        },
        {
            "$group": {
                "_id": {"hour": "$hour", "date": "$date"},
                "connections": {"$sum": 1}
            }
        },
        {
            "$group": {
                "_id": "$_id.hour",
                "avg_connections": {"$avg": "$connections"}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    result = list(collection.aggregate(pipeline))

    hourly_averages = {hour: 0.0 for hour in range(24)}
    for doc in result:
        hourly_averages[doc["_id"]] = round(doc["avg_connections"])

    return hourly_averages


# used ✅
def no_total_connections_on_hours():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {
            "$addFields": {
                "clean_time": {
                    "$dateFromString": {
                        "dateString": {
                            "$substrBytes": ["$connections.start_time", 0, 23]
                        },
                        "format": "%Y-%m-%d %H:%M:%S.%L"
                    }
                }
            }
        },
        {
            "$addFields": {
                "hour": {"$hour": "$clean_time"},
                "date": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$clean_time"}
                }
            }
        },
        {
            "$group": {
                "_id": {"hour": "$hour", "date": "$date"},
                "connections": {"$sum": 1}
            }
        },
        {
            "$group": {
                "_id": "$_id.hour",
                "avg_connections": {"$avg": "$connections"}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]

    result = list(collection.aggregate(pipeline))

    hourly_averages = {hour: 0.0 for hour in range(24)}
    for doc in result:
        hourly_averages[doc["_id"]] = round(doc["avg_connections"])

    return hourly_averages


# used ✅
def no_ips_on_hours():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {
            "$addFields": {
                "clean_time": {
                    "$dateFromString": {
                        "dateString": {
                            "$substrBytes": ["$connections.start_time", 0, 23]
                        },
                        "format": "%Y-%m-%d %H:%M:%S.%L"
                    }
                }
            }
        },
        {
            "$addFields": {
                "hour": {"$hour": "$clean_time"},
                "date": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$clean_time"}
                }
            }
        },
        {
            "$group": {
                "_id": {"hour": "$hour", "date": "$date"},
                "unique_ips": {"$addToSet": "$_id"}
            }
        },
        {
            "$project": {
                "hour": "$_id.hour",
                "ip_count": {"$size": "$unique_ips"}
            }
        },
        {
            "$group": {
                "_id": "$hour",
                "avg_ip_count": {"$avg": "$ip_count"}
            }
        },
        {"$sort": {"_id": 1}}
    ]

    result = list(collection.aggregate(pipeline))

    hourly_averages = {hour: 0.0 for hour in range(24)}
    for doc in result:
        hourly_averages[doc["_id"]] = round(doc["avg_ip_count"])

    return hourly_averages


# used ✅
def avg_bytes_on_hours():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {
            "$addFields": {
                "clean_time": {
                    "$dateFromString": {
                        "dateString": {
                            "$substrBytes": ["$connections.start_time", 0, 23]
                        },
                        "format": "%Y-%m-%d %H:%M:%S.%L"
                    }
                }
            }
        },
        {
            "$addFields": {
                "hour": {"$hour": "$clean_time"}
            }
        },
        {
            "$group": {
                "_id": "$hour",
                "total_bytes": {"$sum": "$connections.bytes_transferred"},
                "count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "hour": "$_id",
                "avg_bytes": {"$cond": [{"$eq": ["$count", 0]}, 0, {"$divide": ["$total_bytes", "$count"]}]}
            }
        },
        {"$sort": {"hour": 1}}
    ]

    result = collection.aggregate(pipeline)

    return {doc["hour"]: round(doc["avg_bytes"], 2) for doc in result}


# ----------------------------------------

def no_connections_on_days():       # returns no connections on every day
    collection = db[ATTACKER_DATA]


def no_ips_on_days():       # returns no connections on every day
    collection = db[ATTACKER_DATA]


# used ✅
def no_ips() -> int:       # return no different ips
    collection = db[ATTACKER_DATA]

    return collection.count_documents({})


# used ✅
def no_ips_on_country():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {
            "$group": {
                "_id": "$geo.location.country",
                "ip_count": {"$sum": 1}
            }
        },
        {"$sort": {"ip_count": -1}}
    ]

    results = collection.aggregate(pipeline)
    return {doc["_id"]: doc["ip_count"] for doc in results}


# used ✅
def max_no_ports_on_ip() -> int:    # max nr ports on an ip address
    collection = db[ATTACKER_DATA]

    pipeline = [
        {
            "$project": {
                "num_ports": {"$size": "$ports"}
            }
        },
        {
            "$group": {
                "_id": None,
                "max_ports": {"$max": "$num_ports"}
            }
        }
    ]

    result = collection.aggregate(pipeline)
    return next(result, {}).get("max_ports", 0)


# used ✅
def avg_no_ports_on_ip() -> float:     # avg nr ports on an ip address
    collection = db[ATTACKER_DATA]

    pipeline = [
        {
            "$project": {
                "num_ports": {"$size": "$ports"}
            }
        },
        {
            "$group": {
                "_id": None,
                "avg_ports": {"$avg": "$num_ports"}
            }
        }
    ]

    result = collection.aggregate(pipeline)
    return round(next(result, {}).get("avg_ports", 0.0), 2)


# used ✅
def ip_port_count_distribution():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {
            "$project": {
                "ip": "$_id",
                "port_count": {"$size": "$ports"}
            }
        },
        {
            "$bucket": {
                "groupBy": "$port_count",
                "boundaries": [1, 2, 3, 5, 7, 10, 15, 20, float("inf")],
                "default": "20+",
                "output": {
                    "ip_count": {"$sum": 1}
                }
            }
        }
    ]

    results = collection.aggregate(pipeline)
    # return [f'IPs with {doc["_id"]}+ ports: {doc["ip_count"]}' for doc in results]    # pretty data
    return [doc for doc in results]


# TODO: use it
def top_ips_by_connection_count() -> list[str]:
    collection = db[ATTACKER_DATA]

    pipeline = [
        {
            "$project": {
                "_id": 1,
                "connection_count": {"$size": "$connections"},
                "country": "$geo.location.country"
            }
        },
        {"$sort": {"connection_count": -1}},
        # {"$limit": n}
    ]

    result = collection.aggregate(pipeline)

    return [doc for doc in result]


# used ✅
def connection_duration_distribution():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {"$match": {"connections.valid_handshake": True}},

        {
            "$addFields": {
                "start": {
                    "$dateFromString": {
                        "dateString": {"$substrBytes": ["$connections.start_time", 0, 23]},
                        "format": "%Y-%m-%d %H:%M:%S.%L"
                    }
                },
                "end": {
                    "$dateFromString": {
                        "dateString": {"$substrBytes": ["$connections.end_time", 0, 23]},
                        "format": "%Y-%m-%d %H:%M:%S.%L"
                    }
                }
            }
        },
        {
            "$addFields": {
                "duration_ms": {
                    "$divide": [
                        {"$subtract": ["$end", "$start"]},
                        1
                    ]
                }
            }
        },
        {
            "$bucket": {
                "groupBy": "$duration_ms",
                "boundaries": [0, 500, 1000, 2000, 5000, 10000, 15000, float('inf')],
                "default": "15k+",
                "output": {
                    "conn_count": {"$sum": 1}
                }
            }
        }
    ]

    results = collection.aggregate(pipeline)
    return [doc for doc in results]


# TODO: use it
def no_connections_by_asn():
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {
            "$group": {
                "_id": "$geo.network.asn",
                "connection_count": {"$sum": 1}
            }
        },
        {"$sort": {"connection_count": -1}}
    ]

    results = collection.aggregate(pipeline)
    return [{"asn": doc["_id"], "connections": doc["connection_count"]} for doc in results]


# TODO: use it
def most_common_orgs(n: int = 10):
    collection = db[ATTACKER_DATA]

    pipeline = [
        {
            "$group": {
                "_id": "$geo.network.org",
                "ip_count": {"$sum": 1}
            }
        },
        {"$sort": {"ip_count": -1}},
        # {"$limit": n}
    ]

    results = collection.aggregate(pipeline)
    return [{"org": doc["_id"], "ip_count": doc["ip_count"]} for doc in results]


# used ✅
def max_bytes_per_connection():     # include only valid handshakes
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {"$match": {"connections.valid_handshake": True}},
        {
            "$group": {
                "_id": None,
                "max_bytes": {"$max": "$connections.bytes_transferred"}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return result[0]["max_bytes"] if result else 0


# used ✅
def average_bytes_per_connection():     # include only valid handshakes
    collection = db[ATTACKER_DATA]

    pipeline = [
        {"$unwind": "$connections"},
        {"$match": {"connections.valid_handshake": True}},
        {
            "$group": {
                "_id": None,
                "avg_bytes": {"$avg": "$connections.bytes_transferred"}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))
    return result[0]["avg_bytes"] if result else 0.0


# used ✅
def ip_total_bytes_distribution():
    collection = db[ATTACKER_DATA]

    pipeline = [
        # Flatten connections
        {"$unwind": "$connections"},
        {"$match": {"connections.valid_handshake": True}},
        {
            "$bucket": {
                "groupBy": "$connections.bytes_transferred",
                "boundaries": [0, 100, 500, 1000, 2000, 3000, 5000, 10000, float("inf")],
                "default": "100k+",
                "output": {
                    "conn_count": {"$sum": 1}
                }
            }
        }
    ]

    results = collection.aggregate(pipeline)
    # return [f'IPs with {doc["_id"]}+ total bytes: {doc["ip_count"]}' for doc in results]      # pretty result
    return [doc for doc in results]


# ----------------- Commands Statistics ------------------
# used ✅
def no_each_comm_type():    # returns dict with each frequency
    collection = db[COMMANDS]

    pipeline = [
        {"$group": {"_id": "$type", "count": {"$sum": 1}}}
    ]

    result = collection.aggregate(pipeline)

    frequencies = {doc["_id"]: doc["count"] for doc in result}

    return frequencies


# used ✅
def n_most_popular_usernames(n: int = 10):   # returns dict with username and its frequency
    collection = db[COMMANDS]

    pipeline = [
        {"$match": {"type": "CREDENTIALS"}},
        {"$group": {"_id": "$data.username", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        # {"$limit": n}
    ]

    result = collection.aggregate(pipeline)

    return {doc["_id"]: doc["count"] for doc in result}


# used ✅
def n_most_popular_passwords(n: int = 10):   # returns dict with password and its frequency
    collection = db[COMMANDS]

    pipeline = [
        {"$match": {"type": "CREDENTIALS"}},
        {"$group": {"_id": "$data.password", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": n}
    ]

    result = collection.aggregate(pipeline)

    return {doc["_id"]: doc["count"] for doc in result}


# used ✅
def n_most_popular_commands(n: int = 10):    # returns dict with command and its frequency
    collection = db[COMMANDS]

    pipeline = [
        {"$match": {"type": {"$in": ["SHELL", "EXEC"]}}},
        {"$group": {"_id": "$data.body", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        # {"$limit": n}
    ]

    result = collection.aggregate(pipeline)

    return {doc["_id"]: doc["count"] for doc in result}


if __name__ == '__main__':
    # print(f'Top N ips by connection count: {top_ips_by_connection_count()}')

    # print(f'No conn by asn: {no_connections_by_asn()}')
    # print(f'Most common orgs: {most_common_orgs()}')

    # print(f'No each comm type: {no_each_comm_type()}')
    # print(f'Most popular usernames: {n_most_popular_usernames()}')
    # print(f'Most popular passwords: {n_most_popular_passwords()}')
    print(f'Most popular commands: {n_most_popular_commands()}')

    # print(f'No ips distribution on country: {no_ips_on_country()}')
    # print(f'No connections distribution on country: {no_connections_on_country()}')
    pass
