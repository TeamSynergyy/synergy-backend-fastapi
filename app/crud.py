from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from . import models


def get_new_creates(db: Session, lastFittedCreatedId: int):
    return db.execute(
        select(models.Post.user_id, models.Post.post_id).where(models.Post.post_id > lastFittedCreatedId)).fetchall()


def get_new_commented(db: Session, lastFittedCommentId: int):
    return db.execute(
        select(models.Comment.user_id, models.Comment.post_id).where(models.Comment.comment_id > lastFittedCommentId)).fetchall()


def get_new_liked(db: Session, lastFittedLikeId: int):
    return db.execute(
        select(models.PostLike.user_id, models.PostLike.post_id).where(models.PostLike.post_id > lastFittedLikeId)).fetchall()
