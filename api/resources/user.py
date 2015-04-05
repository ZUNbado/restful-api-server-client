from flask.ext.restful import reqparse, Resource, abort
import common.persist

users = common.persist.load_file('users')
print users
if not users:
    users = {}

post_parser = reqparse.RequestParser()
post_parser.add_argument('name', type=str)
post_parser.add_argument('password', type=str)

class User(Resource):
    def get(self, name = None):
        if name:
            if name in users:
                return users[name]
            else: abort(404, message='User not found')
        return users

    def post(self, **kargs):
        args = post_parser.parse_args()
        users[args['name']] = args
        common.persist.to_file('users', users)

    def put(self, name):
        args = post_parser.parse_args()
        print args
        users[name] = args
        common.persist.to_file('users', users)

