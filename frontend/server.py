# Python Version: 3.x
# -*- coding: utf-8 -*-

import flask
app = flask.Flask(__name__)

@app.route('/')
def index():
    favorite_problems = []
    if 'name' in flask.request.args:
        favorite_problems += [ { 'foo': 'foo', 'bar': 'bar' } ]
        favorite_problems += [ { 'foo': 'aaa', 'bar': 'xxx' } ]
        favorite_problems += [ { 'foo': 'bbb', 'bar': 'yyy' } ]
        favorite_problems += [ { 'foo': 'ccc', 'bar': 'zzz' } ]

    return flask.render_template('index.html',
        favorite_problems=favorite_problems,
        )

if __name__ == '__main__':
    app.run()
