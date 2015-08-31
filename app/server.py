# Main initialization file
from flask import Flask, render_template
from flask.ext.script import Manager, Server
from flask.ext.bootstrap import Bootstrap
import authentication

app = Flask(__name__)

Bootstrap(app)

app.config["SECRET_KEY"] = "ITSASECRET"
app.register_blueprint(authentication.mod)


@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


@app.route("/protected/", methods=["GET"])
# @login_required
def protected():
    return "Hello, protected!", 200

manager = Manager(app)
manager.add_command("dev", Server(host="localhost", port=5000,
                                  use_debugger=True, use_reloader=True))

if __name__ == '__main__':
    manager.run()
