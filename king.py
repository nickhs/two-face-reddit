from rq import Queue, use_connection
from serf import create, upvote, kill

use_connection()
q = Queue('main', default_timeout=1200)

def create_new_user(username, password='password'):
    return q.enqueue(create, username=username)


def upvote_post(username, title=''):
    return q.enqueue(upvote, username=username, title=title)


def rollback(username):
    return q.enqueue(kill, username)

