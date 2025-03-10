from config.Hash import Hash
from sqlalchemy.orm.session import Session
from config.email_confirmation import send_verification_email, generate_email_token, verify_email_token
from schemas.userSchema import UserBase, userDisplay
from models.Users import DbUser
from fastapi.responses import JSONResponse
import re
from fastapi import HTTPException, status, File, UploadFile
from pathlib import Path
from config.pictures_handler import upload_picture
from typing import List


def create_user(db: Session, request: UserBase):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if not re.match(email_regex, request.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use a valid email type, example ***@gmail.com"
        )
    
    if len(request.about) >= 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="About section cannot be more than 50 characters!."
        )
    existing_user = db.query(DbUser).filter(DbUser.email == request.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists. Please choose a different email!."
        )
    new_user = DbUser(
        user_name = request.username,
        email = request.email,
        password = Hash.bcrypt(request.password),
        about = request.about,
        phone_number = request.phone_number,
        avatar="avatars/default_avatar.jpg"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = generate_email_token(request.email)
    send_verification_email(request.email, token)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Account has been created!, Please Log in!"}
    )


def verify_email(token: str, db: Session):
    email = verify_email_token(token)
    user = db.query(DbUser).filter(DbUser.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.is_verified = True
    db.commit()
    return "You email confirmed. Now you can log in and enjoy HRIN app"


UPLOAD_DIR = Path("avatars")
UPLOAD_DIR.mkdir(exist_ok=True)


def upload_avatar(db: Session, id: int, file: UploadFile = File(...)):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    old_avatar_path = Path(user.avatar)
    if old_avatar_path.exists() and old_avatar_path != Path("avatars/default_avatar.jpg"):
        old_avatar_path.unlink()
    final_path = upload_picture(UPLOAD_DIR, file)
    user.avatar = str(final_path)
    db.commit()
    db.refresh(user)
    return user


def delete_avatar(db: Session, id: int):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    if not user:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f'User with id {id} is not exist!')
    avatar_path = Path(user.avatar)
    if avatar_path == Path("avatars/default_avatar.jpg"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'You can not delete default avatar!')
    avatar_path.unlink()
    user.avatar = "avatars/default_avatar.jpg"
    db.commit()
    db.refresh(user)
    return user



def get_all_users(db:Session)-> List[userDisplay]:
    all_users = db.query(DbUser).all()
    if not all_users:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f'there are no users found!')
    return all_users


def get_user_by_id(db: Session, id: int):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )
       
    return user


def update_user(db: Session, id:int, request: UserBase):
    if len(request.about) >= 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="About section cannot be more than 50 characters!."
        )
    user = db.query(DbUser).filter(DbUser.id == id).first()

    if not user:
         raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                             detail = f'user with id {id} is not exist!')
    
    if user.id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You do not have rights to update this user'
        )
    user.user_name = request.username
    user.email = request.email
    user.password = Hash.bcrypt(request.password)
    user.about = request.about
    user.phone_number = request.phone_number
    db.commit()
    db.refresh(user)
    return 'user information has been updated successfully!'

def delete_user(db: Session, id: int):
    user = db.query(DbUser).filter(DbUser.id == id).first()
    if not user:
         raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                             detail = f'user with id {id} is not exist!')
    db.delete(user)
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": "User account has been deleted!"}
    )