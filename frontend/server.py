# Python Version: 3.x
# -*- coding: utf-8 -*-

import flask
import MySQLdb.cursors
import os
import collections

app = flask.Flask(__name__)

config = {
    'db_connection_name': os.environ.get('DB_CONNECTION_NAME'),
    'db_host':            os.environ.get('DB_HOST',     'localhost'),
    'db_port':        int(os.environ.get('DB_PORT',     '3306')),
    'db_user':            os.environ.get('DB_USER',     'root'),
    'db_password':        os.environ.get('DB_PASSWORD', ''),
}

class AppError(RuntimeError):
    pass

def get_db_handler():
    if not hasattr(flask.g, 'db'):
        kwargs = {
            'user': config['db_user'],
            'passwd': config['db_password'],
            'db': 'yukireco',
            'charset': 'utf8mb4',
            'cursorclass': MySQLdb.cursors.DictCursor,
        }
        if config['db_connection_name'] is not None:
            kwargs['unix_socket'] = os.path.join('/cloudsql', config['db_connection_name'])
        else:
            kwargs['host'] = config['db_host']
            kwargs['port'] = config['db_port']
        flask.g.db = MySQLdb.connect(**kwargs)
    cur = flask.g.db.cursor()
    cur.execute("SET SESSION sql_mode='TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY'")  # use kamipo TRADITIONAL
    return cur

def get_user_id(user_name):
    cur = get_db_handler()
    cur.execute('SELECT id FROM users WHERE name = %s', ( user_name, ))
    user_id = cur.fetchone()
    if user_id is None:
        raise AppError('<i>%s</i>という名前のユーザーはいませんでした。typoしてませんか？' % flask.escape(user_name))
    return user_id['id']

def render_star(level):
    if level is None:
        return '-'
    s = ''
    for _ in range(int(level.split('.')[0])):
        s += '<i class="fa fa-star"></i>'
    if level.endswith('.5'):
        s += '<i class="fa fa-star-half-full"></i>'
    return s

def get_recommended_problems(user_id):
    cur = get_db_handler()

    # Fav情報の取得 (一括)
    favorite_problems = collections.defaultdict(list)
    inverse_favorite_problems = collections.defaultdict(list)
    cur.execute('SELECT user_id, problem_no FROM favorite_problems')
    for row in cur.fetchall():
        favorite_problems[row['user_id']] += [ row['problem_no'] ]
        inverse_favorite_problems[row['problem_no']] += [ row['user_id'] ]

    # 指定ユーザのものだけ抽出
    if user_id not in favorite_problems:
        raise AppError('このユーザーはまだどの問題もふぁぼっていません。なにも判断基準がないのでお手上げだよ')
    target_favorite_problems = set(favorite_problems[user_id])

    # 類似ユーザの重み付き列挙
    similar_users = collections.Counter()
    for problem_no in target_favorite_problems:
        for similar_user_id in inverse_favorite_problems[problem_no]:
            similar_users[problem_no] += 1

    # おすすめ問題の列挙
    recommended_problems = collections.Counter()
    for similar_user_id, user_score in similar_users.items():
        for problem_no in favorite_problems[similar_user_id]:
            if problem_no not in target_favorite_problems:
                recommended_problems[problem_no] += user_score
    recommended_problems = list(recommended_problems.items())
    recommended_problems.sort(key=lambda x: x[1], reverse=True)

    # AC情報の取得 (対象ユーザ)
    target_accepted_problems = set()
    cur.execute('SELECT DISTINCT problem_no FROM submissions WHERE user_id = %s AND is_ac = 1', ( user_id, ))
    for row in cur.fetchall():
        target_accepted_problems.add(row['problem_no'])

    # 問題情報の取得 (一括)
    problems = {}
    cur.execute('SELECT * FROM problems')
    for row in cur.fetchall():
        problems[row['no']] = dict(row)

    # 出力の構成
    result = []
    for problem_no, score in recommended_problems:
        if problem_no not in target_accepted_problems:
            problem_name = problems[problem_no]['name']
            solved = problems[problem_no]['solved']
            if solved is None:
                solved = '-'
            result += [ {
                'name': 'No %d. %s' % (problem_no, problem_name),
                'url': 'https://yukicoder.me/problems/no/%d' % problem_no,
                'level': render_star(problems[problem_no]['level']),
                'solved': solved,
                'score': str(score),
            } ]
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
