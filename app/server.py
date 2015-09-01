# Main initialization file

from flask import Flask, render_template
from flask.ext.script import Manager, Server
from flask.ext.bootstrap import Bootstrap

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

if __name__ == '__main__':
    manager.run()
