from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy import Text, LargeBinary, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql
from sqlalchemy import cast, literal_column


from apps.database import db

class User(db.Model):

    __tablename__ = "users"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    email_id = Column(String, nullable=False, unique=True)
    mobile_number = Column(Integer, nullable=False, unique=True)
    created_at = Column(db.DateTime, server_default=db.func.now())
    updated_at = Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # one-to-many
    discussion_posts = relationship(
        "DiscussionPost",
        back_populates="users_d", # name of relationship defined in another model.
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy=True,
        foreign_keys="DiscussionPost.user_id",
    )
    # TODO: add followers, followee

    def serialize(self):
        out = {}
        out["id"] = self.id
        out["username"] = self.username
        out["email_id"] = self.email_id
        out["mobile_number"] = self.mobile_number
        out["created_at"] = self.created_at.strftime("%d/%m/%Y %H:%M:%S")
        out["updated_at"] = self.updated_at.strftime("%d/%m/%Y %H:%M:%S")
        return out



class DiscussionPost(db.Model):
    
    __tablename__ = "discussion_posts"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="foreign key to User ID",
    )
    heading = Column(String, nullable=False)
    text_content = Column(Text, nullable=False)
    image_data = Column(LargeBinary, nullable=True)
    created_at = Column(db.DateTime, server_default=db.func.now())
    updated_at = Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    users_d = relationship(
        "User",
        back_populates="discussion_posts",
        foreign_keys=[user_id],
    )
    # many-to-many
    tags = relationship(
        "Tag",
        secondary="discussion_tags",
        back_populates="discussion_posts"
    )
    # one-to-many
    likes = relationship(
        "Like",
        back_populates="discussion_posts",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy=True,
        foreign_keys="Like.discussion_id",
    )
    # one-to-many
    comments = relationship(
        "Comment",
        back_populates="discussion_posts",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy=True,
        foreign_keys="Comment.discussion_id",
    )

    def serialize(self):
        out = {}
        out["id"] = self.id
        out["user_id"] = self.user_id
        out["heading"] = self.heading
        out["text_content"] = self.text_content
        out["created_at"] = self.created_at.strftime("%d/%m/%Y %H:%M:%S")
        out["updated_at"] = self.updated_at.strftime("%d/%m/%Y %H:%M:%S")
        out["image_present"] = True if self.image_data else False
        if self.tags:
            post_tags = []
            for tag in self.tags:
                post_tags.append({"id": tag.id, "title": tag.title})
            out["tags"] = post_tags
        if self.comments:
            com = []
            for comment in self.comments:
                replies = []
                if comment.replies:
                    for reply in comment.replies:
                        replies.append(reply.content)
                com.append(f"{comment.content}: {replies}")
            out["comments"] = com
        if self.likes:
            out["likes"] = len(self.likes)
        return out

class Tag(db.Model):
    
    __tablename__ = "tag"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    title =  Column(String, nullable=False, unique=True)
    # many-to-many
    discussion_posts = relationship(
        "DiscussionPost",
        secondary="discussion_tags",
        back_populates="tags"
    )


class DiscussionTags(db.Model):

    __tablename__ = "discussion_tags"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    discussion_id = Column(Integer, ForeignKey('discussion_posts.id'))
    tag_id = Column(Integer, ForeignKey('tag.id'))


class Like(db.Model):
    # store other users id who liked the discussion post
    
    __tablename__ = "likes"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    discussion_id = Column(Integer, ForeignKey('discussion_posts.id', ondelete="CASCADE"), nullable=False)
    # so that same user does not like the post > 1 time.
    UniqueConstraint(user_id, discussion_id)
    discussion_posts = relationship("DiscussionPost", back_populates="likes")


class Comment(db.Model):

    __tablename__ = "comments"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    discussion_id = Column(Integer, ForeignKey('discussion_posts.id', ondelete="CASCADE"), nullable=False)
    discussion_posts = relationship("DiscussionPost", back_populates="comments")

    created_at = Column(db.DateTime, server_default=db.func.now())
    updated_at = Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # one-to-many
    replies = relationship(
        "Reply",
        back_populates="comments",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy=True,
        foreign_keys="Reply.comment_id", # id defined in another model.
    )
    def serialize(self):
        out = {}
        out["id"] = self.id
        out["user_id"] = self.user_id # author
        out["content"] = self.content
        out["discussion_id"] = self.discussion_id
        re = []
        for reply in self.replies:
            re.append({"id": reply.id, "content": reply.content})
        out["replies"] = re
        return out


class Reply(db.Model):

    __tablename__ = "replies"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    discussion_id = Column(Integer, ForeignKey('discussion_posts.id', ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    comment_id = Column(Integer, ForeignKey('comments.id', ondelete="CASCADE"), nullable=False)
    comments = relationship("Comment", back_populates="replies")


class Follow(db.Model):

    __tablename__ = "follows"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id  = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    # person who is followed by follower :D
    followee_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    UniqueConstraint(follower_id, followee_id)


# How CASCADE works in the case of many-to-many relationship?
# back_populates works in vice-versa way