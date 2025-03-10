from pydantic import BaseModel


# User inside ReviewDisplay
class User(BaseModel):
    id: int
    user_name: str
    class Config():
        orm_mode = True


class ReviewBase(BaseModel):
    text_description: str | None = None


class ReviewDisplay(BaseModel):
    id: int
    rating: int
    text_description: str
    creator_id: int
    receiver_id: int
    photos: str | None = ""
    class Config():
        orm_mode = True
