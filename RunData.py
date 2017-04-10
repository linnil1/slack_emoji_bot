import json
import os


class RunDataBase:
    def __init__(self):
        self.path = "data/rundata.json"
        self.data = {}
        if os.path.exists(self.path):
            self.data = json.loads(open(self.path).read())
        else:
            json.dump({}, open(self.path, "w"),
                      sort_keys=True, indent=4)

    def append(self, key, data):
        if not self.data.get(key):
            self.data[key] = []
        self.data[key].append(data)
        json.dump(self.data, open(self.path, "w"),
                   sort_keys=True, indent=4)

    def set(self, key, data):
        self.data[key] = data
        json.dump(self.data, open(self.path, "w"),
                   sort_keys=True, indent=4)

    def get(self, key):
        if self.data.get(key) is not None:
            return self.data.get(key)
        else:
            return []


class RunData():  # add prefix key
    def __init__(self, rundatabase, name):
        self._base = rundatabase
        self.name = name + "_"

    def append(self, key, data):
        return self._base.append(self.name + key, data)

    def set(self, key, data):
        return self._base.set(self.name + key, data)

    def get(self, key):
        return self._base.get(self.name + key)
