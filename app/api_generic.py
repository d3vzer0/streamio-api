from app import app, api, jwt
from app.models import Users
from app.operations import User, Token
from app.validators import Authentication
from flask import Flask, request, g, redirect
from flask_restful import Api, Resource, reqparse, abort
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims,
    create_refresh_token, jwt_refresh_token_required,
    get_raw_jwt, verify_jwt_in_request
)
import json

@jwt.user_claims_loader
def add_claims_to_access_token(user):
    result = {'role':user.role}
    return result


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username


@jwt.expired_token_loader
def expired_token_callback():
    result = {'status':401, 'sub_status':42, 'data':'Token expired'}
    return json.dumps(result), 401


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    is_revoked = Authentication.blacklist(jti)
    return is_revoked


def verify_setup(func):
    def wrapper(*args, **kwargs):
        user_count = Users.objects(role='admin').count()
        if user_count == 0: return func(*args, **kwargs)
        abort(403)
    return wrapper


def admin_required(func):
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['role'] == 'admin': return func(*args, **kwargs)
        abort(403)
    return wrapper


class APISetup(Resource):
    decorators = [verify_setup]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == 'POST':
            self.args.add_argument('username', location='json',required=True, help='Username field is required')
            self.args.add_argument('password', location='json', required=True, help='Password field is required')
            self.args.add_argument('password_confirm', location='json', required=True, help='Password confirmation field is required')

    def post(self):
        args = self.args.parse_args()
        result = User(args['username']).create(args.password, args.password_confirm, 'admin')
        return result

api.add_resource(APISetup, '/api/v1/setup')

class APIUsers(Resource):
    decorators = [jwt_required, admin_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == 'GET':
            self.args.add_argument('skip', location='args', required=False, default=0, help='Start', type=int)
            self.args.add_argument('limit', location='args', required=False, default=20, help='Length', type=int)
            self.args.add_argument('search', location='args', required=False, help='Search', type=str, default="")

        if request.method == 'POST':
            self.args.add_argument('username', location='json',required=True, help='Username field is required')
            self.args.add_argument('password', location='json', required=True, help='Password field is required')
            self.args.add_argument('role', location='json', required=False, default='user', help='Create user with specific role')
            self.args.add_argument('password_confirm', location='json', required=True, help='Password confirmation field is required')


    def post(self):
        args = self.args.parse_args()
        result = User(args['username']).create(args.password, args.password_confirm, args.role)
        return result

    def get(self):
        args = self.args.parse_args()
        result = User(args.search).get(args.skip, args.limit)
        return result

api.add_resource(APIUsers, '/api/v1/users')


class APIUser(Resource):
    decorators = [jwt_required, admin_required]

    def __init__(self):
        self.args = reqparse.RequestParser()

        if request.method == 'PUT':
            self.args.add_argument('password', location='json', required=False, help='Password field is required')
            self.args.add_argument('password_confirm', location='json', required=False, help='Password confirmation field is required')
            self.args.add_argument('role', location='json', required=True, help='Role field', choices=('user', 'admin'))


    def delete(self, username):
        current_user = get_jwt_identity()
        if current_user == username: 
            result = {'result':'failed', 'message':'Unable to delete self'}, 403
        else:
            result = User(username).delete()
        return result

    def put(self, username):
        args = self.args.parse_args()
        result = User(username).update(args.password, args.password_confirm, args.role)
        return result

api.add_resource(APIUser, '/api/v1/user/<string:username>')


class APIUserPassword(Resource):
    decorators = [jwt_required, admin_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == 'PUT':
            self.args.add_argument('password', location='json', required=True, help='Password field is required')
            self.args.add_argument('password_confirm', location='json', required=True, help='Password confirmation field is required')

    def put(self, username):
        args = self.args.parse_args()
        result = User(username).password(args.password, args.password_confirm)
        return result

api.add_resource(APIUserPassword, '/api/v1/user/<string:username>/password')


class APIUserRole(Resource):
    decorators = [jwt_required, admin_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == 'PUT':
            self.args.add_argument('role', location='json', required=True, help='Role field is required', choices=('admin', 'user'))

    def put(self, username):
        args = self.args.parse_args()
        result = User(username).role(args.role)
        return result

api.add_resource(APIUserRole, '/api/v1/user/<string:username>/role')


class APISelf(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()

        if request.method == 'PUT':
            self.args.add_argument('password', location='json', required=True, help='Password field is required')
            self.args.add_argument('password_confirm', location='json', required=True, help='Password confirmation field is required')
            self.args.add_argument('password_old', location='json', required=True, help='Password confirmation field is required')


    def put(self, username):
        return ''
        
api.add_resource(APISelf, '/api/v1/user')


class APILogin(Resource):
    def __init__(self):
        self.args = reqparse.RequestParser()
        self.username = self.args.add_argument('username', location='json', required=True, help='Username')
        self.password = self.args.add_argument('password', location='json', required=True, help='Password')

    def post(self):
        args = self.args.parse_args()
        validate = Authentication.login(args['username'], args['password'])
        if validate['result'] == 'success':
            access_token = create_access_token(identity=validate['data'])
            refresh_token = create_refresh_token(identity=validate['data'])
            result = {"access_token":access_token, 'refresh_token':refresh_token}
            return result

        else:
            return validate, 401

api.add_resource(APILogin, '/api/v1/login')


class APIRefresh(Resource):
    decorators = [jwt_refresh_token_required]

    def get(self):
        user_object = Users.objects.get(username=get_jwt_identity())
        access_token = create_access_token(identity=user_object)
        result = {"access_token":access_token}
        return result

api.add_resource(APIRefresh, '/api/v1/refresh') 


class APILogoutRefresh(Resource):
    decorators = [jwt_refresh_token_required]

    def get(self):
        jti = get_raw_jwt()['jti']
        revoke_token = RevokeToken.create(jti)
        return revoke_token

api.add_resource(APILogoutRefresh, '/api/v1/logout/refresh')


class APILogout(Resource):
    decorators = [jwt_required]

    def get(self):
        jti = get_raw_jwt()['jti']
        revoke_token = RevokeToken.create(jti)
        return revoke_token

api.add_resource(APILogout, '/api/v1/logout/token')

