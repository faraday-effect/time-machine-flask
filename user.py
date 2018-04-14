from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from db import read_user_by_email, create_user


class User(UserMixin):
    def __init__(self):
        self.valid_user = False
        self.first_name = self.last_name = None
        self.email = self.password_hash = None

    def create(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        create_user(self)
        return self

    def read(self, email):
        result = read_user_by_email(email)
        if result is not None:
            self.valid_user = True
            self.first_name = result['first_name']
            self.last_name = result['last_name']
            self.email = result['email']
            self.password_hash = result['password_hash']
            return self
        else:
            return None

    def get_id(self):
        return self.email

    @property
    def password(self):
        raise AttributeError('Not allowed to read password')

    @password.setter
    def password(self, password):
        self['password_hash'] = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


if __name__ == "__main__":
    query = """
    INSERT INTO account (first_name, last_name, email, password_hash)
    VALUES ('Admin', 'User', 'admin@example.com', '{}')
    """
    print(query.format(generate_password_hash('password')))
