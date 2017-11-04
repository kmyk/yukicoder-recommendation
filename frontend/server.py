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

    favorite_problems = collections.defaultdict(list)
    inverse_favorite_problems = collections.defaultdict(list)
    cur.execute('SELECT user_id, problem_no FROM favorite_problems')
    for row in cur.fetchall():
        favorite_problems[row['user_id']] += [ row['problem_no'] ]
        inverse_favorite_problems[row['problem_no']] += [ row['user_id'] ]

    if user_id not in favorite_problems:
        raise AppError('このユーザーはまだどの問題もふぁぼっていません。なにも判断基準がないのでお手上げだよ')
    target_favorite_problems = set(favorite_problems[user_id])

    similar_users = collections.Counter()
    for problem_no in target_favorite_problems:
        for similar_user_id in inverse_favorite_problems[problem_no]:
            similar_users[problem_no] += 1

    recommended_problems = collections.Counter()
    for similar_user_id, user_score in similar_users.items():
        for problem_no in favorite_problems[similar_user_id]:
            if problem_no not in target_favorite_problems:
                recommended_problems[problem_no] += user_score
    recommended_problems = list(recommended_problems.items())
    recommended_problems.sort(key=lambda x: x[1], reverse=True)

    target_accepted_problems = set()
    cur.execute('SELECT DISTINCT problem_no FROM submissions WHERE user_id = %s AND is_ac = 1', ( user_id, ))
    for row in cur.fetchall():
        target_accepted_problems.add(row['problem_no'])

    problems = {}
    cur.execute('SELECT no, name FROM problems')
    for row in cur.fetchall():
        problems[row['no']] = { 'name': row['name'] }

    result = []
    for problem_no, score in recommended_problems:
        if problem_no not in target_accepted_problems:
            problem_name = problems[problem_no]['name']
            link = '''<a href="https://yukicoder.me/problems/no/%d">No %d. %s</a>''' % (problem_no, problem_no, flask.escape(problem_name))
            result += [ { 'link': link, 'score': str(score) } ]

    if not result:
        raise AppError('おすすめはいくつかあったけど全部解かれちゃってたよ。ごめんね')
    return result[: 32]

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
