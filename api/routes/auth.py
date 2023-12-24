from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import database, schemas, models, utils, oauth2, config

from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError

router = APIRouter(tags=['Authentication'], prefix='/auth')

oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=config.settings.google_client_id,
    client_secret=config.settings.google_client_secret,
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': config.settings.google_redirect_uri
    },

)


@router.get('/login/google')
async def login_via_google(request: Request):
    # redirect_uri = request.url_for('auth_via_google')
    url = request.url_for('auth_via_google')
    return await oauth.google.authorize_redirect(request, url)


@router.get('/login/callback')
async def auth_via_google(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return e.error
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse('http://localhost:5173/auth')


@router.post('/login', response_model=schemas.Token)
async def login(user_info: OAuth2PasswordRequestForm = Depends(), db: session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_info.username).one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not utils.verify(user_info.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Verify Credentials")

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    response = {"access_token": access_token, "token_type": "bearer"}
    return response
