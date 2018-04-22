from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from db import read_account_by_email, create_account


class User(UserMixin):
    def __init__(self):
        self.first_name = self.last_name = None
        self.email = None
        self.password_hash = None

    @classmethod
    def create(cls, first_name, last_name, email, password):
        self = cls()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = generate_password_hash(password)
        row_count = create_account(self)
        if row_count == 1:
            return self
        else:
            return None

    @classmethod
    def read(cls, email):
        result = read_account_by_email(email)
        if result is not None:
            self = cls()
            self.first_name = result['first_name']
            self.last_name = result['last_name']
            self.email = result['email']
            self.password_hash = result['password_hash']
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
