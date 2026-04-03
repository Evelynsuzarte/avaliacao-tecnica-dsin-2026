from flask import Flask, render_template, request, redirect, url_for, session, flash
from models.Cliente import Cliente
from models.Servico import Servico
from models.Agendamento import Agendamento
from init_db import init_db, db
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'dev'

init_db(app)

@app.route('/adicionar_cliente', methods=['GET', 'POST'])
def adicionar_cliente():
    mensagem = ''

    if request.method == 'POST':
        nome_digitado = request.form.get('nome')

        if nome_digitado:
            novo_cliente = Cliente(nome_digitado)
            db.session.add(novo_cliente)
            db.session.commit()
            mensagem = f"Cliente {novo_cliente.nome_get()} salvo com sucesso!"

    return render_template('adicionar_cliente.html', mensagem=mensagem)


@app.route('/adicionar_servicos', methods=['GET', 'POST'])
def adicionar_servicos():
    mensagem = ''

    if request.method == 'POST':
        nome_digitado = request.form.get('nome')
        preco_digitado = request.form.get('preco')

        if nome_digitado and preco_digitado:
            novo_servico = Servico(nome_digitado, preco_digitado)
            db.session.add(novo_servico)
            db.session.commit()
            mensagem = f"Serviço {novo_servico.nome_get()} salvo com sucesso!"

    return render_template('adicionar_servicos.html', mensagem=mensagem)


@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    mensagem = ''

    if request.method == 'POST':
        cliente_marcado = request.form.get('cliente')
        servico_marcado = request.form.get('servico')
        data_marcada    = request.form.get('data')
        hora_marcado    = request.form.get('hora')

        if cliente_marcado and servico_marcado and data_marcada and hora_marcado:
            novo_agendamento = Agendamento(cliente_marcado, servico_marcado, data_marcada, hora_marcado)
            db.session.add(novo_agendamento)
            db.session.commit()

            cliente: Cliente = Cliente.query.get(cliente_marcado)
            mensagem = f"Agendamento de {cliente.nome_get()} feito com sucesso!"

    return render_template('agendar.html', mensagem=mensagem)


@app.route('/alterar_agendamento', methods=['GET', 'POST'])
def alterar_agendamento():
    mensagem = ''
    
    if request.method == 'POST':
        agendamento_id = request.form.get('agendamento_id')
        nova_data = request.form.get('data')

        #validando que os valores estao não nulos
        if agendamento_id and nova_data:
            agendamento_alterar: Agendamento = Agendamento.query.get(agendamento_id)
            
            # se encontrou o agendamento
            if agendamento_alterar:
                hoje = date.today().strftime('%d/%m/%Y')
                dias_restantes = agendamento_alterar.data_get() - hoje
            
                #se os dias restantes pra o atendimento for maior ou igual a 2
                if dias_restantes >= 2:
                    agendamento_alterar.data_set(nova_data)
                    db.session.commit()

                    cliente: Cliente = Cliente.query.get(agendamento_alterar.clienteID_get())
                    mensagem = f"Data do agendamento de {cliente.nome_get()} alterada com sucesso!"
                else:
                    mensagem = "Não é possível alterar agendamentos com menos de 2 dias de antecedência, ligue no nosso telefone."

            else:
                mensagem = "Agendamento não encontrado."

    return render_template('alterar_agendamento.html', mensagem=mensagem)



if __name__ == "__main__":
    app.run()
