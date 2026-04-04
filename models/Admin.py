from init_db import db
from flask_login import UserMixin

class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)

    def __init__(self, login, senha):
        self.login = login
        self.senha = senha

    def id_set(self, novo_id ):
        self.id = novo_id

    def id_get(self):
        return self.id
    
    def login_set(self, novo_login):
        self.login = novo_login

    def login_get(self):
        return self.login
    
    def senha_set(self, novo_senha):
        self.senha = novo_senha

    def senha_get(self):
        return self.senha
    
    def get_id(self):
        return f"admin-{self.id}"