from flask.ext import restful
from flask.ext.restful import reqparse
import common.persist

#from common import onapp
#from common.auth import auth

check = common.persist.load_file('checks') 

put_parser = reqparse.RequestParser()
put_parser.add_argument('host', type=str)
put_parser.add_argument('address', type=str, action='append')
put_parser.add_argument('check', type=str)
put_parser.add_argument('interval', type=int)
put_parser.add_argument('retries', type=str)

get_parser = reqparse.RequestParser()
get_parser.add_argument('save', type=bool, default=False)

class Check(restful.Resource):
#    method_decorators = [auth.login_required]
    def get(self):
        args = get_parser.parse_args()
        print args
        if args['save']:
            common.persist.to_file('checks', check)
        return check

    def put(self):
        args = put_parser.parse_args()
        old_len = len(check)
        check.append( args )
        if len(check) > old_len:
            return 'OK'
        else: return 'KO'

