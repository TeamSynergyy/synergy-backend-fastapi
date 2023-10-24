from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy.sql import select, desc
from . import models, crud
from .database import SessionLocal, engine
from lightfm import LightFM
from lightfm.data import Dataset
import numpy as np

# LightFM
dataset = Dataset()
model = LightFM(loss='warp')

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

lastFittedCreatedId = 0
lastFittedLikeId = 0
lastFittedCommentId = 0


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fit_dataset(creates, comments, likes):
    users = set(list(map(lambda x: x[0], creates + comments + likes)))
    items = set(list(map(lambda x: x[1], creates + comments + likes)))

    dataset.fit_partial(users, items)

    num_users, num_items = dataset.interactions_shape()
    print('Num users {}, num_items {}.'.format(num_users, num_items))


@app.get("/fit_model")
def fit_model(db: Session = Depends(get_db)):
    global lastFittedCreatedId, lastFittedLikeId, lastFittedCommentId

    creates = crud.get_new_creates(db, lastFittedCreatedId)
    comments = crud.get_new_comments(db, lastFittedCommentId)
    likes = crud.get_new_likes(db, lastFittedLikeId)

    fit_dataset(creates, comments, likes)

    (interactions, _) = dataset.build_interactions(
        creates + comments + likes)

    print(repr(interactions))
    model.fit(interactions, epochs=30)

    if creates:
        lastFittedCreatedId = max([x[1] for x in creates])
    if comments:
        lastFittedCommentId = max([x[1] for x in comments])
    if likes:
        lastFittedLikeId = max([x[1] for x in likes])


@app.get("/recommend/{user_id}")
def recommend_to_user(user_id: str, db: Session = Depends(get_db)):
    try:
        (umap, _, imap, _) = dataset.mapping()

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

        scores = model.predict(umap[user_id], [imap[x] for x in items])

        top_items = items[np.argsort(-scores)]

        return top_items.tolist()

    except KeyError:
        return []


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    fit_model(db)
