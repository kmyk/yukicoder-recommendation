# Python Version: 3.x
# -*- coding: utf-8 -*-

import MySQLdb.cursors
import requests
import itertools
import time
import os
from onlinejudge.yukicoder import YukicoderService

config = {
    'db_host': os.environ.get('DB_HOST', 'localhost'),
    'db_port': int(os.environ.get('DB_PORT', '3306')),
    'db_user': os.environ.get('DB_USER', 'root'),
    'db_password': os.environ.get('DB_PASSWORD', ''),
}

def get_db_handler():
    conn = MySQLdb.connect(
        host    = config['db_host'],
        port    = config['db_port'],
        user    = config['db_user'],
        passwd  = config['db_password'],
        db      = 'yukireco',
        charset = 'utf8mb4',
        cursorclass = MySQLdb.cursors.DictCursor,
        autocommit = True,
    )
    cur = conn.cursor()
    cur.execute("SET SESSION sql_mode='TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY'")  # use kamipo TRADITIONAL
    return cur

def fetch_user(user_id, session, cursor):
    print('[*] fetch user: %d' % user_id)
    user = YukicoderService().get_user(id=user_id, session=session)
    if user is None:
        return False
    cursor.execute('INSERT IGNORE INTO users VALUES (%s, %s)', ( user_id, user['Name'] ))
    return True

def update_user(user_id, session, cursor):
    print('[*] update user: %d' % user_id)
    for problem in YukicoderService().get_user_favorite_problem(id=user_id, session=session):
        problem_no = problem['ナンバー']
        problem_name = problem['問題名']
        print('[*] favorite problem: (%d, %d)' % (user_id, problem_no))
        cursor.execute('INSERT IGNORE INTO problems VALUES (%s, %s)', ( problem_no, problem_name ))
        cursor.execute('INSERT IGNORE INTO favorite_problems VALUES (%s, %s)', ( user_id, problem_no ))

def fetch_submissions(page, session, cursor):
    print('[*] fetch submission: %d' % page)
    num, den = 0, 0
    for submission in YukicoderService().get_submissions(page=page, status='AC', session=session):
        submission_id = submission['#']
        s = submission['問題']
        assert s.startswith('No.')
        problem_no, _, problem_name = s[len('No.') :].partition(' ')
        problem_no = int(problem_no)
        user_name = submission['提出者']
        if '提出者/url' not in submission:
            continue  # anonymous users
        user_id = int(submission['提出者/url'].split('/')[-1])
        cursor.execute('SELECT 1 FROM submissions WHERE id = %s', ( submission_id, ))
        if cursor.fetchone() is None:
            cursor.execute('INSERT IGNORE INTO users VALUES (%s, %s)', ( user_id, user_name ))
            cursor.execute('INSERT IGNORE INTO problems VALUES (%s, %s)', ( problem_no, problem_name ))
            print('[*] submission: (%d, %d, %d)' % (submission_id, problem_no, user_id))
            cursor.execute('INSERT INTO submissions VALUES (%s, %s, %s, 1)', ( submission_id, problem_no, user_id ))
            num += 1
        den += 1
    return num, den

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('what', choices=( 'favorite', 'submission' ))
    parser.add_argument('args', nargs='*', type=int)
    parser.add_argument('--wait', type=float, default=1)
    args = parser.parse_args()

    cursor = get_db_handler()
    session = requests.Session()

    if args.what == 'favorite':
        failure_count = 0
        for user_id in ( args.args or itertools.count() ):
            if fetch_user(user_id, session=session, cursor=cursor):
                update_user(user_id, session=session, cursor=cursor)
                failure_count = 0
            else:
                failure_count += 1
                if failure_count >= 20 and not args.args:
                    break
            time.sleep(args.wait)

    elif args.what == 'submission':
        for page in ( args.args or itertools.count(1) ):
            num, den = fetch_submissions(page=page, session=session, cursor=cursor)
            if (den == 0 or num < den) and not args.args:
                break
            time.sleep(args.wait)
