from app.models import Users
from app.utils import SaltedPassword
import mongoengine
import json

def verify_create(func):
    def wrapper(origin, password, password_confirm, *args):
        if password != password_confirm:
            result = {'result':'failed', 'message':'Confirmation password does not match password'}
            return result
        else:
            return func(origin, password, password_confirm)

    return wrapper

class User:
    def __init__(self, username):
        self.username = username.replace(' ', '')

    def get(self, skip, limit):
        users_object = Users.objects(username__contains=self.username).only('username', 'role')
        result = {'count':users_object.count(), 'results':json.loads(users_object.skip(skip).limit(limit).to_json())}
        return result

    @verify_create
    def password(self, password, password_confirm):
        try:
            user_object = Users.objects(username=self.username)
            password_hash, salt = SaltedPassword(password).create()
            update_user = user_object.update(set__salt=salt, set__password=password_hash)
            result = {'result': 'created', 'message': 'Succesfully updated user password'}

        except mongoengine.errors.DoesNotExist:
            result = {'result': 'failed', 'message': 'User does not exists'}

        except Exception as err:
            result = {'result': 'failed', 'message': 'Failed to update user password'}

        return result

    def role(self, role):
        try:
            user_object = Users.objects(username=self.username)
            update_user = user_object.update(set__role=role)
            result = {'result': 'created', 'message': 'Succesfully updated user role'}

        except mongoengine.errors.DoesNotExist:
            result = {'result': 'failed', 'message': 'User does not exists'}

        except Exception as err:
            result = {'result': 'failed', 'message': 'Failed to update user role'}

        return result

    @verify_create
    def create(self, password, password_confirm, user_role='user'):
        try:
            password_hash, salt = SaltedPassword(password).create()
            user = Users(username=self.username, salt=salt, password=password_hash, role=user_role).save()
            result = {'result': 'created', 'message': 'Succesfully created user'}

        except mongoengine.errors.NotUniqueError:
            result = {'result': 'failed', 'message': 'User already exists'}

        except Exception as err:
            result = {'result': 'failed', 'message': 'Failed to create user'}

        return result

    def delete(self):
        try:
            user_object = Users.objects.get(username=self.username).delete()
            result = {'result': 'deleted', 'message': 'Deleted user from DB'}

        except mongoengine.errors.DoesNotExist:
            result = {'result': 'failed', 'message': 'User does not exist'}

        except Exception as err:
            result = {'result': 'failed', 'message': 'Failed to delete user from DB'}

        return result