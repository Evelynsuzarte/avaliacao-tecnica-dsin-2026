from init_db import db

class Servico(db.Model):
    __tablename__ = 'servicos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)

    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco

    def id_set(self, novo_id ):
        self.id = novo_id

    def id_get(self ):
        return self.id
    
    def nome_set(self, novo_nome ):
        self.nome = novo_nome

    def nome_get(self ):
        return self.nome
    
    def preco_set(self, novo_preco ):
        self.preco = novo_preco

    def preco_get(self ):
        return self.preco
    