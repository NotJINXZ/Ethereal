import dotenv
import os
import json
import re

dotenv.load_dotenv()

with open("config.jsonc", "r") as r:
    content = re.sub(r'//.*', '', r.read())
    conf = json.loads(content)

class Config:
    def __init__(self):
        self.token = os.getenv("TOKEN")
        self.prefix = conf["bot"]["prefix"]
        self.mongo_uri = os.getenv("MONGO_URI")
        self.osu = os.getenv("OSU_APIKEY")
        self.whitelist_access = conf["bot"]["whitelist"]
        self.whitelist_enabled = True
        self.whitelist_dashboard = True # Enable dashboard so users can whitelist their server ?
        self.whitelist_dashboard_link = "http://localhost:1122"

# if __name__ == "__main__":
#     config = Config()
#     print(config.prefix)