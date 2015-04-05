import json
import os
import config

def getfile(name):
    return os.path.join(config.BASE_PATH, name)

def to_file(name, data):
    with open(getfile(name), 'w') as w:
        json.dump(data, w)
    w.close()
    return True

def load_file(name):
    if not os.path.isfile(getfile(name)):
        return False
    with open(getfile(name), 'r') as r:
        data = json.load(r)
    r.close()
    if data:
        return data
    else:
        return False

