from init_db import db
from flask_login import UserMixin


class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)

    def __init__(self, nome):
        self.nome = nome

    def id_set(self, novo_id ):
        self.id = novo_id

    def id_get(self):
        return self.id
    
    def nome_set(self, novo_nome):
        self.nome = novo_nome

    def nome_get(self):
        return self.nome
    
    def senha_set(self, novo_senha):
        self.senha = novo_senha

    def senha_get(self):
        return self.senha
    