from sqlalchemy import Column, ForeignKey, BigInteger, VARCHAR
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(VARCHAR(64), primary_key=True, index=True)
    organization = Column(VARCHAR(255))
    major = Column(VARCHAR(255))
    minor = Column(VARCHAR(255))

    interest_areas = Column(VARCHAR(255))
    skills = Column(VARCHAR(255))

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    post_likes = relationship("PostLike", back_populates="user")


class Post(Base):
    __tablename__ = "post"

    post_id = Column(BigInteger, primary_key=True,
                     index=True, autoincrement=True)
    user_id = Column(VARCHAR(64), ForeignKey("user.user_id"))

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("PostLike", back_populates="post")


class Comment(Base):
    __tablename__ = "comment"

    comment_id = Column(BigInteger, primary_key=True,
                        index=True, autoincrement=True)
    user_id = Column(VARCHAR(64), ForeignKey("user.user_id"))
    post_id = Column(BigInteger, ForeignKey("post.post_id"))

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")


class PostLike(Base):
    __tablename__ = "post_like"

    post_like_id = Column(BigInteger, primary_key=True,
                          index=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey("post.post_id"))
    user_id = Column(VARCHAR(64), ForeignKey("user.user_id"))

    user = relationship("User", back_populates="post_likes")
    post = relationship("Post", back_populates="likes")


class Project(Base):
    __tablename__ = "project"

    project_id = Column(BigInteger, primary_key=True,
                        index=True, autoincrement=True)
    leader_id = Column(VARCHAR(64), ForeignKey("user.user_id"))
    field = Column(VARCHAR(255))

    likes = relationship("ProjectLike", back_populates="project")
    applies = relationship("Apply", back_populates="project")


class ProjectLike(Base):
    __tablename__ = "project_like"

    project_like_id = Column(BigInteger, primary_key=True,
                             index=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("project.project_id"))
    user_id = Column(VARCHAR(64), ForeignKey("user.user_id"))

    project = relationship("Project", back_populates="likes")


class Apply(Base):
    __tablename__ = "apply"

    apply_id = Column(BigInteger, primary_key=True,
                      index=True, autoincrement=True)
    project_id = Column(BigInteger, ForeignKey("project.project_id"))
    user_id = Column(VARCHAR(64), ForeignKey("user.user_id"))

    project = relationship("Project", back_populates="applies")
