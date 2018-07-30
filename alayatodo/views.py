from . import app
from .core import TodoManager, logged_in, UserManager
from .validators import MessageType, add_information_message, add_validation_message
from .core import get_loggedin_user_id, get_pagination_parameters
from flask import (
    g,
    redirect,
    render_template,
    make_response,
    request,
    session,
    jsonify
)


def get_pagination(page, quantity, user_id):
    todos = TodoManager.paginate(page, quantity, user_id)
    total = TodoManager.count(user_id)
    prev_ = [i for i in range(page - 1, page - 3, -1) if i >= 0]
    prev_.reverse()
    last = total / quantity
    if total % quantity == 0:
        next = page + 1 if page < last - 1 else page
        next_ = [i for i in range(page + 1, page + 3) if i < last]
        last = last - 1
    else:
        next = page + 1 if page < last else page
        next_ = [i for i in range(page + 1, page + 3) if i <= last]
    paginator = {
        'prev': page - 1 if page > 0 else page,
        'last': last,
        'current': page,
        'next': next,
        'prev_': prev_,
        'next_': next_,
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
        session['user'] = user.to_dict()
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
    page, quantity = get_pagination_parameters(request)
    user_id = get_loggedin_user_id(session)
    todos, paginator = get_pagination(page, quantity, user_id)
    return render_template('todos.html', todos=todos, messages=g.messages, paginator=paginator)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@logged_in
def todos_POST():
    page, quantity = get_pagination_parameters(request)
    user_id = get_loggedin_user_id(session)

    field_name = 'description'
    description = request.form.get(field_name, '')
    valid, message = g.validators.validate_not_empty_field(description, field_name)

    if valid:
        TodoManager.insert(description, user_id)
        add_information_message('Todo added correctly.')
    else:
        add_validation_message(message)

    todos, paginator = get_pagination(page, quantity, user_id)

    return render_template('todos.html', todos=todos, messages=g.messages, paginator=paginator)


@app.route('/todo/<id>', methods=['POST'])
@logged_in
def todo_delete(id):
    page, quantity = get_pagination_parameters(request)
    user_id = get_loggedin_user_id(session)

    ok_flag = TodoManager.delete_by_id(id, user_id)
    if ok_flag:
        g.messages.append({'text': 'Todo removed correctly.', 'type': MessageType.Information})
    else:
        g.messages.append({'text': 'You do not have permissions to remove that todo.', 'type': MessageType.Error})

    todos, paginator = get_pagination(page, quantity, user_id)
    return render_template('todos.html', todos=todos, messages=g.messages, paginator=paginator)


@app.route('/todo/uncomplete/<id>', methods=['POST'])
@logged_in
def uncomplete_todo(id):
    page, quantity = get_pagination_parameters(request)
    user_id = get_loggedin_user_id(session)

    TodoManager.uncomplete(id)

    todos, paginator = get_pagination(page, quantity, user_id)
    return render_template('todos.html', todos=todos, messages=g.messages, paginator=paginator)


@app.route('/todo/complete/<id>', methods=['POST'])
@logged_in
def complete_todo(id):
    page, quantity = get_pagination_parameters(request)
    user_id = get_loggedin_user_id(session)

    TodoManager.complete(id)

    todos, paginator = get_pagination(page, quantity, user_id)
    return render_template('todos.html', todos=todos, messages=g.messages, paginator=paginator)


@app.route('/todo/<id>/json', methods=['GET'])
@logged_in
def todo_to_json(id):
    from itsdangerous import json as _json
    todo = TodoManager.get_one_by_id(id)
    if todo:
        return jsonify(todo.to_json())
    return make_response(_json.dumps({'message': 'Todo with "id" %s does not exists' % id}),
                         404,
                         {'Content-Type': 'application/json'})
