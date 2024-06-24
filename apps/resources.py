from flask_restful import Resource
from flask import g, jsonify, make_response, request
import apps.models as models
import jwt
import functools
from jwt.exceptions import InvalidSignatureError, DecodeError
from datetime import (
    datetime,
    timezone,
    timedelta
)
import sqlalchemy
from jwt import ExpiredSignatureError

from apps.settings import JWT_SECRET_KEY

def response(status_code, message):
    if status_code != 200:
        return make_response(jsonify({"error": f"{message}"}), status_code)
    return make_response(jsonify({"data": message}), 200)


def is_token_valid(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            accesstoken = request.headers.get("Authorization")[7:]
            jwt.decode(accesstoken, JWT_SECRET_KEY, algorithms=["HS256"])
        except InvalidSignatureError:
            return response(401, "Invalid Access token.")
        except TypeError:
            return response(401, "Please provide access token in headers.")
        except DecodeError:
            return response(401, "JWT exception raised. Please input valid access token.")
        except ExpiredSignatureError:
            return response(401, "Your Access token has expired. Please login again.")
        return func(*args, **kwargs)
    return wrapper

def get_username_from_token():
    accesstoken = request.headers.get("Authorization")[7:]
    return jwt.decode(accesstoken, JWT_SECRET_KEY, algorithms=["HS256"])["username"]


class RegisterUser(Resource):
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return response(404, "Please help to provide JSON inputs")
        username = json_data["username"]
        if g.db.session.query(models.User).filter_by(username=username).one_or_none():
            return response(403, "Username already exists. Please help to choose different username.")
        try:
            user_d = models.User(
                username=json_data["username"],
                password_hash=json_data["password"], # TODO: use hashing lib
                email_id=json_data["email_id"],
                mobile_number=json_data["mobile_number"],
            )
        except KeyError as e:
            return response(401, f"missing field.: {e}")
        try:
            g.db.session.add(user_d)
            g.db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            print(f"error: {e}")
            return response(401, f"database UniqueViolation error!, please enter different username/email-id/mobile-number")
        except Exception as e:
            # some database exception
            print(f"error: {e}")
            return response(401, f"database error occurred. check logs!")
        return response(200, "Ok, successful user registration")


class LoginUser(Resource):
    def post(self):
        pass



class Discussion(Resource):
    def post(self):
        pass




  
    
    # def update(self):
    #     pass
    
    
    # def delete()
