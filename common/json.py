from json import JSONEncoder
from datetime import datetime
from django.db.models import QuerySet

class QuerySetEncoder(JSONEncoder):
    def default(self,o):
        if isinstance(o,QuerySet):
            return list(o)
        else:
            return super().default(o)

class DateEncoder(JSONEncoder):
    def default(self,o):
        if isinstance(o,datetime):
            return o.isoformat()
        else:
            return super().default(o)

class ModelEncoder(DateEncoder, QuerySetEncoder, JSONEncoder):
    encoders = {}
    # print("1")
    def default(self, o):
        # print("2")
        # print(dir(o))
        # print(type(o))
        # print(self.model)
        if isinstance(o, self.model):
            # print("3")
            d = {}
            if hasattr(o, "get_api_url"):
                d["href"] = o.get_api_url()
                # print("href?")
            for property in self.properties:
                value = getattr(o, property)
                # print(self.encoders)
                if property in self.encoders:
                    # print("4")
                    encoder = self.encoders[property]
                    value = encoder.default(value)
                d[property] = value
            d.update(self.get_extra_data(o))
            # print("Reached return")
            # print(d)
            return d
        else:
            return super().default(o)

    def get_extra_data(self, o):
        return {}
