import pymongo
from config import Config
config = Config()


client = pymongo.MongoClient(config.mongo_uri)
database = client['ethereal']
servers_collection = database['servers']

def init_server(server_id: int):
    if not servers_collection.find_one({"server_id": server_id}):
        new_server = {
            "server_id": server_id,
            "values": {
                "temp_bans": [] 
            }
        }
        servers_collection.insert_one(new_server)

def update_value(server_id: int, value_name: str, value: str | int | bool):
    servers_collection.update_one(
        {"server_id": server_id},
        {"$set": {f"values.{value_name}": value}},
        upsert=True
    )

def get_value(server_id: int, value_name: str):
    server = servers_collection.find_one({"server_id": server_id})
    if server:
        return server.get("values", {}).get(value_name)
    
    return None

def delete_server(server_id: int):
    servers_collection.delete_one({"server_id": server_id})
    
def update_temp_bans(server_id: int, temp_bans: list):
    servers_collection.update_one(
        {"server_id": server_id},
        {"$set": {"values.temp_bans": temp_bans}},
    )

def get_temp_bans(server_id: int):
    server = servers_collection.find_one({"server_id": server_id})
    if server:
        return server.get("values", {}).get("temp_bans", [])
    
    return []