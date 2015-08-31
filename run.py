from app import app
app.config["SECRET_KEY"] = "ITSASECRET"
app.run(host='localhost', port=5000, debug=True)
