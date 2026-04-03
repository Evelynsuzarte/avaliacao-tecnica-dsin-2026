from init_db import db

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'

    id = db.Column(db.Integer, primary_key=True)
    clienteID = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    servicoID = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    data = db.Column(db.String(10), nullable=False)
    hora = db.Column(db.String(5), nullable=False)


    def __init__(self, id, clienteID, servicoID, data, hora):
        self.clienteID = clienteID
        self.servicoID = servicoID
        self.data = data
        self.hora = hora

    def id_set(self, novo_id ):
        self.id = novo_id

    def id_get(self ):
        return self.id
    
    def nome_set(self, novo_nome):
        self.nome = novo_nome

    def nome_get(self ):
        return self.nome
    
    def clienteID_set(self, novo_clienteID ):
        self.clienteID = novo_clienteID

    def clienteID_get(self):
        return self.clienteID
    
    def servicoID_set(self, novo_servicoID ):
        self.servicoID = novo_servicoID

    def servicoID_get(self):
        return self.servicoID
    
    def data_set(self, novo_data):
        self.data = novo_data

    def data_get(self):
        return self.data
    
    def hora_set(self, novo_hora):
        self.hora = novo_hora

    def hora_get(self):
        return self.hora