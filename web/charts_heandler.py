from django.db import connections
import json


class ChartsHandler(object):

    def plotting(self, json_data=None, type="line"):
        data = {}
        if json_data is None:
            return False
        else:
            res = []
            data.update({
                    "columns": [list(it) for it in json.loads(json_data)],
                "type": type
            })
            # print(data)
        return data