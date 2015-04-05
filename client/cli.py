import resources
import pkgutil
import config
import sys


def load_resource(resource):
    load = 'resources.%s.%s' % (resource.lower(), resource.title())
    module = 'resources.%s' % (resource.lower())
    klass = resource.title()
    mod = __import__(module, fromlist=module)
    return getattr(mod, klass)


def main():
    #cmd = sys.argv.pop(0)
    resource = None
    method = None
    if len(sys.argv) > 1: resource = sys.argv.pop(1)
    if len(sys.argv) > 1: method = sys.argv.pop(1)

    for (importer, name, ispkg) in pkgutil.walk_packages(path=resources.__path__, prefix=resources.__name__+'.', onerror=lambda x: None):
        __import__(name)

    if resource:
        obj = load_resource(resource)
        obj = obj(config.BASE_URL)
        if method:
            if hasattr(obj, method):
                getattr(obj, method)()
            else:
                print 'Method %s is not available in resource %s' % (method, resource)
        else:
            obj.usage()
    else:
        available_resources = []
        for rsc in dir(resources):
            if rsc not in ['__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__']:
                for obj in dir(getattr(resources, rsc)):
                    if obj not in ['__builtins__', '__doc__', '__file__', '__name__', '__package__', 'BaseAttribute', 'BaseObject']:
                        available_resources.append(obj)
        print available_resources



if __name__ == '__main__':
    main()
