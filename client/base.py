import requests, argparse, sys, json
from requests.auth import HTTPBasicAuth
from prettytable import PrettyTable
import config
import logging

class BaseObject(object):
    url = None
    path = None
    primary_key = None
    default_list_columns = None
    invalid_attrs = [ 'url', 'path', 'primary_key', 'default_list_columns', 'invalid_attrs', 'invalid_methods', 'fetch', 'new', 'update', 'list', 'delete' ]
    invalid_methods = [ 'get_methods', 'get_columns', 'get_params', 'valid_attr', 'get', 'put', 'post', 'get_primary', 'parser', 'cli_parser', 'list_parser', 'show_columns', 'print_table', 'usage' ]

    def __init__(self, url, path = None, data = None):
        self.url = url
        self.path = path
        primary = self.get_primary()
        if primary:
            self.primary_key = primary
        else:
            logging.warning('No primary key defined')

        if data:
            self._update(data)
        self._set_default_list_columns()

    def _update(self, data):
        for (name, value) in data.items():
            if hasattr(self, name):
                attr = getattr(self, name)
                attr.set_value(value)
                setattr(self, name, attr)

    def _set_default_list_columns(self):
        if not self.default_list_columns: 
            logging.debug('Setting default list columns to primary key')
            self.default_list_columns = [ self.get_primary() ]

    def usage(self):
        cmd = sys.argv.pop(0)
        resource = self.__class__.__name__
        print '%s %s action' % (cmd, resource)
        print 'Available actions:'
        for m in self.get_methods():
            print '\t%s' % m

    def list_parser(self):
        list_args = [
                { 'args' : '-c',    'options' : { 'required' : False, 'type' : str,  'dest' : 'columns',        'action' : 'append' } },
                { 'args' : '-C' ,   'options' : { 'required' : False, 'dest' : 'show_columns',   'action' : 'store_true' } },
                ]
        args = self.parser(list_args)
        if args['show_columns']:
            self.show_columns()
        else:
            if args['columns']:
                cols = args['columns']
            else:
                cols = self.default_list_columns

            columns = []
            for c in cols:
                if ',' in c: columns += c.split(',')
                else: columns.append(c)

            return columns
        return False


    def show_columns(self):
        print 'Available columns list'
        pt = PrettyTable(['Column', 'Description'])
        pt.align = 'l'
        for c, d in self.get_columns().items():
            pt.add_row([ c, d ])
        print pt

    def cli_parser(self, action = 'cli_create'):
        return self.parser(self.get_params(action))

    def parser(self, args):
        cmd = sys.argv.pop(0)
        parser = argparse.ArgumentParser(prog='%s %s' % (cmd, self.__class__.__name__))
        for arg in args:
            if 'options' in arg: parser.add_argument(arg['args'], **arg['options'])
            else: parser.add_argument(arg['args'])
        return vars(parser.parse_args([] if len(sys.argv) == 0 else sys.argv))

    def valid_attr(self, attr_name):
        if attr_name not in self.invalid_attrs and attr_name not in self.invalid_methods and attr_name[:2] != '__' and attr_name[:1] != '_': return True
        return False

    def get_primary(self):
        for c in dir(self):
            if self.valid_attr(c):
                attr = getattr(self, c)
                if attr.primary:
                    return c
        return False

    def get_params(self, action = 'cli_create'):
        args = []
        for c in dir(self):
            if self.valid_attr(c):
                attr = getattr(self, c)
                if hasattr(attr, action):
                    arg = {
                            'args' : '--%s' % c,
                            'options' : {
                                'required' : attr.cli_create_required,
                                'type' : attr.vartype,
                                'dest' : c,
                                'metavar' : attr.description,
                                'help' : attr.usage,
                                'default' : attr.default,
                                'action' : attr.action
                                }
                            }
                    if attr.choices:
                        arg['options']['choices'] = attr.choices
                    args.append(arg)
        return args

    def get_columns(self):
        columns = {}
        for c in dir(self):
            if self.valid_attr(c):
                attr = getattr(self, c)
                if attr.list_title:
                    columns[c] = attr.list_title
                else:
                    columns[c] = c.title().replace('_',' ')
        return columns

    def get_methods(self):
        methods = []
        for c in dir(self):
            if c not in self.invalid_methods and c[:2] != '__' and c[:1] != '_':
                if hasattr(getattr(self, c), '__call__'):
                    methods.append(c)
        return methods

    def print_table(self, data, columns):
        ocol = self.get_columns()
        tcol = []
        for c in columns:
            if c in ocol:
                tcol.append({ 'column' : c, 'description' : ocol[c]})

        pt = PrettyTable([c['description'] for c  in tcol])
        pt.align = 'l'
        for objdata in data:
            obj = object.__new__(self.__class__)
            obj.__init__(url = self.url, path = self.path, data = objdata)
            row = []
            for c in tcol:
                attr = getattr(obj, c['column'])
                if callable(attr):
                    row.append(attr())
                else:
                    row.append(attr.get_value())
            pt.add_row(row)
        print pt


    def get(self, id = None):
        if id:
            r = requests.get('%s/%s/%s' % (self.url, self.path, id), auth=(config.user, config.password))
        else:
            r = requests.get('%s/%s' % (self.url, self.path), auth=(config.user, config.password))
        return r

    def fetch(self):
        args = self.parser([{ 'args' : '-S' ,   'options' : { 'required' : True, 'dest' : 'id' } }])
        r = self.get(args['id'])

    def list(self, id = None):
        columns = self.list_parser()
        if columns:
            r = self.get(id)
            data = []
            for (key, obj) in r.json().items():
                data.append(obj)
            self.print_table(data, columns)


    def delete(self):
        args = self.parser([{ 'args' : '-S' ,   'options' : { 'required' : True, 'dest' : self.primary_key } }])
        print args
        self._update(args)
        r = requests.delete('%s/%s/%s' % (self.url, self.path, getattr(self, self.primary_key)), auth=(config.user, config.password))

    def post(self, args = None):
        if not args: args = self.cli_parser()
        r = requests.post('%s/%s' % (self.url, self.path), data = args, auth=(config.user, config.password))

    def put(self, args = None):
        if not args: args = self.cli_parser('cli_edit')
        self._update(args)
        r = requests.put('%s/%s/%s' % (self.url, self.path, getattr(self, self.primary_key)), data = args, auth=(config.user, config.password))

    def new(self):
        args = self.cli_parser()
        self._update(args)
        r = self.get(getattr(self, self.primary_key))
        if r.status_code == 404:
            self.post(args)
            logging.info('New user created')
        else:
            logging.info('User already exists')

    def update(self):
        args = self.cli_parser('cli_edit')
        self._update(args)
        r = self.get(getattr(self, self.primary_key))
        if r.status_code == 200:
            self.put(args)
        else:
            logging.critical('Object does not exists')

