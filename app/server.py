# Main initialization file

from flask import Flask, Blueprint
from flask.ext.script import Manager, Server
from flask.ext.bootstrap import Bootstrap
from model import CheckNotifications, InitDb, DropDb
import chartkick

import authentication
import measurements

app = Flask(__name__)
app.jinja_env.line_statement_prefix = '%'

# Chartkick initialization
ck = Blueprint('ck_page', __name__, static_folder=chartkick.js(),
               static_url_path='/static')
app.register_blueprint(ck, url_prefix='/ck')
app.jinja_env.add_extension("chartkick.ext.charts")

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

manager.add_command("init_db", InitDb())
manager.add_command("drop_db", DropDb())


if __name__ == '__main__':
    manager.run()
