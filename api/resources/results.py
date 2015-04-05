from flask.ext import restful
from flask.ext.restful import reqparse

#from common import onapp
#from common.auth import auth

results = [] 

parser = reqparse.RequestParser()
parser.add_argument('host', type=str)
parser.add_argument('check', type=str)
parser.add_argument('result', type=str)
parser.add_argument('date', type=str)
parser.add_argument('md5', type=str)

class Results(restful.Resource):
#    method_decorators = [auth.login_required]
    def get(self, id = None):
        if id:
            return results[id]
        return results

    def post(self):
        args = parser.parse_args()
        old_len = len(results)
        results.append( args )
        if len(results) > old_len:
            return 'OK'
        else: return 'KO'

