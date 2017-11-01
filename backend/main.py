# Python Version: 3.x
# -*- coding: utf-8 -*-

import sqlite3
import requests
import itertools
import time
from onlinejudge.yukicoder import YukicoderService

def get_db_handler(path):
    conn = sqlite3.connect(path)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def fetch_user(user_id, session, cursor):
    print('[*] fetch user: %d' % user_id)
    user = YukicoderService().get_user(id=user_id, session=session)
    if user is None:
        return False
    cursor.execute('INSERT OR REPLACE INTO users VALUES (?, ?)', ( user_id, user['Name'] ))
    return True

def update_user(user_id, session, cursor):
    print('[*] update user: %d' % user_id)
    for problem in YukicoderService().get_user_favorite_problem(id=user_id, session=session):
        problem_no = problem['ナンバー']
        problem_name = problem['問題名']
        print('[*] favorite problem: (%d, %d)' % (user_id, problem_no))
        cursor.execute('INSERT OR IGNORE INTO problems VALUES (?, ?)', ( problem_no, problem_name ))
        cursor.execute('INSERT OR IGNORE INTO favorite_problems VALUES (?, ?)', ( user_id, problem_no ))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('user_id', nargs='*', type=int)
    parser.add_argument('--db-path', required=True)
    parser.add_argument('--wait', type=float, default=1)
    args = parser.parse_args()

    connection = get_db_handler(path=args.db_path)
    cursor = connection.cursor()
    session = requests.Session()
    failure_count = 0
    for user_id in ( args.user_id or itertools.count() ):
        if fetch_user(user_id, session=session, cursor=cursor):
            update_user(user_id, session=session, cursor=cursor)
            failure_count = 0
        else:
            failure_count += 1
            if failure_count >= 5 and not args.user_id:
                break
        connection.commit()
        time.sleep(args.wait)
