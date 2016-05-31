from django.db import connections
import json


class ChartsHandler(object):
    def plotting(self, json_data=None, type_chart=["line"]):
        data = {}
        res = []

        if json_data is None:
            return False
        else:
            json_data = json.loads(json_data)
            for i in json_data:
                for t in type_chart:
                    data = {
                        "columns": i,
                        "type": t
                    }
                    res.append([data])
                    del type_chart[0]
                    break
        return res