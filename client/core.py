import requests
import config
from checks import Checks

def main():
    ccheck = Checks()
    put = ccheck.put()
    checks = ccheck.get()
    for check in checks:
        print check

