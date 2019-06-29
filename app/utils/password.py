from app.utils import Random
import hashlib

class SaltedPassword:
    def __init__(self, password):
        self.password = password

    def create(self):
        salt = Random(32).create()
        hash_object = hashlib.sha512()
        password_string = salt + self.password
        hash_object.update(password_string.encode('utf-8'))
        return str(hash_object.hexdigest()), salt
