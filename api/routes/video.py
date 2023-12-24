from .. import models, database, schemas, config, oauth2, utils
from fastapi import status, HTTPException, Depends, APIRouter, BackgroundTasks
from sqlalchemy.exc import SQLAlchemyError
import os
import base64
from sqlalchemy import func
import logging
import random
from sqlalchemy.orm import session
from PIL import Image
from moviepy.editor import VideoFileClip
from typing import List, Optional
import subprocess
import uuid


router = APIRouter(
    prefix="/videos",
    tags=['Videos']
)


@router.post('/new', status_code=status.HTTP_201_CREATED)
async def new_video(payload: schemas.NewVideo, background_tasks: BackgroundTasks, db: session = Depends(database.get_db)):
    static_dir = './static/'

    videos_dir = os.path.join(static_dir, 'videos')
    thumbnails_dir = os.path.join(static_dir, 'thumbnails')

    blob_id = uuid.uuid4()
    blob_id = str(blob_id).split('-')[0].upper()

    if not payload.blob_base:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")

    video_name = f"Untitled_Video_{blob_id}"
    thumbnail_name = f"Untitled_thumbnail_{blob_id}"
    video_path_mp4 = os.path.join(videos_dir, f"{video_name}.mp4")
    thumbnail_path = os.path.join(
        thumbnails_dir, f"{thumbnail_name}_thumbnail.jpeg")

    decoded_blob = base64.b64decode(payload.blob_base)

    base_url = config.settings.base_url
    video_url = f"{base_url}videos/{video_name}.mp4"
    thumbnail_url = f"{base_url}thumbnails/{thumbnail_name}_thumbnail.jpeg"

    new_video = models.Video(
        video_url=video_url, title=video_name, blob_id=blob_id, thumbnail_url=thumbnail_url, status='proccessing', video_path=video_path_mp4)

    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    background_tasks.add_task(utils.process_video, decoded_blob,
                              video_path_mp4, thumbnail_path, new_video.id, db)

    return {"data": {"message": "Success", "blob_id": blob_id}}


@router.get('/single/{blob_id}', response_model=schemas.Video)
def single_video(blob_id: str, db: session = Depends(database.get_db)):
    video = db.query(models.Video).filter(
        models.Video.blob_id == blob_id).first()
    try:
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        return video
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Video not found")


@router.get('/')
def get_user_videos(db: session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ''):
    user_id = current_user.id

    videos = db.query(models.Video).filter(
        models.Video.user_id == user_id, func.lower(models.Video.title).contains(func.lower(search.lower()))).order_by(models.Video.id.desc()).limit(limit).offset(skip).all()

    if not videos:
        return {videos: []}

    total_video_count = db.query(models.Video).filter(
        models.Video.user_id == user_id).count()

    if search:
        total_video_count = db.query(models.Video).filter(models.Video.user_id == user_id, func.lower(
            models.Video.title).contains(func.lower(search.lower()))).count()

    return {"videos": videos, "total_video": total_video_count}


@router.post('/send')
async def send_video(payload: schemas.SendVideo, db: session = Depends(database.get_db)):
    video = db.query(models.Video).filter(
        models.Video.id == payload.id).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="video not found")

    try:
        if payload.email and video:
            await utils.send_video(payload.email, video.video_url)

        if video.status != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="video is not ready to be sent")

        return {"message": f"Video sent to {payload.email}"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send video {e}")


@router.get('/check/{id}')
def check_status(id: int, db: session = Depends(database.get_db)):
    try:
        video = db.query(models.Video).get(id)

        if video is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

        return {"status": video.status}
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put('/save/{id}', status_code=status.HTTP_202_ACCEPTED)
def save_video(id: int, db: session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user)):
    try:
        video = db.query(models.Video).get(id)
        user_id = current_user.id

        if video is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        if video.user_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Video is saved already!")

        video.user_id = user_id
        db.commit()
        db.refresh(video)
        return {"message": "Video saved successfully!"}
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error occurred while checking video status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
