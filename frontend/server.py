# Python Version: 3.x
# -*- coding: utf-8 -*-

import flask
import MySQLdb.cursors
import requests
import os
import collections

app = flask.Flask(__name__)

def get_custom_metadata(key, default=None):
    url = 'http://metadata.google.internal/computeMetadata/v1/project/attributes/%s' % key
    try:
        resp = requests.get(url, headers={ 'Metadata-Flavor': 'Google' })
        resp.raise_for_status()
        return resp.content.decode()
    except requests.exceptions.RequestException:
        return default

config = {
    'db_host':         get_custom_metadata('db-host',     os.environ.get('DB_HOST',     'localhost')),
    'db_port':     int(get_custom_metadata('db-port',     os.environ.get('DB_PORT',     '3306'))),
    'db_user':         get_custom_metadata('db-user',     os.environ.get('DB_USER',     'root')),
    'db_password':     get_custom_metadata('db-password', os.environ.get('DB_PASSWORD', '')),
}

class AppError(RuntimeError):
    pass

def get_db_handler():
    if not hasattr(flask.g, 'db'):
        flask.g.db = MySQLdb.connect(
            host    = config['db_host'],
            port    = config['db_port'],
            user    = config['db_user'],
            passwd  = config['db_password'],
            db      = 'yukireco',
            charset = 'utf8mb4',
            cursorclass = MySQLdb.cursors.DictCursor,
            autocommit = True,
        )
    cur = flask.g.db.cursor()
    cur.execute("SET SESSION sql_mode='TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY'")
    return cur

def get_user_id(user_name):
    cur = get_db_handler()
    cur.execute('SELECT id FROM users WHERE name = %s', ( user_name, ))
    user_id = cur.fetchone()
    if user_id is None:
        raise AppError('<i>%s</i>という名前のユーザーはいませんでした。typoしてませんか？' % flask.escape(user_name))
    return user_id['id']

def get_recommended_problems(user_id):
    cur = get_db_handler()
    cur.execute('SELECT problem_no FROM favorite_problems WHERE user_id = %s', ( user_id, ))
    favorite_problems = set([ row['problem_no'] for row in cur.fetchall() ])
    if not favorite_problems:
        raise AppError('このユーザーはまだどの問題もふぁぼっていません。なにも判断基準がないのでお手上げだよ')
    cur.execute('SELECT t1.user_id FROM favorite_problems t1 INNER JOIN favorite_problems t2 ON t1.problem_no = t2.problem_no WHERE t2.user_id = %s', ( user_id, ))
    user_dict = collections.Counter()
    for row in cur.fetchall():
        user_dict[row['user_id']] += 1
    problem_dict = collections.Counter()
    for similar_user_id, user_score in user_dict.items():
        cur.execute('SELECT problem_no FROM favorite_problems WHERE user_id = %s', ( similar_user_id, ))
        for row in cur.fetchall():
            problem_no = row['problem_no']
            if problem_no not in favorite_problems:
                problem_dict[problem_no] += 1
    problem_dict = list(problem_dict.items())
    problem_dict.sort(key=lambda x: x[1], reverse=True)
    result = []
    for problem_no, score in problem_dict[: 32]:
        cur.execute('SELECT 1 FROM submissions WHERE user_id = %s AND problem_no = %s AND is_ac = 1', ( user_id, problem_no, ))
        if cur.fetchone() is None:
            cur.execute('SELECT name FROM problems WHERE no = %s', ( problem_no, ))
            problem_name = cur.fetchone()['name']
            link = '''<a href="https://yukicoder.me/problems/no/%d">No %d. %s</a>''' % (problem_no, problem_no, flask.escape(problem_name))
            result += [ { 'link': link, 'score': str(score) } ]
    if not result:
        raise AppError('おすすめはいくつかあったけど全部解かれちゃってたよ。ごめんね')
    return result

@app.route('/')
def index():
    error_message = ''
    recommended_problems = []
    user_name = ''

    try:
        if flask.request.args.get('name'):
            user_name = flask.request.args['name']
            user_id = get_user_id(user_name)
            recommended_problems = get_recommended_problems(user_id=user_id)
    except AppError as e:
        error_message = e.args[0]

    return flask.render_template('index.html',
        error_message=error_message,
        recommended_problems=recommended_problems,
        user_name=user_name,
        )

if __name__ == '__main__':
    app.run()
