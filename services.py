import fastapi as _fastapi
import fastapi.security as _security
import jwt
import pandas as pd
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import datetime as _dt
import json

import database as _database, schemas as _schemas
import models as _models

from conexion.conexiondb import open_connection
import cleanData.Limpieza as cd

oauth2_scheme = _security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = "myjwtsecret"


# Crear las tablas en la base de datos
def create_database():
    _database.Base.metadata.create_all(bind=_database.engine)


# Generador de sesiones de base de datos
def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Obtener usuario por email
async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()


# Crear nuevo usuario
async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    user_obj = _models.User(
        name=user.name,
        phone=user.phone,
        email=user.email,
        hashed_password=_hash.bcrypt.hash(user.hashed_password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


# Autenticar usuario
async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(email, db)
    if not user or not user.verify_password(password):
        return False
    return user


# Crear token JWT
async def create_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)
    token = jwt.encode(user_obj.dict(), JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


# Obtener usuario actual a partir del token
async def get_current_user(db: _orm.Session = _fastapi.Depends(get_db), token: str = _fastapi.Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except:
        raise _fastapi.HTTPException(status_code=401, detail="Email o contraseña no válidos")
    return _schemas.User.from_orm(user)


# Crear nuevo lead
async def create_lead(user: _schemas.User, db: _orm.Session, lead: _schemas.LeadCreate):
    lead_obj = _models.Lead(**lead.dict(), owner_id=user.id)
    db.add(lead_obj)
    db.commit()
    db.refresh(lead_obj)
    return _schemas.Lead.from_orm(lead_obj)


# Obtener todos los leads del usuario
async def get_leads(user: _schemas.User, db: _orm.Session):
    leads = db.query(_models.Lead).filter_by(owner_id=user.id).all()
    return [_schemas.Lead.from_orm(lead) for lead in leads]


# Seleccionar lead específico
async def _lead_selector(lead_id: int, user: _schemas.User, db: _orm.Session):
    lead = db.query(_models.Lead).filter(_models.Lead.owner_id == user.id, _models.Lead.id == lead_id).first()
    if lead is None:
        raise _fastapi.HTTPException(status_code=404, detail="Lead no existe")
    return lead


# Obtener lead específico
async def get_lead(lead_id: int, user: _schemas.User, db: _orm.Session):
    lead = await _lead_selector(lead_id, user, db)
    return _schemas.Lead.from_orm(lead)


# Eliminar lead
async def delete_lead(lead_id: int, user: _schemas.User, db: _orm.Session):
    lead = await _lead_selector(lead_id, user, db)
    db.delete(lead)
    db.commit()


# Actualizar lead
async def update_lead(lead_id: int, lead: _schemas.LeadCreate, user: _schemas.User, db: _orm.Session):
    lead_db = await _lead_selector(lead_id, user, db)
    lead_db.grafica_name = lead.grafica_name
    lead_db.grafica_url = lead.grafica_url
    lead_db.grafica_type = lead.grafica_type
    lead_db.grafica_status = lead.grafica_status
    lead_db.date_last_updated = _dt.datetime.now()
    db.commit()
    db.refresh(lead_db)
    return _schemas.Lead.from_orm(lead_db)


# Actualizar estado de administrador de un usuario
async def update_admin_status(user_id: int, is_admin: bool, db: _orm.Session):
    user = db.query(_models.User).filter(_models.User.id == user_id).first()
    if user is None:
        raise _fastapi.HTTPException(status_code=404, detail="Usuario no encontrado")
    user.is_admin = is_admin
    db.commit()
    db.refresh(user)
    return user


# Obtener usuarios no administradores
async def get_non_admin_users(db: _orm.Session):
    return db.query(_models.User).filter(_models.User.is_admin == False).all()


# Eliminar usuario no administrador
async def delete_non_admin_user(user_id: int, db: _orm.Session):
    user_to_delete = db.query(_models.User).filter(_models.User.id == user_id, _models.User.is_admin == False).first()
    if not user_to_delete:
        return None
    db.delete(user_to_delete)
    db.commit()
    return user_to_delete


# Conectar y limpiar dataframe
def conectar_dfu(consulta: str):
    connection = open_connection()
    with open(f'querys/{consulta}.sql', 'r') as file:
        query = file.read()
    df = pd.read_sql_query(query, connection)
    df = cd.eliminar_columna_con_nulos(df)
    df = cd.eliminar_columnas_vacias(df)
    return df


# Obtener dataframe
async def conectar_df(consulta: str):
    connection = open_connection()
    with open(f'querys/{consulta}.sql', 'r') as file:
        query = file.read()
    if connection:
        try:
            df = pd.read_sql_query(query, connection)
            js = df.to_json(orient="index")
            data = json.loads(js)
            return data
        except Exception as e:
            raise _fastapi.HTTPException(status_code=500, detail=f"Error al ejecutar la consulta SQL: {e}")
    else:
        raise _fastapi.HTTPException(status_code=500, detail="No se pudo establecer conexión a la base de datos.")
