# Python Version: 3.x
# -*- coding: utf-8 -*-

import flask
import sqlite3

app = flask.Flask(__name__)

def get_db_handler():
    if not hasattr(flask.g, 'db'):
        flask.g.db = sqlite3.connect('sqlite.db')
    return flask.g.db

def get_user_id(name):
    cur = get_db_handler().cursor()
    cur.execute('SELECT id FROM users WHERE name = ?', ( name, ))
    user_id = cur.fetchone()
    if user_id is None:
        return None
    return user_id[0]

def get_favorite_problems(user_id):
    cur = get_db_handler().cursor()
    cur.execute('SELECT problem_no FROM favorite_problems WHERE user_id = ?', ( user_id, ))
    result = []
    for problem_no, in cur.fetchall():
        result += [ { 'foo': str(user_id), 'bar': str(problem_no) } ]
    return result

@app.route('/')
def index():
    user_name = ''
    unknown_user = False
    favorite_problems = []

    if 'name' in flask.request.args:
        user_name = flask.request.args['name']
        user_id = get_user_id(user_name)
        if user_id is None:
            unknown_user = True
        else:
            favorite_problems = get_favorite_problems(user_id=user_id)

    return flask.render_template('index.html',
        user_name=user_name,
        unknown_user=unknown_user,
        favorite_problems=favorite_problems,
        )

if __name__ == '__main__':
    app.run()
