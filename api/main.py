from flask import Flask
from flask.ext import restful
from resources.results import Results
from resources.checks import Check
from resources.user import User

app = Flask(__name__)
api = restful.Api(app)

api.add_resource(Results, '/results/list', '/results')
api.add_resource(Check, '/checks')
api.add_resource(User, '/user', '/user/<name>')


if __name__ == '__main__':
    app.run(debug=True)
