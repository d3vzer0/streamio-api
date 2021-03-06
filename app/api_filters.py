from app import app, api, jwt
from app.operations import Regex, Fuzzy, Whitelist
from app.utils import Streaming
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse, abort
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims,
    verify_jwt_in_request
)

from bson.json_util import dumps as loadbson
import json
import asyncio

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


class APIWhitelists(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('value', location='json', required=True, help='Value', type=str)

        if request.method == "GET":
            self.args.add_argument('skip', location='args', required=True, help='Start', type=int)
            self.args.add_argument('limit', location='args', required=True, help='Length', type=int)
            self.args.add_argument('value', required=False, default='', type=str)


    def get(self):
        args = self.args.parse_args()
        result = Whitelist(args.value).get(args.skip, args.limit)
        return result

    @admin_required
    def post(self):
        args = self.args.parse_args()
        result = Whitelist(args.value).create()
        asyncio.run(Streaming().refresh('whitelist'))
        return result

api.add_resource(APIWhitelists, '/api/v1/whitelist')


class APIWhitelist(Resource):
    decorators = [jwt_required, admin_required]

    def delete(self, whitelist_name):
        result = Whitelist(whitelist_name).delete()
        asyncio.run(Streaming().refresh('whitelist'))
        return result

api.add_resource(APIWhitelist, '/api/v1/whitelist/<string:whitelist_name>')


class APIRegex(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('value', location='json', required=True, help='Value', type=str)
            self.args.add_argument('score', location='json', required=False, default=80, type=int)

        if request.method == "GET":
            self.args.add_argument('skip', location='args', required=True, help='Start', type=int)
            self.args.add_argument('limit', location='args', required=True, help='Length', type=int)
            self.args.add_argument('value', required=False, default='', type=str)

    @admin_required
    def post(self):
        args = self.args.parse_args()
        result = Regex(args.value).create(args.score)
        asyncio.run(Streaming().refresh('regex'))
        return result

    def get(self):
        args = self.args.parse_args()
        result = Regex(args.value).get(args.skip, args.limit)
        return result

api.add_resource(APIRegex, '/api/v1/filters/regex')


class APIFuzzy(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('value', location='json', required=True, help='Value', type=str)
            self.args.add_argument('likelihood', location='json', required=True, help='Likelihood', default=None, type=int)
            self.args.add_argument('score', location='json', required=False, default=80, type=int)


        if request.method == "GET":
            self.args.add_argument('skip', location='args', required=True, help='Start', type=int)
            self.args.add_argument('limit', location='args', required=True, help='Length', type=int)
            self.args.add_argument('value', required=False, default='', type=str)

    @admin_required
    def post(self):
        args = self.args.parse_args()
        result = Fuzzy(args.value).create(args.likelihood, args.score)
        asyncio.run(Streaming().refresh('fuzzy'))
        return result

    def get(self):
        args = self.args.parse_args()
        result = Fuzzy(args.value).get(args.skip, args.limit)
        return result

api.add_resource(APIFuzzy, '/api/v1/filters/fuzzy')


class APIFilter(Resource):
    decorators = [jwt_required, admin_required]

    def delete(self, filter_type, filter_name):
        if filter_type == 'fuzzy':
            result = Fuzzy(filter_name).delete()
            asyncio.run(Streaming().refresh('fuzzy'))

        elif filter_type == 'regex':
            result = Regex(filter_name).delete()
            asyncio.run(Streaming().refresh('regex'))
        else:
            result = {'result':'failed', 'data':'Invalid filter type '}

        return result


api.add_resource(APIFilter, '/api/v1/filter/<string:filter_type>/<string:filter_name>')

class APIFiltersState(Resource):
    decorators = [jwt_required, admin_required]

    def get(self):
        result = Streaming().state()
        return result

api.add_resource(APIFiltersState, '/api/v1/filters/state')
