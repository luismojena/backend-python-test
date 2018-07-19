from flask import session, redirect, g
from functools import wraps


class MessageType:
    Error = 1
    Information = 2


class TodoManager:

    @staticmethod
    def get_one_by_id(id):
        cur = g.db.execute("SELECT * FROM todos WHERE id ='%s'" % id)
        todo = cur.fetchone()
        return todo

    @staticmethod
    def get_all():
        cur = g.db.execute("SELECT * FROM todos")
        todos = cur.fetchall()
        return todos

    @staticmethod
    def delete_by_id(id):
        g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
        g.db.commit()

    @staticmethod
    def insert(description):
        g.db.execute(
            "INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"
            % (session['user']['id'], description)
        )
        g.db.commit()

    @staticmethod
    def uncomplete(id):
        TodoManager._update_completed(id, 0)

    @staticmethod
    def complete(id):
        TodoManager._update_completed(id, 1)

    @staticmethod
    def _update_completed(id, value):
        g.db.execute(
            "UPDATE todos SET completed = %s WHERE id = '%s'" % (value, id)
        )
        g.db.commit()


def logged_in(f):
    @wraps(f)
    def _wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)

    return _wrapper
