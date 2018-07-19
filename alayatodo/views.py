from alayatodo import app
from .core import TodoManager, logged_in
from flask import (
    g,
    redirect,
    render_template,
    request,
    session
)

import json


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'"
    print sql % (username, password)
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


# security fix: Unauthenticated user can get a todo by its id
@app.route('/todo/<id>', methods=['GET'])
@logged_in
def todo(id):
    todo = TodoManager.get_one_by_id(id)
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@logged_in
def todos():
    todos = TodoManager.get_all()
    return render_template('todos.html', todos=todos, validation_errors=g.validation_errors)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@logged_in
def todos_POST():
    description = g.validators.validate_not_empty_field(request.form.get('description', ''), 'description')

    if description is not None:
        TodoManager.insert(description)

    if g.validation_dirty:
        todos = TodoManager.get_all()
        return render_template('todos.html', todos=todos, validation_errors=g.validation_errors)
    else:
        return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
@logged_in
def todo_delete(id):
    TodoManager.delete_by_id(id)
    return redirect('/todo')


@app.route('/todo/uncomplete/<id>', methods=['POST'])
@logged_in
def uncomplete_todo(id):
    TodoManager.uncomplete(id)
    return redirect(request.referrer)


@app.route('/todo/complete/<id>', methods=['POST'])
@logged_in
def complete_todo(id):
    TodoManager.complete(id)
    return redirect(request.referrer)
