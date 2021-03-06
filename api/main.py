from flask import Flask
from flask.ext import restful
from flask.ext.cors import CORS
from resources.results import Results
from resources.checks import Check
from resources.user import User
import json
from common.doc_helper import Index

app = Flask(__name__)
cors = CORS(app)
api = restful.Api(app)

api.add_resource(Results, '/results/list', '/results')
api.add_resource(Check, '/checks')
api.add_resource(User, '/user', '/user/<string:name>', endpoint='user')

@app.route("/")
def index():
    return Index()


if __name__ == '__main__':
    app.run(debug=True)
