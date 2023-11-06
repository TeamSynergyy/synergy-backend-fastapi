from typing import List
from pydantic import BaseModel


class UserBase(BaseModel):
    user_id: str
    organization: str
    major: str
    minor: str
    interest_areas: str
    skills: str


class User(UserBase):
    posts: List["Post"] = []

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    post_id: int
    user_id: str


class Post(PostBase):
    comments: List["Comment"] = []
    likes: List["PostLike"] = []

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    comment_id: int
    user_id: str
    post_id: int


class Comment(CommentBase):
    class Config:
        orm_mode = True


class PostLikeBase(BaseModel):
    post_like_id: int
    post_id: int
    user_id: str


class PostLike(PostLikeBase):
    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    project_id: int
    leader_id: str
    field: str


class ProjectLikeBase(BaseModel):
    project_like_id: int
    project_id: int
    user_id: str


class ApplyBase(BaseModel):
    apply_id: int
    project_id: int
    user_id: str
