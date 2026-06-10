import requests
from datetime import datetime
from fastapi import APIRouter, Response, HTTPException, Depends
from google.oauth2 import id_token
from google.auth.transport import requests
from app.config import settings
from app.fastcore.common.constant import MSG
from app.fastcore.db.auth_session import get_auth_master_db
from app.fastcore.user.models import BaseUser
from app.modules.common.utility import is_valid_tmsc_email
from sqlalchemy.orm import Session
from app.fastcore.user.auth import create_access_token, create_refresh_token

router = APIRouter()
    

@router.post("/google", name="view")
def auth_google(data: dict, response: Response, db: Session = Depends(get_auth_master_db)):
    try:
        token = data.get("token")
        if not token:
            raise HTTPException(status_code=400, detail={'code': MSG['400']['code'], 'message': 'Missing token'})
        
        idinfo = id_token.verify_oauth2_token(
            data["token"],
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
         # check email verified
        if not idinfo.get("email_verified"):
            raise HTTPException(status_code=400, detail={'code': MSG['400']['code'], 'message': 'Email not verified'})

        email = idinfo["email"]
        sub = idinfo["sub"]
        
        if not is_valid_tmsc_email(email):
            raise HTTPException(status_code=400, detail={'code': MSG['400']['code'], 'message': 'Invalid email'})
        
        db_user = db.query(BaseUser).filter(BaseUser.email == email).first()
        if not db_user:
            db_user = BaseUser(email=email, phone=None, fullname=idinfo['name'], avatar=idinfo['picture'],
                             is_active=1, department=None, position=1, google_sub=sub, last_login_at=datetime.now(),
                             created_at=datetime.now())
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        else:
            if db_user.is_active != 1:
                raise HTTPException(status_code=401,
                            detail={'code': MSG['401']['code'], 'message': MSG['401']['message']})
            
            if not db_user.avatar and idinfo['picture']:
                db_user.avatar = idinfo['picture']
                
            if not db_user.fullname or (idinfo['name'] and (db_user.fullname != idinfo['name'])):
                db_user.fullname = idinfo['name']
            
            if not db_user.google_sub or (db_user.google_sub != sub):
                db_user.google_sub = sub

        token = create_access_token({'uuid': db_user.id, "sub": db_user.email, 'email': db_user.email, 'phone': db_user.phone, 'fullname': db_user.fullname, 'department': db_user.department, 'position': db_user.position})
        refresh_token = create_refresh_token({'uuid': db_user.id, "sub": db_user.email, 'email': db_user.email, 'phone': db_user.phone, 'fullname': db_user.fullname, 'department': db_user.department, 'position': db_user.position})

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
            domain=".example.com",
            max_age=7 * 24 * 3600
        )
        
        return {"code": MSG['200']['code'], 'message': MSG['200']['message'], "access_token": token}
    except ValueError as e:
        raise HTTPException(status_code=401, detail={'code': MSG['401']['code'], 'message': "Invalid Google token"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail={'code': MSG['500']['code'], 'message': MSG['500']['message'], 'system_message': str(e)})
