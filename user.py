from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

import db


class User(UserMixin):
    def __init__(self):
        self.id = None
        self.first_name = self.last_name = None
        self.email = None
        self.password_hash = None
        self.is_superuser = False

    @classmethod
    def create(cls, first_name, last_name, email, password):
        new_account = db.create_account({
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password_hash': generate_password_hash(password)
        })
        if new_account is not None:
            self = cls()
            self.first_name = new_account['first_name']
            self.last_name = new_account['last_name']
            self.email = new_account['email']
            self.password_hash = new_account['password_hash']
            self.is_superuser = new_account['is_superuser']
            return self
        else:
            return None

    @classmethod
    def read(cls, email):
        result = db.read_account_by_email(email)
        if result is not None:
            self = cls()
            self.id = result['id']
            self.first_name = result['first_name']
            self.last_name = result['last_name']
            self.email = result['email']
            self.password_hash = result['password_hash']
            self.is_superuser = result['is_superuser']
            return self
        else:
            return None

    def get_id(self):
        return self.email

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


if __name__ == "__main__":
    query = """
    INSERT INTO accounts (first_name, last_name, email, password_hash)
    VALUES ('Admin', 'User', 'admin@example.com', '{}')
    """
    print(query.format(generate_password_hash('password')))
