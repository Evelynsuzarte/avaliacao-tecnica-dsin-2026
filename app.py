from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.Cliente import Cliente
from models.Servico import Servico
from models.Agendamento import Agendamento
from models.Admin import Admin
from init_db import init_db, db
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date, datetime, timedelta

app = Flask(__name__)

# configuração do banco de dados ------------------------------------------------------------

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'dev'
app.config['TEMPLATES_AUTO_RELOAD'] = True

init_db(app)


# login e logout ------------------------------------------------------------
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    tipo, id_str = user_id.split("-")
    user_id = int(id_str)
    if tipo == "admin":
        return Admin.query.get(user_id)
    elif tipo == "usuario":
        return Cliente.query.get(user_id)


@app.route('/', methods=['GET', 'POST'])
def login():
    mensagem = ''

    if request.method == 'POST':
        login_digitado = request.form.get('login')
        senha_digitada = request.form.get('senha')
        tipo = request.form.get('tipo')

        if tipo == 'admin': 
            admin: Admin = Admin.query.filter_by(login=login_digitado).first()

            if admin and admin.senha_get() == senha_digitada:
                login_user(admin)
                return render_template('painel.html', mensagem="Login realizado com sucesso!")
            else:
                mensagem = "Login ou senha incorretos."

        elif tipo == 'usuario':
            cliente: Cliente = Cliente.query.filter_by(login=login_digitado).first()

            if cliente and cliente.senha_get() == senha_digitada:
                login_user(cliente)
                return render_template('painel.html', mensagem="Login realizado com sucesso!")
            else:
                mensagem = "Login ou senha incorretos."

    return render_template('login.html', mensagem_login=mensagem)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/painel')
@login_required
def painel():
    return render_template('painel.html', nome=current_user.login)


# endpoints principais ------------------------------------------------------------------------

@app.route('/adicionar_cliente', methods=['GET', 'POST'])
def adicionar_cliente():
    if current_user.is_authenticated and not isinstance(current_user, Admin):
        logout_user()
        session.clear()

    mensagem = ''
    if request.method == 'POST':
        nome_digitado = request.form.get('login')
        senha_digitada = request.form.get('senha')

        if nome_digitado and senha_digitada:
            cliente_busca = Cliente.query.filter_by(login=nome_digitado).first()
            if not cliente_busca:
                novo_cliente = Cliente(nome_digitado, senha_digitada)
                db.session.add(novo_cliente)
                db.session.commit()
                mensagem = f"Cliente {novo_cliente.login_get()} salvo com sucesso!"
            else:
                mensagem = "Cliente já cadastrado!"

    if current_user.is_authenticated and isinstance(current_user, Admin):
        return render_template('adicionar_cliente.html', mensagem_cadastro=mensagem)
    
    return render_template('login.html', mensagem_cadastro=mensagem)


#apenas admin
@app.route('/adicionar_servicos', methods=['GET', 'POST'])
@login_required
def adicionar_servicos():
    mensagem = ''

    if not isinstance(current_user, Admin):
        return render_template('painel.html', mensagem="Ação não permitida")
    
    if request.method == 'POST':
        nome_digitado = request.form.get('nome')
        preco_digitado = request.form.get('preco')

        if nome_digitado and preco_digitado:
            servico_busca: Servico = Servico.query.filter_by(nome=nome_digitado).first()

            if not servico_busca:
                novo_servico = Servico(nome_digitado, preco_digitado)
                db.session.add(novo_servico)
                db.session.commit()
                mensagem = f"Serviço {novo_servico.nome_get()} salvo com sucesso!"
            else:
                mensagem = f"Serviço já cadastrado no banco de dados!"

    return render_template('adicionar_servicos.html', mensagem=mensagem)


