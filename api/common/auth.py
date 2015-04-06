from flask.ext.httpauth import HTTPBasicAuth
from common import persist 

auth = HTTPBasicAuth()

users = persist.load_file('users')

@auth.verify_password
def verify_password(user, password):
    if user in users:
        if password == users[user]['password']:
            return True
    return False
