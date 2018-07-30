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
        todo = Todo.query.get(id)
        return todo

    @staticmethod
    def get_all():
        todos = Todo.query.all()
        return todos

    @staticmethod
    def delete_by_id(id, user_id):
        todo = Todo.query.get_or_404(id)
        if todo.user_id == user_id:
            db.session.delete(todo)
            db.session.commit()
            return True
        return False

    @staticmethod
    def insert(description, user_id):
        todo = Todo(description=description, user_id=user_id)
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
    def paginate(page, quantity, user_id):
        pivot = page * quantity
        todos = Todo.query.filter_by(user_id=user_id).order_by(Todo.id).limit(quantity).offset(pivot)
        return todos

    @staticmethod
    def count(user_id):
        count = Todo.query.filter_by(user_id=user_id).count()
        return count


def logged_in(f):
    @wraps(f)
    def _wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)

    return _wrapper
