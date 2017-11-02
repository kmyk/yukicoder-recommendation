# Python Version: 3.x
# -*- coding: utf-8 -*-

import flask
import sqlite3
import collections

app = flask.Flask(__name__)

class AppError(RuntimeError):
    pass

def get_db_handler():
    if not hasattr(flask.g, 'db'):
        flask.g.db = sqlite3.connect('sqlite.db')
    return flask.g.db

def get_user_id(user_name):
    cur = get_db_handler().cursor()
    cur.execute('SELECT id FROM users WHERE name = ?', ( user_name, ))
    user_id = cur.fetchone()
    if user_id is None:
        raise AppError('<i>%s</i>という名前のユーザーはいませんでした。typoしてませんか？' % flask.escape(user_name))
    return user_id[0]

def get_recommended_problems(user_id):
    cur = get_db_handler().cursor()
    cur.execute('SELECT problem_no FROM favorite_problems WHERE user_id = ?', ( user_id, ))
    favorite_problems = set([ problem_no for problem_no, in cur.fetchall() ])
    if not favorite_problems:
        raise AppError('このユーザーはまだどの問題もふぁぼっていません。なにも判断基準がないのでお手上げだよ')
    cur.execute('SELECT t1.user_id FROM favorite_problems t1 INNER JOIN favorite_problems t2 ON t1.problem_no = t2.problem_no WHERE t2.user_id = ?', ( user_id, ))
    user_dict = collections.Counter()
    for similar_user_id, in cur.fetchall():
        user_dict[similar_user_id] += 1
    problem_dict = collections.Counter()
    for similar_user_id, user_score in user_dict.items():
        cur.execute('SELECT problem_no FROM favorite_problems WHERE user_id = ?', ( similar_user_id, ))
        for problem_no, in cur.fetchall():
            if problem_no not in favorite_problems:
                problem_dict[problem_no] += 1
    problem_dict = list(problem_dict.items())
    problem_dict.sort(key=lambda x: x[1], reverse=True)
    result = []
    for problem_no, score in problem_dict[: 32]:
        cur.execute('SELECT 1 FROM submissions WHERE user_id = ? AND problem_no = ? AND is_ac = 1', ( user_id, problem_no, ))
        if cur.fetchone() is None:
            cur.execute('SELECT name FROM problems WHERE no = ?', ( problem_no, ))
            problem_name, = cur.fetchone()
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
