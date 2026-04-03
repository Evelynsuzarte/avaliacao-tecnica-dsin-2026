from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.Cliente import Cliente
from models.Servico import Servico
from models.Agendamento import Agendamento
from models.Admin import Admin
from init_db import init_db, db
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date, datetime

app = Flask(__name__)

# configuração do banco de dados ------------------------------------------------------------

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'dev'

init_db(app)


# login e logoff ------------------------------------------------------------
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
    return Cliente.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    mensagem = ''

    if request.method == 'POST':
        login_digitado = request.form.get('login')
        senha_digitada = request.form.get('senha')

        admin: Admin = Admin.query.filter_by(login=login_digitado).first()

        if admin and admin.senha_get() == senha_digitada:
            login_user(admin)

            return redirect(url_for('painel_adm'))
        else:
            mensagem = "Login ou senha incorretos."

    return render_template('login.html', mensagem=mensagem)

@app.route('/login_cliente', methods=['GET', 'POST'])
def login_cliente():
    mensagem = ''

    if request.method == 'POST':
        login_digitado = request.form.get('login')
        senha_digitada = request.form.get('senha')

        cliente: Cliente = Cliente.query.filter_by(login=login_digitado).first()

        if cliente and cliente.senha_get() == senha_digitada:
            login_user(cliente)
            return redirect(url_for('agendar'))
        else:
            mensagem = "Login ou senha incorretos."

    return render_template('login_cliente.html', mensagem=mensagem)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/painel')
@login_required
def painel():
    return render_template('painel.html')


# endpoints principais ------------------------------------------------------------------------

@app.route('/adicionar_cliente', methods=['GET', 'POST'])
def adicionar_cliente():
    mensagem = ''

    if isinstance(current_user, Admin) or isinstance(current_user, Cliente): 
        if request.method == 'POST':
            nome_digitado = request.form.get('nome')
            senha_digitada = request.form.get('senha')

            if nome_digitado and senha_digitada:
                novo_cliente = Cliente(nome_digitado, senha_digitada)
                db.session.add(novo_cliente)
                db.session.commit()
                mensagem = f"Cliente {novo_cliente.nome_get()} salvo com sucesso!"
    else:
        return render_template('login.html')

    return render_template('adicionar_cliente.html', mensagem=mensagem)


@app.route('/adicionar_servicos', methods=['GET', 'POST'])
def adicionar_servicos():
    mensagem = ''

    if isinstance(current_user, Admin): 
        if request.method == 'POST':
            nome_digitado = request.form.get('nome')
            preco_digitado = request.form.get('preco')

            if nome_digitado and preco_digitado:
                novo_servico = Servico(nome_digitado, preco_digitado)
                db.session.add(novo_servico)
                db.session.commit()
                mensagem = f"Serviço {novo_servico.nome_get()} salvo com sucesso!"
    else:
        return render_template('login.html')

    return render_template('adicionar_servicos.html', mensagem=mensagem)


@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    mensagem = ''

    if isinstance(current_user, Admin) or isinstance(current_user, Cliente): 
        if request.method == 'POST':
            cliente_marcado = request.form.get('cliente')
            servico_marcado = request.form.get('servico')
            data_marcada = request.form.get('data')
            hora_marcado = request.form.get('hora')
            atendimento_confirmado = request.form.get('atendimento_confirmado')
            status = request.form.get('status')

            if cliente_marcado and servico_marcado and data_marcada and hora_marcado and atendimento_confirmado and status:
                novo_agendamento = Agendamento(cliente_marcado, servico_marcado, data_marcada, hora_marcado, atendimento_confirmado, status)
                db.session.add(novo_agendamento)
                db.session.commit()

                cliente: Cliente = Cliente.query.get(cliente_marcado)
                mensagem = f"Agendamento de {cliente.nome_get()} feito com sucesso!"
    else:
        return render_template('login.html')
    
    return render_template('agendar.html', mensagem=mensagem)


