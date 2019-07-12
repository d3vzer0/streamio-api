
from app import app, api
from flask import Flask, request, g
from flask_restful import Api, Resource, reqparse
from app.operations import Match
from flask_jwt_extended import jwt_required

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
    decorators = []

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

