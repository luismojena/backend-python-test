from . import app
from .core import TodoManager, logged_in, UserManager
from .validators import MessageType
from flask import (
    g,
    redirect,
    render_template,
    request,
    session
)


def get_pagination():
    page = int(request.values.get('page', 0))
    quantity = int(request.values.get('quantity', 5))
    todos = TodoManager.paginate(page, quantity)
    total = TodoManager.count()
    prev_ = [i for i in range(page - 1, page - 3, -1) if i >= 0]
    prev_.reverse()
    paginator = {
        'prev': page - 1 if page > 0 else page,
        'last': total / quantity,
        'current': page,
        'next': page + 1 if page < total / quantity else page,
        'prev_': prev_,
        'next_': [i for i in range(page + 1, page + 3) if i <= total / quantity],
        'quantity': quantity
    }

    return todos, paginator


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

    user = UserManager.authenticate(username, password)

    if user:
        session['user'] = user.to_json()
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
    todos, paginator = get_pagination()
    return render_template('todos.html', todos=todos, messages=g.messages, paginator=paginator)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@logged_in
def todos_POST():
    description = g.validators.validate_not_empty_field(request.form.get('description', ''), 'description')

    if description is not None:
        TodoManager.insert(description)
        g.messages.append({'text': 'Todo added correctly.', 'type': MessageType.Information})

    todos, paginator = get_pagination()

    return render_template('todos.html', todos=todos, messages=g.messages, paginator=paginator)


@app.route('/todo/<id>', methods=['POST'])
@logged_in
def todo_delete(id):
    TodoManager.delete_by_id(id)
    g.messages.append({'text': 'Todo removed correctly.', 'type': MessageType.Information})
    todos, paginator = get_pagination()
    return render_template('todos.html', todos=todos, messages=g.messages, paginator=paginator)


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


@app.route('/todo/<id>/json', methods=['GET'])
@logged_in
def todo_to_json(id):
    todo = TodoManager.get_one_by_id(id)
    return todo.to_json()