@app.route('/agendar', methods=['GET', 'POST'])
@login_required
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
            sugestao = request.form.get('sugestao') 

            sugestao_data = ''

            if cliente_marcado and servico_marcado and data_marcada and hora_marcado and atendimento_confirmado and status:

                # verifica agendamento na mesma semana
                data_marcada_dt = datetime.strptime(data_marcada, '%Y-%m-%d').date()
                inicio_semana   = data_marcada_dt - timedelta(days=data_marcada_dt.weekday())
                fim_semana      = inicio_semana + timedelta(days=6)

                agendamento_semana = None
                for agendamento in Agendamento.query.filter_by(clienteID=cliente_marcado).all():
                    agendamento: Agendamento
                    data_ag = datetime.strptime(agendamento.data_get(), '%Y-%m-%d').date()
                    if inicio_semana <= data_ag <= fim_semana:
                        agendamento_semana = agendamento
                        break

                # se achou agendamento na semana e o cliente ainda não respondeu
                if agendamento_semana and sugestao is None:
                    sugestao_data = agendamento_semana.data_get()
               
                    mensagem = f"Você já tem um agendamento nessa semana no dia {sugestao_data}. Deseja agendar na mesma data?"
                    return render_template('adicionar_agendamento.html', mensagem=mensagem, sugestao_data=sugestao_data,
                                           cliente_marcado=cliente_marcado, servico_marcado=servico_marcado,
                                           hora_marcado=hora_marcado, status=status, atendimento_confirmado=atendimento_confirmado, 
                                           clientes=Cliente.query.all(), servicos=Servico.query.all())
                    

                # se respondeu 'sim' para a sugestão
                elif sugestao == 'sim' and agendamento_semana:
                    data_marcada = agendamento_semana.data_get()
                    hora_marcado = agendamento_semana.hora_get()

                # cria o agendamento
                novo_agendamento = Agendamento(cliente_marcado, servico_marcado, data_marcada, hora_marcado, atendimento_confirmado, status)
                db.session.add(novo_agendamento)
                db.session.commit()

                cliente: Cliente = Cliente.query.get(cliente_marcado)
                mensagem = f"Agendamento de {cliente.login_get()} feito com sucesso!"

    else:
        return render_template('login.html')
    
    return render_template('adicionar_agendamento.html', mensagem=mensagem, clientes=Cliente.query.all(), servicos=Servico.query.all())


@app.route('/alterar_agendamento', methods=['GET', 'POST'])
@login_required
def alterar_agendamento():
    mensagem = ''
    clientes_lista = {}

    
    if isinstance(current_user, Admin):
        agendamentos : Agendamento = Agendamento.query.all()  
        servicos: Servico = Servico.query.all()
    elif isinstance(current_user, Cliente):
        # Cliente vê apenas os próprios
        cliente_id = current_user.id_get() 
        agendamentos : Agendamento = Agendamento.query.filter_by(clienteID=cliente_id).all()
        servicos: Servico = Servico.query.all()
    
    for ag in agendamentos:
        ag: Agendamento
        c: Cliente = Cliente.query.get(ag.clienteID_get())
        s: Servico = Servico.query.get(ag.servicoID_get())
        clientes_lista[ag.clienteID_get()] = {
            'id'                     : ag.id_get(),
            'cliente'                : c.login_get(),
            'servico'                : s.nome_get(),
            'data'                   : ag.data_get(),
            'hora'                   : ag.hora_get(),
            'status'                 : ag.status_get(),
            'atendimento_confirmado' : ag.atendimento_confirmado_get()
        }


    
    if request.method == 'POST':
        agendamento_id = request.form.get('agendamento_id')

        if agendamento_id:
            agendamento: Agendamento = Agendamento.query.get(agendamento_id)

            if agendamento:
                #se for admin, ele pode ver tudo
                if isinstance(current_user, Admin):
                    novo_servico = request.form.get('servico')
                    nova_data = request.form.get('data')
                    nova_hora = request.form.get('hora')
                    novo_status = request.form.get('status')
                    novo_atend_confirmado = request.form.get('atendimento_confirmado')

                    if novo_servico:
                        agendamento.servicoID_set(novo_servico)
                    if nova_data:
                        agendamento.data_set(nova_data)
                    if nova_hora:
                        agendamento.hora_set(nova_hora)
                    if novo_status:
                        agendamento.status_set(novo_status)
                    if novo_atend_confirmado:
                        agendamento.atendimento_confirmado_set(novo_atend_confirmado)

                    db.session.commit()
                    mensagem = f"Agendamento alterado com sucesso!"

                # cliente pode alterar data se maior que 2 dias
                elif isinstance(current_user, Cliente):
                    novo_servico = request.form.get('servico')
                    nova_data = request.form.get('data')
                    nova_hora = request.form.get('hora')
                    novo_status = 'pendente'
                    novo_atend_confirmado = 'nao'

                    if novo_servico:
                        agendamento.servicoID_set(novo_servico)
                    if nova_hora:
                        agendamento.hora_set(nova_hora)

                    if nova_data :
                        hoje = date.today()
                        data_agendamento = datetime.strptime(nova_data, '%Y-%m-%d').date()
                        dias_restantes = (data_agendamento - hoje).days
                        if dias_restantes > 2:
                            agendamento.data_set(nova_data)
                            agendamento.hora_set(nova_hora)
                            db.session.commit()
                            mensagem = f"Data do agendamento alterada com sucesso!"
                        else:
                            mensagem = "Não é possível alterar com menos de 2 dias de antecedência, ligue no nosso telefone."
            else:
                mensagem = "Agendamento não encontrado."
                
    
    return render_template('alterar_agendamento.html', mensagem=mensagem, agendamentos=agendamentos, servicos=servicos, clientes=clientes_lista)


