from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from . import models


def get_new_post_creates(db: Session, last_id: int):
    return db.execute(
        select(models.Post.user_id, models.Post.post_id).where(models.Post.post_id > last_id)).fetchall()


def get_new_post_comments(db: Session, last_id: int):
    return db.execute(
        select(models.Comment.user_id, models.Comment.post_id).where(models.Comment.comment_id > last_id)).fetchall()


def get_new_post_likes(db: Session, last_id: int):
    return db.execute(
        select(models.PostLike.user_id, models.PostLike.post_id).where(models.PostLike.post_id > last_id)).fetchall()


def get_new_projects(db: Session, last_id: int):
    return db.execute(
        select(models.Project.leader_id, models.Project.project_id, models.Project.field).where(models.Project.project_id > last_id)).fetchall()


def get_new_project_likes(db: Session, last_id: int):
    return db.execute(
        select(models.ProjectLike.user_id, models.ProjectLike.project_id).where(models.ProjectLike.project_like_id > last_id)).fetchall()


def get_new_project_applies(db: Session, last_id: int):
    return db.execute(
        select(models.Apply.user_id, models.Apply.project_id).where(models.Apply.apply_id > last_id)).fetchall()


def get_users(db: Session):
    return db.query(models.User).all()
