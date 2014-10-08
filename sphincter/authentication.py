import random
import string
TOKEN_CHARS = string.ascii_uppercase+string.ascii_lowercase+string.digits

def random_token(n):
    res = ""
    for i in range(n):
        res += random.choice(TOKEN_CHARS)
    return res

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()

class UserManager:
    """
    This is a UserManager. It manages Users.
    """
    def __init__(self, dbpath="sqlite:///sphincter_tokens.db"):
        self.engine = create_engine(dbpath)
        self.session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        
    def get_user_by_token(self, token):
        s = self.session()
        try:
            return s.query(User).filter_by(token=token).one()
        except NoResultFound:
            return None
        
    def add_user(self, email):
        s = self.session()
        u = User(email=email)
        s.add(u)
        s.commit()
        return u

class User(Base):
    __tablename__ = "users"
    
    email = Column(String, primary_key=True)
    token = Column(String)
    
    def __init__(self, email):
        self.email = email
        self.token = random_token(64)