#apenas admin
@app.route('/confirmar_agendamento', methods=['GET','POST'])
@login_required
def confirmar_agendamento():
    mensagem = ''

    if not isinstance(current_user, Admin):
        return render_template('painel.html', mensagem="Ação não permitida")
    
    if request.method == 'POST':
        agendamentoID = request.form.get('agendamentoID')
        atendimento_confirmado = request.form.get('atendimento_confirmado')

        if agendamentoID and atendimento_confirmado:

            agendamento_alterar: Agendamento = Agendamento.query.get(agendamentoID)
            agendamento_alterar.atendimento_confirmado_set(True)
            db.session.commit()

            cod_cliente = agendamento_alterar.clienteID_get()
            cliente: Cliente = Cliente.query.get(cod_cliente)

        mensagem = f"Agendamento de {cliente.login_get()} confirmado com sucesso!"
    
    return render_template('adicionar_agendamento.html', mensagem=mensagem)



@app.route('/agendamentos', methods=['GET'])
@login_required
def listar_agendamentos_periodo():
    mensagem = ''
    agendamentos_buscados = []

    if isinstance(current_user, Admin):
        agendamentos = Agendamento.query.all()
    elif isinstance(current_user, Cliente):
        agendamentos = Agendamento.query.filter_by(clienteID=current_user.id_get()).all()
    else:
        return redirect(url_for('login'))

    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    if data_inicio and data_fim:
        data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d").date()
    else:
        data_inicio_dt = data_fim_dt = None

    for agendamento in agendamentos:
        agendamento: Agendamento

        # filtra por período
        if data_inicio_dt and data_fim_dt:
            data_agendamento_dt = datetime.strptime(agendamento.data_get(), "%Y-%m-%d").date()
            if not (data_inicio_dt <= data_agendamento_dt <= data_fim_dt):
                continue

        cliente: Cliente = Cliente.query.get(agendamento.clienteID_get())
        servico: Servico = Servico.query.get(agendamento.servicoID_get())

        agendamentos_buscados.append({
            'id': agendamento.id_get(),
            'cliente': cliente.login_get(),
            'servico': servico.nome_get(),
            'data': agendamento.data_get(),
            'hora': agendamento.hora_get(),
            'status': agendamento.status_get(),
            'atendimento_confirmado': agendamento.atendimento_confirmado_get()
        })

    if not agendamentos_buscados:
        if isinstance(current_user, Admin):
            mensagem = "Nenhum agendamento encontrado no período."
        else:
            mensagem = "Nenhum agendamento encontrado para você neste período."

    return render_template('listagem_agendamento.html', agendamentos=agendamentos_buscados, mensagem=mensagem)



#apenas admin
@app.route('/cancelar_agendamento', methods=['GET', 'POST'])
@login_required
def cancelar_agendamento():
    mensagem = ''

    if not isinstance(current_user, Admin):
        return render_template('painel.html', mensagem="Ação não permitida")
    
    if request.method == 'POST':
        agendamentoID = request.form.get('agendamentoID')

        if agendamentoID:
            agendamento: Agendamento = Agendamento.query.get(agendamentoID)

            if agendamento:
                cliente: Cliente = Cliente.query.get(agendamento.clienteID_get())
                nome_cliente = cliente.login_get()
                db.session.delete(agendamento)
                db.session.commit()
                mensagem = f"Agendamento de {nome_cliente} cancelado com sucesso!"
            else:
                mensagem = "Agendamento não encontrado."


    return render_template('cancelar_agendamento.html', mensagem=mensagem, agendamentos=Agendamento.query.all(), clientes=Cliente.query.all(), servicos=Servico.query.all())



if __name__ == "__main__":
    app.run()
