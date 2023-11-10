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


def flatten(l):
    return [item for sublist in l for item in sublist]


def fit_dataset_post(post_creates, post_comments, post_likes, users):
    posts_ids = set(
        list(map(lambda x: x[1], post_creates + post_comments + post_likes)))

    user_features = set(
        (list(flatten(map(lambda x: x[1], create_user_features_base(users))))))

    user_ids = [x.user_id for x in users]

    dataset_post.fit_partial(user_ids, posts_ids, user_features)

    num_users_post, num_posts = dataset_post.interactions_shape()
    print('Num users_post {}, num_posts {}.'.format(num_users_post, num_posts))


def fit_dataset_project(project_creates, project_applies, project_likes, users):
    projects_ids = set(
        list(map(lambda x: x[1], project_creates + project_likes + project_applies)))

    user_features = set(
        (list(flatten(map(lambda x: x[1], create_user_features_base(users))))))

    user_ids = [x.user_id for x in users]

    dataset_project.fit_partial(user_ids, projects_ids, user_features)

    num_users_project, num_projects = dataset_project.interactions_shape()
    print('Num users_project {}, num_projects {}.'.format(
        num_users_project, num_projects))


def create_user_features_base(users):
    user_features_base = []
    for user in users:
        features = []

        if user.organization:
            features.append(f"organization:{user.organization}")
        if user.major:
            features.append(f"major:{user.major}")
        if user.minor:
            features.append(f"minor:{user.minor}")
        if user.interest_areas:
            features.append(f"interest_areas:{user.interest_areas}")
        if user.skills:
            features.append(f"skills:{user.skills}")
        # if user.interest_areas:
        #     features.extend([f"interestArea:{area.name}" for area in user.interest_areas if area.name])
        # if user.skills:
        #     features.extend([f"skill:{skill.name}" for skill in user.skills if skill.name])

        user_features_base.append((user.user_id, features))

    return user_features_base


@app.get("/fit_model")
def fit_model(db: Session = Depends(get_db)):
    try:
        global lastFittedPostCreateId, lastFittedPostLikeId, lastFittedPostCommentId

        post_creates = crud.get_new_post_creates(db, lastFittedPostCreateId)
        post_comments = crud.get_new_post_comments(db, lastFittedPostCommentId)
        post_likes = crud.get_new_post_likes(db, lastFittedPostLikeId)

        users = crud.get_users(db)

        fit_dataset_post(post_creates, post_comments, post_likes,
                         users)

        (post_interactions, _) = dataset_post.build_interactions(
            post_creates + post_comments + post_likes)

        user_features_post = dataset_post.build_user_features(
            create_user_features_base(users))

        print(repr(post_interactions))

        lfm_post.fit_partial(
            post_interactions, user_features=user_features_post, epochs=30)

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

        fit_dataset_project(project_creates, project_applies,
                            project_likes, users)

        (project_interactions, _) = dataset_project.build_interactions(
            project_creates + project_applies + project_likes)

        user_features_project = dataset_project.build_user_features(
            create_user_features_base(users))

        print(repr(project_interactions))
        lfm_project.fit_partial(project_interactions,
                                user_features=user_features_project, epochs=30)

        if project_creates:
            lastFittedProjectCreateId = max([x[1] for x in project_creates])
        if project_applies:
            lastFittedProjectApplyId = max([x[1] for x in project_applies])
        if project_likes:
            lastFittedProjectLikeId = max([x[1] for x in project_likes])

        return "success"
    except:
        return "error"


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
    except:
        return "error"


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
    except:
        return "error"


@app.get("/users/similar/{user_id}")
def similar_users(user_id: str, db: Session = Depends(get_db)):
    from sklearn.metrics.pairwise import cosine_similarity

    try:
        (umap, _, _, _) = dataset_post.mapping()

        users = crud.get_users(db)
        user_features_post = dataset_post.build_user_features(
            create_user_features_base(users))

        _, user_embeddings = lfm_post.get_user_representations(
            user_features_post)

        target_user_embedding = user_embeddings[umap[user_id]].reshape(1, -1)

        similarities = cosine_similarity(
            target_user_embedding, user_embeddings)

        similarities[0, umap[user_id]] = -1

        # 상위 10개 유저
        most_similar_user_indices = np.argsort(-similarities[0])[:10]

        reverse_umap = {v: k for k, v in umap.items()}
        most_similar_user_ids = [reverse_umap[idx]
                                 for idx in most_similar_user_indices]

        return most_similar_user_ids

    except:
        return "error"


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    fit_model(db)
