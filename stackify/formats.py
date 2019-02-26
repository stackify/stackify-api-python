import json


def nonempty(d):
    return {k: v for k, v in d.items() if v is not None}


class JSONObject(object):
    def toJSON(self):
        return json.dumps(self, default=lambda x: nonempty(x.__dict__))
