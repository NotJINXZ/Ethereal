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

# if __name__ == "__main__":
#     config = Config()
#     print(config.prefix)