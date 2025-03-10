from sqlalchemy.orm.session import Session
from schemas.reviewSchema import ReviewBase
from models.Reviews import DbReview
from fastapi import HTTPException, status, File, UploadFile, Form
from sqlalchemy.sql import func
from models.Users import DbUser
from pathlib import Path
from config.pictures_handler import upload_picture

UPLOAD_DIR = Path("reviews_photos")
UPLOAD_DIR.mkdir(exist_ok=True)


def create_review(db: Session, request: ReviewBase, user_rating: int, receiver_id: int, creator_id: int):
    creator = db.query(DbUser).filter(DbUser.id == creator_id).first()
    receiver = db.query(DbUser).filter(DbUser.id == receiver_id).first()
    if not creator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f'None exist user can not create reviews')
    if not receiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f'None exist user can not receive reviews')
    if creator_id == receiver_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail=f'You can not leave review about yourself.')
    if len(request.text_description) >= 300:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text description cannot be more than 300 characters."
        )

    new_review = DbReview(
        rating=user_rating,
        text_description=request.text_description,
        receiver_id=receiver_id,
        creator_id=creator_id
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    reviews_received = db.query(DbReview).filter(DbReview.receiver_id == receiver_id).all()
    reviews_received_count = len(reviews_received)
    ratings = []
    for review in reviews_received:
        ratings.append(review.rating)
    average_rating = round(sum(ratings)/len(reviews_received), 1)
    receiver.average_rating = average_rating
    receiver.reviews_received_count = reviews_received_count
    db.commit()
    db.refresh(receiver)
    return new_review


def get_review(db: Session, id: int):
    review = db.query(DbReview).filter(DbReview.id == id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return review


def get_all_reviews(db: Session, creator_id: int, receiver_id: int):
    review_query = db.query(DbReview)
    if creator_id is not None:
        review_query = review_query.filter(DbReview.creator_id == creator_id)
    if receiver_id is not None:
        review_query = review_query.filter(DbReview.receiver_id == receiver_id)
    return review_query.all()


def update_review(db: Session, id: int, request: ReviewBase, user_rating: int, creator_id: int, receiver_id: int):
    review = db.query(DbReview).filter(DbReview.id == id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if review.creator_id != creator_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail=f'You do not have rights to update this review')
    if len(request.text_description) >= 300:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text description  cannot be more than 300 characters.")
    review.rating = user_rating
    review.text_description = request.text_description
    review.created_at = func.now()
    review.receiver_id = receiver_id   
    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, id: int, creator_id: int):
    review = db.query(DbReview).filter(DbReview.id == id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f'Review with id {id} does not exist.')
    if review.creator_id != creator_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail=f'You do not have rights to delete this review')
    db.delete(review)
    db.commit()


def upload_photos(db: Session, id: int, files: list[UploadFile] = File(...)):
    review = db.query(DbReview).filter(DbReview.id == id).first()
    file_paths = []
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for file in files:
        final_path = upload_picture(UPLOAD_DIR, file)
        file_paths.append(str(final_path))
    if review.photos:
        existing_photos = review.photos.split(",")
        review.photos = ",".join(existing_photos + file_paths)
    else:
        review.photos = ",".join(file_paths)
    db.commit()
    db.refresh(review)
    return review


def delete_photos(db: Session, id: int):
    review = db.query(DbReview).filter(DbReview.id == id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    existing_photos = review.photos.split(",")
    for photo in existing_photos:
        photo_path = Path(photo)
        photo_path.unlink()
    review.photos = None
    db.commit()
    db.refresh(review)
    return review
