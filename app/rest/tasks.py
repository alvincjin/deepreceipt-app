from flask import Flask, jsonify, abort, make_response
from flask_restful import Resource, reqparse, fields, marshal
from flask_httpauth import HTTPBasicAuth
from app import restApi
from ..models import User, Post


auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}


user_fields = {
    'id': fields.Integer,
    'nickname': fields.String,
    'firstname': fields.String,
    'lastname': fields.String,
    'email': fields.String,
    'phone': fields.Integer,
    'address': fields.String
}


post_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'body': fields.String,
    'user_id': fields.Integer,
    'location': fields.String,
    'price': fields.Integer,
    'address': fields.String,
    'badroom_no': fields.Integer,
    'garage_no': fields.Integer,
    'bathroom_no': fields.Integer,
    'style': fields.String
}


class TaskListAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, default="",
                                   location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        return {'tasks': [marshal(task, task_fields) for task in tasks]}

    def post(self):
        args = self.reqparse.parse_args()
        task = {
            'id': tasks[-1]['id'] + 1,
            'title': args['title'],
            'description': args['description'],
            'done': False
        }
        tasks.append(task)
        return {'task': marshal(task, task_fields)}, 201


class TaskAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        return {'task': marshal(task[0], task_fields)}

    def put(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        task = task[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                task[k] = v
        return {'task': marshal(task, task_fields)}

    def delete(self, id):
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            abort(404)
        tasks.remove(task[0])
        return {'result': True}


class UserAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('nickname', type=str, default="", location='json')
        self.reqparse.add_argument('firstname', type=str, default="", location='json')
        self.reqparse.add_argument('lastname', type=str, default="", location='json')
        self.reqparse.add_argument('email', type=str, default="", location='json')
        self.reqparse.add_argument('phone', type=str, default="", location='json')
        self.reqparse.add_argument('address', type=str, default="", location='json')

        super(UserAPI, self).__init__()

    def get(self, id):
        user = User.query.get_or_404(id)

        return {'user': marshal(user, user_fields)}


class PostAPI(Resource):
    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('title', type=str, default="", location='json')
        self.reqparse.add_argument('body', type=str, default="", location='json')
        self.reqparse.add_argument('user_id', type=int, default="", location='json')
        self.reqparse.add_argument('location', type=str, default="", location='json')
        self.reqparse.add_argument('price', type=int, default="", location='json')
        self.reqparse.add_argument('address', type=str, default="", location='json')
        self.reqparse.add_argument('badroom_no', type=int, default="", location='json')
        self.reqparse.add_argument('garage_no', type=int, default="", location='json')
        self.reqparse.add_argument('bathroom_no', type=int, default="", location='json')
        self.reqparse.add_argument('style', type=str, default="", location='json')

        super(PostAPI, self).__init__()

    def get(self, id):
        post = Post.query.get_or_404(id)

        return {'post': marshal(post, post_fields)}

restApi.add_resource(TaskListAPI, '/todo/api/v1.0/tasks', endpoint='tasks')
restApi.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint='task')
restApi.add_resource(UserAPI, '/users/<int:id>', endpoint='user')
restApi.add_resource(PostAPI, '/posts/<int:id>', endpoint='post')