from base import BaseObject, BaseAttribute

class Checks(BaseObject):
    id = BaseAttribute(primary = True)
    host = BaseAttribute(cli_create_required = True, cli_edit_required = True)
    check = BaseAttribute(cli_create_required = True, cli_edit_required = True)
    interval = BaseAttribute(cli_create_required = True, cli_edit_required = True)
    retries = BaseAttribute(cli_create_required = True, cli_edit_required = True)
    address = BaseAttribute(cli_create_required = True, cli_edit_required = True, action = 'append')


    def __init__(self, *args, **kwargs):
        super(Checks, self).__init__(*args, **kwargs)
        self.path = 'checks'
