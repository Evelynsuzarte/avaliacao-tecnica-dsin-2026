from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

        from models.Admin import Admin
        from models.Cliente import Cliente
        from models.Servico import Servico
        from models.Agendamento import Agendamento


        if not Admin.query.filter_by(login='admin').first():   #adicionando admin
            admin_padrao = Admin('admin','1234')
            db.session.add(admin_padrao)
            db.session.commit()

        if not Cliente.query.first():
            cliente1 = Cliente('João Silva','123')  #id 1
            cliente2 = Cliente('Maria Souza','123') #id 2
            cliente3 = Cliente('Ana Maria','123')   #id 3
            db.session.add_all([cliente1, cliente2, cliente3])
            db.session.commit()

        if not Servico.query.first():
            servico1 = Servico('Corte de cabelo','30') #id 1
            servico2 = Servico('Manicure','25')        #id 2
            servico3 = Servico('Pedicure','35')        #id 3
            servico4 = Servico('Progressiva','230')    #id 4
            db.session.add_all([servico1, servico2, servico3, servico4])
            db.session.commit()

        if not Agendamento.query.first():
            agendamento1 = Agendamento(1, 1, "2026-04-13", "10:00", 'nao', 'agendado')         #id 1
            agendamento2 = Agendamento(1, 2, "2026-04-15", "12:00", 'nao', 'agendado')         #id 2
            agendamento3 = Agendamento(2, 3, "2026-04-05", "09:30", 'sim', 'agendado')         #id 3
            agendamento4 = Agendamento(3, 2, "2026-04-10", "15:20", 'sim', 'agendado')         #id 4
            db.session.add_all([agendamento1, agendamento2, agendamento3, agendamento4])
            db.session.commit()



