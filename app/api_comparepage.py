from app import app, api, jwt
from app.operations import ComparePage
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


class APIComparePages(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "POST":
            self.args.add_argument('url', location='json', required=True, help='URL', type=str)
            self.args.add_argument('score', location='json', required=True, help='Score', type=str)
            self.args.add_argument('tag', location='json', required=True, help='Tag', type=str)

        if request.method == "GET":
            self.args.add_argument('skip', location='args', required=False, help='Start', type=int, default=0)
            self.args.add_argument('limit', location='args', required=False, help='Length', type=int, default=25)
            self.args.add_argument('search', required=False, default='', type=str)


    def get(self):
        args = self.args.parse_args()
        result = ComparePage(args.search).get(args.skip, args.limit)
        return result

    @admin_required
    def post(self):
        args = self.args.parse_args()
        result = ComparePage(args.url).create(args.score, args.tag)
        return result

api.add_resource(APIComparePages, '/api/v1/comparepages')


class APIComparePage(Resource):
    decorators = [jwt_required, admin_required]


    def delete(self, whitelist_name):
        # result = Whitelist(whitelist_name).delete()
        # asyncio.run(Streaming().refresh('whitelist'))
        return 'result'

api.add_resource(APIComparePage, '/api/v1/comparepage/<string:compare_id>')
