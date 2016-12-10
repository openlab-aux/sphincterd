import random
import string
TOKEN_CHARS = string.ascii_uppercase+string.ascii_lowercase+string.digits

from hashlib import sha256

def random_token(n):
    res = ""
    for i in range(n):
        res += random.choice(TOKEN_CHARS)
    return res
    
import logging

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
            token_hash = sha256(token).hexdigest()
            u = s.query(User).filter(User.token_hash == token_hash and
                                     User.token_type == "web").one()
            logging.info("found user %s" % u.email)
            return u
        except NoResultFound:
            logging.info("Could't find user for token hash %s" % token_hash)
            return None
        finally:
            s.close()
        
    def add_user(self, email, token):
        s = self.session()
        u = User(email=email, token=token, token_type = "web")
        s.add(u)
        s.commit()
        return u
    
    def check_token(self, token):
        u = self.get_user_by_token(token)
        if u is not None:
            return True
        return False

class User(Base):
    __tablename__ = "users"
    
    email = Column(String, primary_key=True)
    token_hash = Column(String)
    token_type = Column(String)
    
    def __init__(self, email, token, token_type):
        self.email = email
        self.token_hash = sha256(token).hexdigest()
        self.token_type = token_type
