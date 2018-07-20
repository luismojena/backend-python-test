from flask import session, redirect, g
from .models import db, User, Todo
from functools import wraps
from werkzeug.security import check_password_hash


class UserManager:
    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            return user
        return None


class TodoManager:

    @staticmethod
    def get_one_by_id(id):
        todo = Todo.query.get_or_404(id)
        return todo

    @staticmethod
    def get_all():
        todos = Todo.query.all()
        return todos

    @staticmethod
    def delete_by_id(id):
        todo = Todo.query.get_or_404(id)
        db.session.delete(todo)
        db.session.commit()

    @staticmethod
    def insert(description):
        userid = session['user']['id']
        todo = Todo(description=description, user_id=userid)
        db.session.add(todo)
        db.session.commit()

    @staticmethod
    def uncomplete(id):
        TodoManager._update_completed(id, 0)

    @staticmethod
    def complete(id):
        TodoManager._update_completed(id, 1)

    @staticmethod
    def _update_completed(id, value):
        todo = Todo.query.get_or_404(id)
        todo.completed = value
        db.session.commit()

    @staticmethod
    def paginate(page, quantity):
        pivot = page * quantity
        todos = Todo.query.order_by(Todo.id).limit(quantity).offset(pivot)
        return todos

    @staticmethod
    def count():
        count = Todo.query.count()
        return count


def logged_in(f):
    @wraps(f)
    def _wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)

    return _wrapper
