from django.db import connections
import json


class Charts(object):

    def plotting(self, json_data=None):
        data = {}
        if json_data is None:
            return False
        else:
            res = []
            data.update({
                    "columns": [list(it) for it in json.loads(json_data)],
                "type": "line"
            })
            # print(data)
        return data