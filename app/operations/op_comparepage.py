from app.models import ComparePages as ComparePages
import mongoengine
import json
import bson


class ComparePage:
    def __init__(self, url):
        self.url = url

    def get(self, skip, limit):
        pipeline = [ {'$lookup': {
            'from': 'snapshots', 'let': { 'url': '$url' }, 'as': 'screenshots',
            'pipeline': [ { '$match': { '$expr': {'$eq': ['$url', '$$url'] } }  }, {'$limit': 1} ] } } ]

        objects = ComparePages.objects(url__contains=self.url)
        result = {'count':objects.count(), 'data':json.loads(bson.json_util.dumps(objects.skip(skip).limit(limit).aggregate(*pipeline)))}
        return result

    def create(self, score, tag):
        try:
            filter = ComparePages(url=self.url, score=score, tag=tag).save()
            result = {'result': 'created', 'message': 'Succesfully added page to compare table'}

        except mongoengine.errors.NotUniqueError:
            result = {'result': 'failed', 'message': 'Url already exists in compare table'}

        except Exception as err:
            result = {'result': 'failed', 'message': 'Failed to add url to compare table'}

        return result 


    def delete(self):
        try:
            filter_object = ComparePages.objects.get(id=self.url).delete()
            result = {'result': 'deleted', 'message': 'Deleted url from compare table'}

        except mongoengine.errors.DoesNotExist:
            result = {'result': 'failed', 'message': 'URL does not exist in compare table'}

        except Exception as err:
            result = {'result': 'failed', 'message': 'Failed to delete url from compare table'}

        return result
