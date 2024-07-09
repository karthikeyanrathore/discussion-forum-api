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

def get_userid_from_token():
    accesstoken = request.headers.get("Authorization")[7:]
    return jwt.decode(accesstoken, JWT_SECRET_KEY, algorithms=["HS256"])["user_id"]


class RegisterUser(Resource):
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return response(404, "Please help to provide JSON inputs")
        username = json_data["username"]
        if g.db.session.query(models.User).filter_by(username=username).one_or_none():
            return response(403, "Username already exists. Please help to choose different username.")
        try:
            json_data["password_hash"] = json_data["password"]
            del json_data["password"]
            user_d = models.User(**json_data)
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
        json_data = request.get_json()
        if not json_data:
            return response(404, "Please help to provide JSON inputs")
        username = json_data["username"]
        password = json_data["password"]
        user_session = g.db.session.query(models.User).filter_by(username=username).one_or_none()
        if not user_session:
            return response(401, "Username does not exists. Please first signup.")
        if user_session.password_hash != password:
            return response(401, "Incorrect password.")
        jwt_dict = {
            "user_id": user_session.id,
            "username": username,
            "exp": datetime.now(tz=timezone.utc) + timedelta(hours=8)
        }
        access_token = jwt.encode(jwt_dict, JWT_SECRET_KEY, algorithm="HS256")
        ret = user_session.serialize()
        ret["access_token"]=  access_token
        return response(200, ret)


class ShowUsers(Resource):
    def get(self):
        ret = []
        users_m = g.db.session.query(models.User).all()
        for user in users_m:
            ret.append(user.serialize())
        return ret


class UsersDetails(Resource):
    def delete(self, user_id):
        is_user = g.db.session.query(models.User).filter_by(
            id=user_id
        ).one_or_none()
        assert is_user != None, "user does not exists!"
        # First delete all the discussion posts
        # then the user.
        for post in is_user.discussion_posts:
            g.db.session.delete(post)
            g.db.session.commit()
        g.db.session.delete(is_user)
        g.db.session.commit()
        return {"message": "user deleted!"}

    def put(self, user_id):
        json_data = request.get_json()
        if not json_data:
            return response(404, "Please help to provide JSON inputs")
        is_user = g.db.session.query(models.User).filter_by(
            id=user_id
        ).one_or_none()
        assert is_user != None, "user does not exists!"
        if json_data.get("username", None):
            is_user.username = json_data["username"]            
        if json_data.get("email_id", None):
            is_user.email_id = json_data["email_id"]
        if json_data.get("mobile_number", None):
            is_user.mobile_number = json_data["mobile_number"]
        if json_data.get("password", None):
            is_user.password_hash = json_data["password"]
        try:
            g.db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return response(404, "UniqueViolation error!")
        return {"message": "updated!"}

class FollowUser(Resource):
    @is_token_valid
    def post(self, user_id):
        followee_exists = g.db.session.query(models.User).filter_by(
            id=user_id
        ).one_or_none()
        assert followee_exists != None, "Followee does not exists."
        curr_userid_session = get_userid_from_token()
        model_payload = {}
        model_payload["follower_id"] = curr_userid_session
        model_payload["followee_id"] = followee_exists.id
        assert curr_userid_session != followee_exists.id, "you can't follow yourself lol :D"
        try:
            follow_q = models.Follow(**model_payload)
            g.db.session.add(follow_q)
            g.db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            print(f"debug error: {e}")
            return {"message": "you already follow this person."}
        return {"message": f"user id: {curr_userid_session} follows user id:{followee_exists.id}"}


