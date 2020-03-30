import json


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        return json.JSONEncoder.default(self, obj)

# with open('result.json', 'w') as fp:
    #json.dump(tick_dic, fp, cls=JSONEncoder)
