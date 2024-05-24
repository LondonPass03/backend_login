from typing import List
from fastapi import FastAPI, HTTPException, Depends
from fastapi import security as _security
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import schemas
import services

app = FastAPI()

# Configuración de CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = _security.OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
async def init():
    return {"message": "inline change2"}


@app.get("/api")
async def root():
    return {"message": "Hola api"}


@app.post("/api/users")
async def create_user(user: schemas.UserCreate, db: Session = Depends(services.get_db)):
    db_user = await services.get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya en uso")
    user = await services.create_user(user, db)
    return await services.create_token(user)


@app.post("/api/token")
async def generate_token(form_data: _security.OAuth2PasswordRequestForm = Depends(),
                         db: Session = Depends(services.get_db)):
    user = await services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales no válidas")
    return await services.create_token(user)


@app.get("/api/users/me", response_model=schemas.User)
async def get_current_user(user: schemas.User = Depends(services.get_current_user)):
    return user


@app.post("/api/leads", response_model=schemas.Lead)
async def create_lead(lead: schemas.LeadCreate, user: schemas.User = Depends(services.get_current_user),
                      db: Session = Depends(services.get_db)):
    return await services.create_lead(user=user, db=db, lead=lead)


@app.get("/api/leads", response_model=List[schemas.Lead])
async def get_leads(user: schemas.User = Depends(services.get_current_user), db: Session = Depends(services.get_db)):
    return await services.get_leads(user=user, db=db)


@app.get("/api/leads/{lead_id}", response_model=schemas.Lead)
async def get_lead(lead_id: int, user: schemas.User = Depends(services.get_current_user),
                   db: Session = Depends(services.get_db)):
    return await services.get_lead(lead_id, user, db)


@app.delete("/api/leads/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, user: schemas.User = Depends(services.get_current_user),
                      db: Session = Depends(services.get_db)):
    await services.delete_lead(lead_id, user, db)
    return {"message": "Eliminado exitosamente"}


@app.put("/api/leads/{lead_id}", response_model=schemas.Lead)
async def update_lead(lead_id: int, lead: schemas.LeadCreate, user: schemas.User = Depends(services.get_current_user),
                      db: Session = Depends(services.get_db)):
    updated_lead = await services.update_lead(lead_id, lead, user, db)
    return updated_lead


@app.put("/api/user/{user_id}/admin", response_model=schemas.User)
async def update_admin_rights(user_id: int, is_admin: bool,
                              current_user: schemas.User = Depends(services.get_current_user),
                              db: Session = Depends(services.get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para realizar esta acción")
    updated_user = await services.update_admin_status(user_id, is_admin, db)
    return updated_user


@app.get("/api/users/non_admin", response_model=List[schemas.User])
async def get_non_admin_users(db: Session = Depends(services.get_db),
                              current_user: schemas.User = Depends(services.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para realizar esta acción")
    return await services.get_non_admin_users(db)


@app.delete("/api/users/non_admin/{user_id}", response_model=schemas.User)
async def delete_non_admin_user_route(user_id: int, db: Session = Depends(services.get_db),
                                      current_user: schemas.User = Depends(services.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No tienes permiso para realizar esta acción.")
    deleted_user = await services.delete_non_admin_user(user_id, db)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    return {"message": "Usuario eliminado exitosamente."}


@app.put("/api/user/change_password")
async def change_password(user_id: int, new_password: str, db: Session = Depends(services.get_db),
                          current_user: schemas.User = Depends(services.get_current_user)):
    pass


@app.put("/api/user/change_mail")
async def change_mail(user_id: int, new_email: str, db: Session = Depends(services.get_db),
                      current_user: schemas.User = Depends(services.get_current_user)):
    pass


@app.get("/datos/{query}")
async def read_total_data(query: str):
    try:
        data = await services.conectar_df(query)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))