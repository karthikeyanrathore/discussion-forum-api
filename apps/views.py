from apps.resources import (
    RegisterUser,
    LoginUser
)

from flask import Blueprint
from flask_restful import Api

auth_bp = Blueprint("auth", __name__)

auth_api = Api(auth_bp)

auth_api.add_resource(RegisterUser, "/auth/signup")
auth_api.add_resource(LoginUser, "/auth/login")






