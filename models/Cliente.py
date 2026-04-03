from init_db import db

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

    def __init__(self, nome):
        self.nome = nome

    def id_set(self, novo_id ):
        self.id = novo_id

    def id_get(self ):
        return self.id
    
    def nome_set(self, novo_nome):
        self.nome = novo_nome

    def nome_get(self ):
        return self.nome
    