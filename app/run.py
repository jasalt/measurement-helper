# Script for running in Heroku
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from server import app, deploy
import logging
from logging import StreamHandler
import os

deploy()

file_handler = StreamHandler()
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(os.environ['PORT'])
IOLoop.instance().start()
