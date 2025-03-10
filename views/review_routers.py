from enum import Enum
from controller.authentication import get_current_user
from schemas.adminSchema import AdminBase
from schemas.reviewSchema import ReviewBase
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from config.db_connect import get_db
from controller import db_review
from schemas.reviewSchema import ReviewDisplay
from typing import List

from schemas.userSchema import UserBase

router = APIRouter(
    prefix="/reviews",
    tags=['reviews']
)


class UserRating(int, Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5


# Create review
@router.post("/", response_model=ReviewDisplay)
def create_review(request: ReviewBase, user_rating: UserRating, receiver_id: int, creator_id: int, db: Session = Depends(get_db), current_user: UserBase | AdminBase = Depends(get_current_user)):
    return db_review.create_review(db, request, user_rating, receiver_id, creator_id)


@router.post("/{id}")
def upload_photos(id: int, files: list[UploadFile] = File(...), db: Session = Depends(get_db), current_user: UserBase | AdminBase = Depends(get_current_user)):
    return db_review.upload_photos(db, id, files)


@router.delete('/{id}/photos')
def delete_photos(id: int, db: Session = Depends(get_db), current_user: UserBase | AdminBase = Depends(get_current_user)):
    return db_review.delete_photos(db, id)


# Read specific review
@router.get("/{id}", response_model=ReviewDisplay)
def get_review(id: int, db: Session = Depends(get_db), current_user: UserBase | AdminBase = Depends(get_current_user)):
    return db_review.get_review(db, id)


# Read all reviews
@router.get("/", response_model=List[ReviewDisplay])
def get_reviews(creator_id: int = None, receiver_id: int = None, db: Session = Depends(get_db), current_user: UserBase | AdminBase = Depends(get_current_user)):
    return db_review.get_all_reviews(db, creator_id, receiver_id)


# Update review
@router.put('/{id}')
def update_review(id: int, request: ReviewBase, receiver_id: int, user_rating: UserRating, creator_id: int, db: Session = Depends(get_db), current_user: UserBase | AdminBase = Depends(get_current_user)):
    return db_review.update_review(db, id, request, user_rating, creator_id, receiver_id)


# Delete review
@router.delete('/{id}')
def delete_review(id: int, creator_id: int, db: Session = Depends(get_db), current_user: UserBase | AdminBase = Depends(get_current_user)):
    return db_review.delete_review(db, id, creator_id)
