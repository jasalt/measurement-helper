# Main initialization file

from flask import Flask
from flask.ext.script import Manager, Server
from flask.ext.bootstrap import Bootstrap
from model import CheckNotifications, InitNotificationIntervals, InitFromCsv, \
    DropDb

import authentication
import measurements

app = Flask(__name__)
app.jinja_env.line_statement_prefix = '%'

Bootstrap(app)

app.config["SECRET_KEY"] = "ITSASECRET"

app.register_blueprint(authentication.mod)
authentication.login_manager.init_app(app)

app.register_blueprint(measurements.mod)

manager = Manager(app)
manager.add_command("dev", Server(host="localhost", port=5000,
                                  use_debugger=True, use_reloader=True))
manager.add_command("run", Server(host="0.0.0.0", port=5001,
                                  use_debugger=False, use_reloader=True))

manager.add_command("check_notifications", CheckNotifications())

manager.add_command("drop_db", DropDb())
manager.add_command("init", InitNotificationIntervals())
manager.add_command("load_csv", InitFromCsv())


@manager.command
def deploy():
    '''Initialize database.'''
    InitNotificationIntervals()
    InitFromCsv()

if __name__ == '__main__':
    manager.run()
