import datetime as _dt

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash

import database as _database


class User(_database.Base):
    __tablename__ = "Users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    email = _sql.Column(_sql.String, unique=True, index=True)
    hashed_password = _sql.Column(_sql.String)
    name = _sql.Column(_sql.String, index=True)
    phone = _sql.Column(_sql.Integer, index=True)
    is_admin = _sql.Column(_sql.Boolean, default=False)
    leads = _orm.relationship("Lead", back_populates="owner")

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)


class Lead(_database.Base):
    __tablename__ = "Leads"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    grafica_name = _sql.Column(_sql.String, index=True)
    grafica_url = _sql.Column(_sql.String, index=True)
    grafica_type = _sql.Column(_sql.String, index=True)
    date_created = _sql.Column(_sql.DateTime, default=_dt.datetime.now)
    date_last_updated = _sql.Column(_sql.DateTime, default=_dt.datetime.now)
    grafica_status = _sql.Column(_sql.Boolean, index=True)

    owner_id = _sql.Column(_sql.Integer, _sql.ForeignKey("Users.id"))
    owner = _orm.relationship("User", back_populates="leads")
