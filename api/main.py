from fastapi import FastAPI
from api.routes import video, user, auth
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


from starlette.middleware.sessions import SessionMiddleware

origins = [
    "http://localhost:5173",
    "http://localhost:8000"
]



app = FastAPI()

app.include_router(video.router)
app.include_router(user.router)
app.include_router(auth.router)

app.mount('/videos', StaticFiles(directory='./static/videos'), name='videos')

app.mount('/thumbnails', StaticFiles(directory='./static/thumbnails'),
          name='thumbnails')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.add_middleware(
    SessionMiddleware,
    secret_key="random string"
)


@app.get('/')
def root():
    return {"message": "Welcome Helpme Server 😁"}
