from typing import List
from pydantic import BaseModel


class UserBase(BaseModel):
    user_id: str


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


# 이렇게 나중에 선언된 모델을 참조할 수 있도록 하기 위해 별도로 설정해줍니다.
User.update_forward_refs()
Post.update_forward_refs()
