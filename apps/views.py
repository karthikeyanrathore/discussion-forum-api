from apps.resources import (
    RegisterUser,
    LoginUser,
    ShowUsers,
    UsersDetails,
    FollowUser,
    Discussions,
    DiscussionPost,
    CommentPost,
    LikePost
)

from flask import Blueprint
from flask_restful import Api

user_bp = Blueprint("user", __name__)
discuss_bp = Blueprint("discuss", __name__)


user_api = Api(user_bp)
discuss_api = Api(discuss_bp)

user_api.add_resource(RegisterUser, "/users/signup")
user_api.add_resource(LoginUser, "/users/login")
user_api.add_resource(ShowUsers, "/users")
user_api.add_resource(UsersDetails, "/users/<int:user_id>")
user_api.add_resource(FollowUser, "/users/follow/<int:user_id>")


discuss_api.add_resource(Discussions, "/discussions")
discuss_api.add_resource(DiscussionPost, "/discussion/<int:discuss_id>")
discuss_api.add_resource(CommentPost, "/discussion/<int:discuss_id>/comment")
discuss_api.add_resource(LikePost, "/discussion/<int:discuss_id>/like")

# doubtful ?? 
# discuss_api.add_resource(ReplyComment, "/discussion/<int:comment_id>/reply")







