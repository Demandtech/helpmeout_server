from fastapi import HTTPException, status, BackgroundTasks
import asyncio
from moviepy.editor import VideoFileClip
from PIL import Image
from passlib.context import CryptContext
from .config import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import subprocess
from . import models, config
import re
from jinja2 import Environment, FileSystemLoader


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

smtp_server = settings.smtp_server
smtp_port = settings.smtp_port
smtp_username = settings.smtp_username
smtp_password = settings.smtp_password

sender_email = settings.sender_email


def render_template(template_name, **context):
    env = Environment(loader=FileSystemLoader('templates/'))
    template = env.get_template(template_name)
    return template.render(context)


async def hash(password):
    return pwd_context.hash(password)


def verify(plain_password, hash_password):
    return pwd_context.verify(plain_password, hash_password)


async def send_verification_email(user_email, otp_code, subject):

    subject = subject
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = subject

    template_name = 'verification.html'

    email_body = render_template(
        template_name, otp_code=otp_code, domain=config.settings.domain)
    msg.attach(MIMEText(email_body, 'html'))
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, user_email, msg.as_string())
            print("Email successfully sent")
    except Exception as e:
        print(f"Email sending failed:  {str(e)}")


async def send_confirmation_email(user_email, link, subject):
    subject = subject
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = subject

    template_name = 'confirmation.html'

    email_body = render_template(
        template_name, link=link, domain=config.settings.domain)
    msg.attach(MIMEText(email_body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, user_email, msg.as_string())
            print("Email Sent Successfully")
    except Exception as e:
        print(f"Email sending failed:  {str(e)}")


async def convert_to_mp4(video_path_mp4, decoded_blob):
    try:
        return subprocess.run([
            '/Users/demandbtc/ffmpeg/bin/ffmpeg', '-i', 'pipe:0',
            '-c:v', 'libx264', '-c:a', 'aac',
            '-strict', 'experimental', video_path_mp4
        ], input=decoded_blob, check=True)
    except Exception as e:
        print(e)


async def process_video(decoded_blob, video_path_mp4, thumbnail_path, video_id, db):
    try:
        process = await asyncio.create_subprocess_exec(
            '/Users/demandbtc/ffmpeg/bin/ffmpeg',
            '-i', 'pipe:0',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            video_path_mp4,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate(input=decoded_blob)

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, process.args, output=stdout, stderr=stderr)

        duration = await get_video_duration(video_path_mp4)

        await create_thumbnail(video_path_mp4, thumbnail_path)

        await update_video_status(video_id, db, duration)

    except Exception as e:
        print(e)
        await update_video_status(video_id, db, error=str(e))


async def get_video_duration(video_path_mp4):
    video_clip = VideoFileClip(video_path_mp4)
    duration = video_clip.duration
    video_clip.close()
    return duration


async def create_thumbnail(video_path_mp4, thumbnail_path):
    video_clip = VideoFileClip(video_path_mp4)
    thumbnail = video_clip.get_frame(0)
    video_clip.close()

    thumbnail_pil = Image.fromarray(thumbnail)
    thumbnail_pil.save(thumbnail_path)


async def update_video_status(video_id, db, duration=None, error=None):
    video = db.query(models.Video).filter(models.Video.id == video_id).first()

    if duration is not None:
        video.duration = duration
        video.status = 'completed'
    elif error:
        video.status = 'failed'
        print(f"Line 169 {error}")
    db.commit()
    db.refresh(video)


async def send_video(email, video_url):
    print("here")
    subject = "You received a video"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    template_name = 'send_video.html'

    email_body = render_template(
        template_name, video_url=video_url, domain=config.settings.domain)
    msg.attach(MIMEText(email_body, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, email, msg.as_string())
            print("Video Sent Successfully")
    except Exception as e:
        print(f"Video sending failed:  {str(e)}")


def is_strong_password(password: str) -> bool:
    min_length = 8
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special_char = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    return (len(password) >= min_length) and has_uppercase and has_lowercase and has_special_char and has_digit

def is_name_str(name:str)-> bool:
    return re.match("^[a-zA-Z]+$", name)