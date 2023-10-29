from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy.sql import select, desc
from . import models, crud
from .database import SessionLocal, engine
from lightfm import LightFM
from lightfm.data import Dataset
import numpy as np

# LightFM
dataset_post = Dataset()
dataset_project = Dataset()
lfm_post = LightFM(loss='warp')
lfm_project = LightFM(loss='warp')

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

lastFittedPostCreateId = 0
lastFittedPostLikeId = 0
lastFittedPostCommentId = 0
lastFittedProjectCreateId = 0
lastFittedProjectLikeId = 0
lastFittedProjectApplyId = 0


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fit_dataset_post(post_creates, post_comments, post_likes):
    users_post = set(
        list(map(lambda x: x[0], post_creates + post_comments + post_likes)))
    posts_ids = set(
        list(map(lambda x: x[1], post_creates + post_comments + post_likes)))

    dataset_post.fit_partial(users_post, posts_ids)

    num_users_post, num_posts = dataset_post.interactions_shape()
    print('Num users_post {}, num_posts {}.'.format(num_users_post, num_posts))


def fit_dataset_project(project_creates, project_applies, project_likes):
    users_project = set(
        list(map(lambda x: x[0], project_creates + project_likes + project_applies)))
    projects_ids = set(
        list(map(lambda x: x[1], project_creates + project_likes + project_applies)))

    dataset_project.fit_partial(users_project, projects_ids)

    num_users_project, num_projects = dataset_project.interactions_shape()
    print('Num users_project {}, num_projects {}.'.format(
        num_users_project, num_projects))


@app.get("/fit_model")
def fit_model(db: Session = Depends(get_db)):
    global lastFittedPostCreateId, lastFittedPostLikeId, lastFittedPostCommentId

    post_creates = crud.get_new_post_creates(db, lastFittedPostCreateId)
    post_comments = crud.get_new_post_comments(db, lastFittedPostCommentId)
    post_likes = crud.get_new_post_likes(db, lastFittedPostLikeId)

    fit_dataset_post(post_creates, post_comments, post_likes)

    (post_interactions, _) = dataset_post.build_interactions(
        post_creates + post_comments + post_likes)

    print(repr(post_interactions))
    lfm_post.fit(post_interactions, epochs=30)

    if post_creates:
        lastFittedPostCreateId = max([x[1] for x in post_creates])
    if post_comments:
        lastFittedPostCommentId = max([x[1] for x in post_comments])
    if post_likes:
        lastFittedPostLikeId = max([x[1] for x in post_likes])

    global lastFittedProjectCreateId, lastFittedProjectLikeId, lastFittedProjectApplyId

    project_creates = list(map(lambda x: (x[0], x[1]), crud.get_new_projects(
        db, lastFittedProjectCreateId)))
    project_applies = crud.get_new_project_applies(
        db, lastFittedProjectApplyId)
    project_likes = crud.get_new_project_likes(db, lastFittedProjectLikeId)

    print(project_creates)
    fit_dataset_project(project_creates, project_applies, project_likes)

    (project_interactions, _) = dataset_project.build_interactions(
        project_creates + project_applies + project_likes)

    print(repr(project_interactions))
    lfm_project.fit(project_interactions, epochs=30)

    if project_creates:
        lastFittedProjectCreateId = max([x[1] for x in project_creates])
    if project_applies:
        lastFittedProjectApplyId = max([x[1] for x in project_applies])
    if project_likes:
        lastFittedProjectLikeId = max([x[1] for x in project_likes])


@app.get("/recommend/posts/{user_id}")
def recommend_posts_to_user(user_id: str, db: Session = Depends(get_db)):
    try:
        (umap, _, imap, _) = dataset_post.mapping()

        items = [
            x[0] for x in db.execute(
                select(models.Post.post_id)
                .where(models.Post.user_id != user_id)
                .order_by(desc(models.Post.post_id))
            ).fetchmany(size=1000)
        ]
        if len(items) == 0:
            return []

        items = np.array(items)

        scores = lfm_post.predict(umap[user_id], [imap[x] for x in items])

        top_items = items[np.argsort(-scores)]

        return top_items.tolist()

    except KeyError:
        return []


@app.get("/recommend/projects/{user_id}")
def recommend_projects_to_user(user_id: str, db: Session = Depends(get_db)):
    try:
        (umap, _, imap, _) = dataset_project.mapping()

        items = [
            x[0] for x in db.execute(
                select(models.Project.project_id)
                .where(models.Project.leader_id != user_id)
                .order_by(desc(models.Project.project_id))
            ).fetchmany(size=1000)
        ]
        if len(items) == 0:
            return []

        items = np.array(items)

        scores = lfm_project.predict(umap[user_id], [imap[x] for x in items])

        top_items = items[np.argsort(-scores)]

        return top_items.tolist()

    except KeyError:
        return []


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    fit_model(db)
