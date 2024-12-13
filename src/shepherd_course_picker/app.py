import json

from flask import Flask, render_template
import data_maker


app = Flask(__name__)

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__json__()

def toJSON(object):
    return json.dumps(object, cls=CustomEncoder)


@app.route('/')
def home():
    return render_template('programs')

@app.route('/picker')
def home():
    return render_template('picker.html')

@app.route('/api/programs')
def picker():
    programs =data_maker.get_program_list()

    a = toJSON(programs)

    return a

@app.route('/api/programs/<int:program_id>', methods=['GET'])
def picker2(program_id: int):
    p = data_maker.get_program(
        program_id
    )

    return toJSON(p)


if __name__ == '__main__':
    app.run()