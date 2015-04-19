from flask import request, url_for, current_app, jsonify
from flask.ext.restful import reqparse
import inspect
from decorator import decorator
import json

@decorator
def getparser(self, *args, **kwargs):
    doc = parsedoc(function)
    if 'Parser' in doc:
        parser = reqparse.RequestParser()
        for arg, options in doc['Parser'].items():
            parser.add_argument(arg, **options)
        kwargs['parser'] = parser
        setattr(self, '%s_parser' % function.__name__, parser)
    return function(self, *args, **kwargs)

def parsedoc(function):
    doc = function.__doc__
    if doc:
        doc = filter(None, [i.strip() for i in doc.split('\n')])
        docdict = { }
        for line in doc:
            if line in [ 'Parser:', 'Arguments:' ]:
                key = line[:-1]
                continue
            else: 
                if line[:1] != ':':
                    key = 'Documentation'
            if key not in docdict: 
                if key == 'Documentation':
                    docdict[key] = []
                else:
                    docdict[key] = {}
            if line[:1] == ':':
                lines = str(line).split(' ', 2)
                if len(lines) > 2:
                    value = lines[2]
                else:
                    value = None

                argkey = lines[0][1:]
                name = lines[1][:-1]
                if argkey in [ 'arg', 'param' ]:
                    if argkey not in docdict[key]:
                        docdict[key][argkey] = {}
                    docdict[key][name] = {}
                elif argkey in docdict[key]:
                    docdict[key][argkey][name] = value
            else:
                docdict[key].append(line)
        return docdict
    else:
        return False

def ResourceOptions(cls):
    def options(self, **kwargs):
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
            if intersect or method == 'OPTIONS':
                doc = parsedoc(getattr(self, method.lower()))
                link = { 'method' : method, 'url' : url_for(self.endpoint, **kwargs ) }
                if doc and 'Arguments' in doc:
                    link.update(doc)
                else:
                    link['Arguments' ] = args
                links.append(link)

        return links
    cls.options = classmethod(options)
    cls.methods.append('OPTIONS')
    return cls

def Index():
    rules = {}
    for rule in current_app.url_map.iter_rules():
        print vars(rule)
        if rule.endpoint not in rules and rule.endpoint not in [ 'static' ]:
            rules[rule.endpoint] = {
                    'url ': url_for(rule.endpoint),
                    'methods' : list(rule.methods),
                    }
    return jsonify(rules)

