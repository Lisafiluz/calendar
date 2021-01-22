import datetime
import io

from fastapi import APIRouter, Depends, File, Request, UploadFile
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from PIL import Image

from app import config
from app.database.database import get_db
from app.database.models import User, Event
from app.dependencies import MEDIA_PATH, templates


PICTURE_EXTENSION = config.PICTURE_EXTENSION
PICTURE_SIZE = config.AVATAR_SIZE

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    responses={404: {"description": "Not found"}},
)


def get_placeholder_user():
    return User(
        id=1,
        username='new_user',
        email='my@email.po',
        password='1a2s3d4f5g6',
        full_name='My Name'
    )


def get_placeholder_event():
    return Event(
        id=1,
        title="new_event",
        content="content_of_the_event",
        start=datetime.date(2007, 5, 26),
        end=datetime.date(2007, 5, 27),
        owner_id=1
    )


@router.get("/")
async def profile(
        request: Request,
        session=Depends(get_db),
        new_user=Depends(get_placeholder_user),
        new_event=Depends(get_placeholder_event)):

    # Get relevant data from database
    upcouming_events = range(5)
    user = session.query(User).filter_by(id=1).first()
    if not user:
        session.add(new_user)
        session.commit()
        user = session.query(User).filter_by(id=1).first()

    session.close()

    user_events = session.query(Event).filter_by(owner_id=user.id).all()
    if not user_events:
        session.add(new_event)
        session.commit()
        user_events = session.query(Event).filter_by(owner_id=user.id).first()
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "events": upcouming_events
    })


@router.post("/update_user_fullname")
async def update_user_fullname(
        request: Request, session=Depends(get_db)):

    user = session.query(User).filter_by(id=1).first()
    data = await request.form()
    new_fullname = data['fullname']

    # Update database
    user.full_name = new_fullname
    session.commit()

    session.close()

    url = router.url_path_for("profile")
    response = RedirectResponse(url=url, status_code=HTTP_302_FOUND)
    return response


@router.post("/update_user_email")
async def update_user_email(
        request: Request, session=Depends(get_db)):

    user = session.query(User).filter_by(id=1).first()
    data = await request.form()
    new_email = data['email']

    # Update database
    user.email = new_email
    session.commit()

    session.close()

    url = router.url_path_for("profile")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/update_user_description")
async def update_profile(
        request: Request, session=Depends(get_db)):

    user = session.query(User).filter_by(id=1).first()
    data = await request.form()
    new_description = data['description']

    # Update database
    user.description = new_description
    session.commit()

    session.close()

    url = router.url_path_for("profile")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


async def get_current_user():
    user = get_placeholder_user()
    return user


@router.post("/delete_user")
async def delete_user(
        request: Request, session=Depends(get_db), current_user: User = Depends(get_current_user)):
    
    data = await request.form()
    username_confirmation = data['username_confirmation']

    if username_confirmation == current_user.username:
        # Delete all the events of the user
        session.query(Event).filter_by(owner_id=current_user.id).delete()
        session.commit()
        session.close()
        
        # Delete the user
        session.query(User).filter_by(username=current_user.username).delete()
        session.commit()
        session.close()

        url = '/'
        return RedirectResponse(url=url, status_code=HTTP_302_FOUND)
    else:
        url = router.url_path_for("profile")
        return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/upload_user_photo")
async def upload_user_photo(
        file: UploadFile = File(...), session=Depends(get_db)):

    user = session.query(User).filter_by(id=1).first()
    pic = await file.read()

    try:
        # Save to database
        user.avatar = await process_image(pic, user)
        session.commit()

    finally:
        session.close()

        url = router.url_path_for("profile")
        return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


async def process_image(image, user):
    img = Image.open(io.BytesIO(image))
    width, height = img.size
    crop_area = get_image_crop_area(width, height)
    cropped = img.crop(crop_area)
    cropped.thumbnail(PICTURE_SIZE)
    file_name = f"{user.username}{PICTURE_EXTENSION}"
    cropped.save(f"{MEDIA_PATH}/{file_name}")
    return file_name


def get_image_crop_area(width, height):
    if width > height:
        delta = (width - height) // 2
        return (delta, 0, width - delta, height)
    delta = (height - width) // 2
    return (0, delta, width, width + delta)