class Discussions(Resource):
    @is_token_valid
    def post(self):
        payload = ""
        if "multipart/form-data" in request.content_type:
            payload = request.form.to_dict()
        else:
            return response(404, "Please help to provide multipart inputs")
        image_file = request.files.get("image_file", None)
        if image_file:
            bytes_image = (image_file.read())
        userid_session = get_userid_from_token()
        model_payload = {}
        model_payload["user_id"] = int(userid_session)
        model_payload["heading"] = payload.get("heading")
        model_payload["text_content"] = payload.get("text_content")
        model_payload["image_data"] = bytes_image if image_file else None

        try:
            discussion_session = models.DiscussionPost(**model_payload)
            g.db.session.add(discussion_session)
            g.db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return response(401, "please provide text content. check logs!")

        if payload.get("tags"):
            tags = payload.get("tags").split(",")
            for tag in tags:
                tag_exists = g.db.session.query(models.Tag).filter_by(
                    title=tag.strip()
                ).one_or_none()
                if not tag_exists:
                    # g.db.session.add(tag_exists)
                    tag_m = models.Tag(title=tag.strip())
                    g.db.session.add(tag_m)
                    g.db.session.commit()
                    discussion_session.tags.append(tag_m)
                else:
                    discussion_session.tags.append(tag_exists)
            g.db.session.commit()
        r_serialize = discussion_session.serialize()
        return (discussion_session.serialize())

    
    def get(self):
        # search post by tags
        r_tag = request.args.get("tag", None)
        if not r_tag:
            out = []
            for post in g.db.session.query(models.DiscussionPost).all():
                out.append(post.serialize())
            return out
        discussions = g.db.session.query(models.DiscussionPost).join(
            models.DiscussionPost.tags
        ).filter(models.Tag.title == r_tag).all()
        out = []
        for dp in discussions:
            out.append(dp.serialize())
        return out
        

class DiscussionPost(Resource):
    def get(self, discuss_id):
        post_exists = g.db.session.query(models.DiscussionPost).filter_by(
            id=discuss_id
        ).one_or_none()
        assert post_exists != None, "post does not exists"
        return post_exists.serialize()

    def put(self, discuss_id):
        pass

    
    def delete(self, discuss_id):
        pass



class CommentPost(Resource):
    @is_token_valid
    def post(self, discuss_id):
        json_data = request.get_json()
        if not json_data:
            return response(404, "Please help to provide JSON inputs")
        # verify discuss_id
        post_exists = g.db.session.query(models.DiscussionPost).filter_by(
            id=discuss_id
        ).one_or_none()
        assert post_exists != None, "post does not exists"
        model_payload = {}
        model_payload["content"] = json_data["content"]
        model_payload["user_id"] = get_userid_from_token()
        model_payload["discussion_id"] = discuss_id
        comment_session = models.Comment(**model_payload)
        g.db.session.add(comment_session)
        g.db.session.commit()
        return {"message": "added comment!"}


class LikePost(Resource):
    @is_token_valid
    def post(self, discuss_id):
        # verify discuss_id
        post_exists = g.db.session.query(models.DiscussionPost).filter_by(
            id=discuss_id
        ).one_or_none()
        assert post_exists != None, "post does not exists"
        model_payload = {}
        model_payload["user_id"] = get_userid_from_token()
        model_payload["discussion_id"] = discuss_id
        try:
            like_session = models.Like(**model_payload)
            g.db.session.add(like_session)
            g.db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            print(f"debug error: {e}")
            return {"message": "user already liked the post."}
        return {"message": "added like!"}


class ReplyComment(Resource):
    # it does not support nested replies like reddit conv.
    @is_token_valid
    def post(self, comment_id):
        json_data = request.get_json()
        if not json_data:
            return response(404, "Please help to provide JSON inputs")
        comment_exists = g.db.session.query(models.Comment).filter_by(
            id=comment_id
        ).one_or_none()
        assert comment_exists != None, "comment does not exists!"
        model_payload = {}
        model_payload["content"] = json_data["content"]
        model_payload["comment_id"] = comment_id
        model_payload["user_id"] = get_userid_from_token()
        model_payload["discussion_id"] = comment_exists.discussion_id
        # print(comment_exists.discussion_id)
        reply_m = models.Reply(**model_payload)
        g.db.session.add(reply_m)
        g.db.session.commit()
        return {"message": "added reply to comment."}
