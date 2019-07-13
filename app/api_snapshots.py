from app import app, api
from flask import Flask, request, g, make_response
from flask_restful import Api, Resource, reqparse, inputs
from app.models import Snapshots
from flask_jwt_extended import jwt_required

import bson
import json


class APISnapshot(Resource):
    decorators = [jwt_required]

    def get(self, snapshot_id):
        snapshot = Snapshots.objects.get(screenshot=bson.objectid.ObjectId(snapshot_id))
        snapshot_file = snapshot.screenshot.read()
        filename = "%s.png" %(snapshot_id)
        response = make_response(snapshot_file)
        response.headers['Content-Type'] = "image/png"
        return response

api.add_resource(APISnapshot, '/api/v1/snapshot/<string:snapshot_id>')


class APISnapshots(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.args = reqparse.RequestParser()
        if request.method == "GET":
            self.args.add_argument('max', location='args', required=False, help='max entries', type=int, default=25)
            self.args.add_argument('search', location='args', required=False, default="")
            self.args.add_argument('distinct', location='args', required=False, default=False, type=inputs.boolean)

    def get(self):
        args = self.args.parse_args()
        if args.distinct:
            pipeline = [ { "$group" : { "_id" : {"hash": "$sha256", "url": "$url" },
                "screenshot": { "$first": "$screenshot"  },
                "firstSeen": { "$first": "$timestamp" } } }, 
                { "$limit": args.max } ]

            get_snaps = Snapshots.objects(url__contains=args.search).aggregate(*pipeline)
            results = json.loads(bson.json_util.dumps(get_snaps))
        else:
            get_snaps = Snapshots.objects(url__contains=args.search).order_by('-timestamp').limit(args.max)
            results = json.loads(get_snaps.to_json())

        return results

api.add_resource(APISnapshots, '/api/v1/snapshots')
