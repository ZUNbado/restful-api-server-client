from base import BaseObject, BaseAttribute

class User(BaseObject):
    name = BaseAttribute(primary = True, cli_create_required = True, cli_edit_required = True)
    password = BaseAttribute(cli_create_required = True, cli_edit_required = True)

    default_list_columns = [ 'name', 'password' ]

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.path = 'user'


