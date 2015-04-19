from flask.ext.restful import reqparse, Resource, abort, fields, Api
from flask import request

import inspect

import common.persist
from common.auth import auth
from common.doc_helper import getparser, ResourceOptions

users = common.persist.load_file('users')
if not users:
    users = {}

post_parser = reqparse.RequestParser()
post_parser.add_argument('name', type=__builtins__['str'])
post_parser.add_argument('password', type=str)

@ResourceOptions
class User(Resource):
    method_decorators = [auth.login_required]
    @getparser
    def get(self, name = None, **kwargs):
        """
        Get an user or list of users
        and other line

        Arguments:
        :param name: Name of user
        :name type: str
        :name required: False
        """
        #args = kwargs['parser'].parse_args() if 'parser' in kwargs else False
        #args = self.get_parser.parse_args() if hasattr(self, 'get_parser') else False
        if name:
            if name in users:
                return users[name]
            else: abort(404, message='User not found')

        user = []
        for (k, obj) in users.items():
            user.append(obj)
        return user

    @getparser
    def post(self):
        """
        Create new user

        Parser:
        :arg name: Name of new user
        :name type: str
        :name required: True
        :arg password: Passworf of new user
        :password type: str
        :password required: True
        """
        args = post_parser.parse_args()
        users[args['name']] = args
        common.persist.to_file('users', users)
        return '', 201, { 'Location' : '/user/%s' % args['name'], 'header' : 'hedvalue' }

    @getparser
    def put(self, name):
        args = post_parser.parse_args()
        users[name] = args
        common.persist.to_file('users', users)

    @getparser
    def delete(self, name):
        if name in users:
            del users[name]
            common.persist.to_file('users', users)
