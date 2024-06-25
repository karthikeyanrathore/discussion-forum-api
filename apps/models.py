from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy import Text, LargeBinary
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
        pass



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
        pass


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



# How CASCADE works in the case of many-to-many relationship?
# back_populates works in vice-versa way