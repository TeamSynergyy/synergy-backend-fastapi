from fastapi import Depends, FastAPI, HTTPException
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


def get_new_interactions(db: Session = Depends(get_db)):
    creates = crud.get_new_creates(db, lastFittedCreatedId)
    commented = crud.get_new_commented(db, lastFittedCommentId)
    liked = crud.get_new_liked(db, lastFittedLikeId)
    return (creates, commented, liked)


def fit_dataset(creates, commented, liked):
    users = set(list(map(lambda x: x[0], creates + commented + liked)))
    items = set(list(map(lambda x: x[1], creates + commented + liked)))

    dataset.fit_partial(users, items)

    num_users, num_items = dataset.interactions_shape()
    print('Num users {}, num_items {}.'.format(num_users, num_items))


@app.get("/fit_model/")
def fit_model(db: Session = Depends(get_db)):
    (creates, commented, liked) = get_new_interactions(db)

    fit_dataset(creates, commented, liked)

    (interactions, _) = dataset.build_interactions(
        creates + commented + liked)

    print(repr(interactions))
    model.fit(interactions, epochs=30)

    global lastFittedCreatedId, lastFittedLikeId, lastFittedCommentId
    if creates:
        lastFittedCreatedId = max([x[1] for x in creates])
    if commented:
        lastFittedCommentId = max([x[1] for x in commented])
    if liked:
        lastFittedLikeId = max([x[1] for x in liked])


@app.get("/recommend/{user_id}")
def recommend_to_user(user_id: str, offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        (umap, _, imap, _) = dataset.mapping()

        items = np.array([
            x[0] for x in db.execute(
                select(models.Post.post_id)
                .where(models.Post.user_id != user_id)
                .order_by(desc(models.Post.post_id))
            ).fetchmany(size=1000)
        ])

        scores = model.predict(umap[user_id], [imap[x] for x in items])

        top_items = items[np.argsort(-scores)]

        return top_items[offset:offset+limit].tolist()

    except KeyError:
        return []


@app.on_event("startup")
async def startup_event():
    fit_model(db=SessionLocal())
