
from app import app, api, jwt
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from app.operations import Match
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims,
    verify_jwt_in_request
)

@jwt.user_claims_loader
def add_claims_to_access_token(user):
    result = {'role':user.role}
    return result

def admin_required(func):
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['role'] == 'admin': return func(*args, **kwargs)
        abort(403)
    return wrapper


class APIMatches(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "GET":
            self.args.add_argument('skip', location='args', required=True, help='Start', type=int)
            self.args.add_argument('limit', location='args', required=True, help='Length', type=int)
            self.args.add_argument('search', location='args', required=False, help='Search', type=str, default="")

    def get(self):
        args = self.args.parse_args()
        results = Match(args.search).get(args.skip, args.limit)
        return results


api.add_resource(APIMatches, '/api/v1/hits')


class APIConfirm(Resource):
    decorators = [jwt_required, admin_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('url', location='json', required=True, help='URL', type=str)
            self.args.add_argument('action', location='json', required=True, help='Action', type=bool, choices=(True, False))

    def post(self):
        args = self.args.parse_args()
        results = Match(args.url).confirm(args.action)
        return results

api.add_resource(APIConfirm, '/api/v1/confirm')


class APIMonitor(Resource):
    decorators = [jwt_required, admin_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('url', location='json', required=True, help='URL', type=str)
            self.args.add_argument('action', location='json', required=True, help='Action', type=bool, choices=(True, False))

    def post(self):
        args = self.args.parse_args()
        results = Match(args.url).monitor(args.action)
        return results

api.add_resource(APIMonitor, '/api/v1/monitor')