@app.route('/alterar_agendamento', methods=['GET', 'POST'])
def alterar_agendamento():
    mensagem = ''

    if request.method == 'POST':
        agendamento_id = request.form.get('agendamento_id')

        if agendamento_id:
            agendamento_alterar: Agendamento = Agendamento.query.get(agendamento_id)

            # se o a agendamento existe
            if agendamento_alterar:

                #vista do adm, que pode alterar qualquer coisa
                if isinstance(current_user, Admin):
                    novo_cliente = request.form.get('cliente')
                    novo_servico = request.form.get('servico')
                    nova_data = request.form.get('data')
                    nova_hora = request.form.get('hora')

                    if novo_cliente:
                        agendamento_alterar.clienteID_set(novo_cliente)
                    if novo_servico:
                        agendamento_alterar.servicoID_set(novo_servico)
                    if nova_data:
                        agendamento_alterar.data_set(nova_data)
                    if nova_hora:
                        agendamento_alterar.hora_set(nova_hora)

                    db.session.commit()
                    cliente: Cliente = Cliente.query.get(agendamento_alterar.clienteID_get())
                    mensagem = f"Agendamento de {cliente.nome_get()} alterado com sucesso!"

                #vista do cliente, que pode alterar dentro de até 2 dias
                elif isinstance(current_user, Cliente):
                    nova_data = request.form.get('data')

                    if nova_data:
                        hoje= date.today()
                        data_agendamento= datetime.strptime(agendamento_alterar.data_get(), '%Y-%m-%d').date()
                        dias_restantes = (data_agendamento - hoje).days

                        if dias_restantes >= 2:
                            agendamento_alterar.data_set(nova_data)
                            db.session.commit()

                            cliente: Cliente = Cliente.query.get(agendamento_alterar.clienteID_get())
                            mensagem = f"Data do agendamento de {cliente.nome_get()} alterada com sucesso!"
                        else:
                            mensagem = "Não é possível alterar com menos de 2 dias de antecedência, ligue no nosso telefone."
                else:
                    return redirect(url_for('login_cliente'))

            else:
                mensagem = "Agendamento não encontrado."

    return render_template('alterar_agendamento.html', mensagem=mensagem)


@app.route('/agendamentos', methods=['GET', 'POST'])
def listar_agendamentos_periodo():
    mensagem = ''
    agendamentos_buscados = []

    if isinstance(current_user, Admin):
        if request.method == 'GET':
            for agendamento in Agendamento.query.all():
                agendamento: Agendamento
                cliente: Cliente = Cliente.query.get(agendamento.clienteID_get())
                servico: Servico = Servico.query.get(agendamento.servicoID_get())
                agendamentos_buscados.append({
                    'id': agendamento.id_get(),
                    'cliente': cliente.nome_get(),
                    'servico': servico.nome_get(),
                    'data': agendamento.data_get(),
                    'hora': agendamento.hora_get()
                })

    elif isinstance(current_user, Cliente):
        if request.method == 'POST':
            cliente_id = request.form.get('cliente')
            data_inicial = request.form.get('data_inicial')
            data_final = request.form.get('data_final')

            if cliente_id and data_inicial and data_final:
                for agendamento in Agendamento.query.filter_by(clienteID=cliente_id).all():
                    agendamento: Agendamento
                    data_agendamento = agendamento.data_get()

                    if data_inicial <= data_agendamento <= data_final:
                        cliente: Cliente = Cliente.query.get(agendamento.clienteID_get())
                        servico: Servico = Servico.query.get(agendamento.servicoID_get())
                        agendamentos_buscados.append({
                            'id': agendamento.id_get(),
                            'cliente': cliente.nome_get(),
                            'servico': servico.nome_get(),
                            'preco': servico.preco_get(),
                            'data': agendamento.data_get(),
                            'hora': agendamento.hora_get()
                        })

            mensagem = "Agendamentos encontrados." 
                
            if not agendamentos_buscados: 
                mensagem = "Nenhum agendamento encontrado no período."

    else:
        return redirect(url_for('login_cliente'))

    return render_template('agendamentos.html', agendamentos=agendamentos_buscados, mensagem=mensagem)

if __name__ == "__main__":
    app.run()
