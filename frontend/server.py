# Python Version: 3.x
# -*- coding: utf-8 -*-

import flask
app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html')

if __name__ == '__main__':
    app.run()