class BaseAttribute(object):
    primary = False
    value = None
    vartype = str
    cli_create_required = False
    cli_create = False
    cli_edit_required = False
    cli_edit = False
    cli_list = True
    list_title = None
    description = None
    usage = None
    choices = None
    default = None

    def __init__(self, primary = False, value = None, vartype = str, cli_create_required = False, cli_create = False, cli_edit_required = False, cli_edit = False, cli_list = True, list_title = None, description = None, usage = None, choices = [], default = None, action = None):
        self.primary = primary
        self.value = value
        self.vartype = vartype
        self.cli_create_required = cli_create_required
        if self.cli_create_required:
            self.cli_create = True
        else:
            self.cli_create = cli_create
        self.cli_edit_required = cli_edit_required
        if self.cli_edit_required:
            self.cli_edit = True
        else:
            self.cli_edit = cli_edit
        self.cli_list = cli_list
        self.list_title = list_title
        self.description = description
        self.usage = usage
        self.choices = choices
        self.default = default
        self.action = None

    def set_value(self, value):
        # TO-DO verify data type
        self.value = value

    def get_value(self): return self.value

    def __str__(self): return '%s' % self.value
    def __unicode__(self): return u'%s' % self.value
    def __repr__(self): return '<Attribute Value: %s>' % self.value

