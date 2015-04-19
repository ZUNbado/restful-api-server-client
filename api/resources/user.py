from flask.ext.restful import reqparse, Resource, abort, fields, Api
from flask import current_app, request

import inspect

import common.persist
from common.auth import auth

users = common.persist.load_file('users')
if not users:
    users = {}

post_parser = reqparse.RequestParser()
post_parser.add_argument('name', type=str)
post_parser.add_argument('password', type=str)

class User(Resource):
    method_decorators = [auth.login_required]
    def get(self, name = None):
        if name:
            if name in users:
                return users[name]
            else: abort(404, message='User not found')

        user = []
        for (k, obj) in users.items():
            user.append(obj)
        print user
        return user

    def post(self):
        args = post_parser.parse_args()
        users[args['name']] = args
        common.persist.to_file('users', users)
        return '', 201, { 'Location' : '/user/%s' % args['name'], 'header' : 'hedvalue' }

    def put(self, name):
        args = post_parser.parse_args()
        users[name] = args
        common.persist.to_file('users', users)

#    def delete(self, name):
#        if name in users:
#            del users[name]
#            common.persist.to_file('users', users)

    def options(self, name = None):
        """
        Get options
        :param name: A tring
        :reurns: Json
        """
        rule = request.url_rule.rule
        rule_args = request.view_args if len(request.view_args) > 0 else None

        intersect = True
        links = []
        for method in self.methods:
            args = []
            for arg in inspect.getargspec(getattr(self, method.lower()))[0]:
                if arg not in [ 'self' ]:
                    args.append(arg)
                if rule_args:
                    intersect = True
                    for ra in rule_args:
                        if ra not in args:
                            intersect = False
            if rule_args:
                for key, value in rule_args.items():
                    rule = rule.replace('<%s>' % key, value)

            if intersect:
                doc = getattr(self, method.lower()).__doc__
                if doc:
                    doc = filter(None, [i[8:] for i in doc.split('\n')])

                links.append({ 'method' : method, 'args' :  args, 'rule' : rule, 'doc': doc})

        print vars(post_parser.args[0])

        return links
