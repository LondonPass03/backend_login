from fastapi import FastAPI, HTTPException, Depends
from fastapi import security as _security
from sqlalchemy.orm import Session
import services, schemas
from typing import List

app = FastAPI()

oauth2_scheme = _security.OAuth2PasswordBearer(tokenUrl="token")


@app.get("/api")
async def root():
    return {"Guardar Gráfica"}


@app.post("/api/users")
async def create_user(user: schemas.UserCreate, db: Session = Depends(services.get_db)):
    db_user = await services.get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already in use")
    user = await services.create_user(user, db)
    return await services.create_token(user)


@app.post("/api/token")
async def generate_token(form_data: _security.OAuth2PasswordRequestForm = Depends(),
                         db: Session = Depends(services.get_db), ):
    user = await services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401, detail="invalid Creadentials")

    return await services.create_token(user)


@app.get("/api/users/me", response_model=schemas.User)
async def get_users(user: schemas.User = Depends(services.get_current_user)):
    return user


@app.post("/api/leads", response_model=schemas.Lead)
async def create_lead(lead: schemas.LeadCreate, user: schemas.User = Depends(services.get_current_user),
                      db: Session = Depends(services.get_db)):
    return await services.create_lead(user=user, db=db, lead=lead)


@app.get("/api/leads", response_model=List[schemas.Lead])
async def get_leads(user: schemas.User = Depends(services.get_current_user),
                    db: Session = Depends(services.get_db)):
    return await services.get_leads(user=user, db=db)


@app.get("/api/leads/{lead_id}", status_code=200)
async def get_lead(lead_id: int, user: schemas.User = Depends(services.get_current_user),
                   db: Session = Depends(services.get_db)):
    return await services.get_lead(lead_id, user, db)


@app.delete("/api/leads/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, user: schemas.User = Depends(services.get_current_user),
                      db: Session = Depends(services.get_db)):
    await services.delete_lead(lead_id, user, db)
    return {"Successfully Deleted"}


@app.put("/api/leads/{lead_id}", status_code=200)
async def update_lead(lead_id: int, lead: schemas.LeadCreate, user: schemas.User = Depends(services.get_current_user),
                      db: Session = Depends(services.get_db)):
    await services.update_lead(lead_id, lead, user, db)
    return {"Successfully Updated"}
