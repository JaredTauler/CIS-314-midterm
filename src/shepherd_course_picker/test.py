import data_maker
# print(data_maker.get_program_list())

# a = data_maker.get_program_list()[0]
import json
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__json__()

def toJSON(object):
    return json.dumps(object, cls=CustomEncoder)


# a.render()

a = data_maker.get_program(2576)

print(a)
# a.render()
# print(data_maker.get_program_list())
# a.render()
# html = a.make_html()
#
# nodes = a.find_cores(html)

# print('hi')
# print(a.nodes)