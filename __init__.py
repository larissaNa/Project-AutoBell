
from flask import Flask, jsonify, render_template, session, request, redirect, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from sqlalchemy.inspection import inspect
from datetime import time, datetime
import time
import hashlib
from .config import app,db,engine
from .models.horarios import Horarios
from .models.usuarios import Usuarios
from .models.ativacoes import Ativacoes
from .models.diasdasemana import DiasDaSemana
from .models.usuarios import Usuarios
import requests



app.secret_key = "user04"
url = "http://ricardosekeff.digital:9000/api/v1/pessoa"


@app.route('/api/horarios', methods=["GET"])
def retornar_horarios():
   matricula = request.args.get('matricula')
   senha = request.args.get('senha')
   token = request.args.get('token')

   if not matricula or not senha or not token:
      return jsonify({"error": "Credenciais incompletas"}), 400

   usuario = checagem_de_usuario(matricula, senha)
   checagem_token = checagem_de_token(token)

   if usuario and checagem_token:
      lista_ativacoes = pegar_ativacoes()
   else:
      lista_ativacoes = {"error": "Credenciais inválidas"}

   return jsonify(lista_ativacoes)
    
def create_tables():
   if not inspect(db.engine).has_table('Usuarios'):
      db.create_all()
      print("tabelas criadas com sucesso")

      senha = "123456"
      senha_hash = hashlib.sha256(senha.encode()).hexdigest()
      email_admin = "joao.exemplo@gmail.com"
      email_comum = "usuario@gmail.com"

      usuario_comum = Usuarios(matricula = "user", senha = senha_hash, email = email_comum, admin = False)
      db.session.add(usuario_comum)
      db.session.commit()
      db.session.close()

      admin = Usuarios(matricula = "admin", senha = senha_hash, email = email_admin, admin = True)
      db.session.add(admin)
      db.session.commit()
      db.session.close()

      usuario = db.session.query(Usuarios).filter_by(matricula = "admin").first()

      domingo = DiasDaSemana(nome = "domingo", abreviacao = "DOM", numero = 0,id_cadastro = usuario.id )
      segunda = DiasDaSemana(nome = "segunda", abreviacao = "SEG", numero = 1,id_cadastro = usuario.id )
      terca   = DiasDaSemana(nome = "terça", abreviacao = "TER", numero = 2,id_cadastro = usuario.id )
      quarta  = DiasDaSemana(nome = "quarta", abreviacao = "QUA", numero = 3,id_cadastro = usuario.id )
      quinta  = DiasDaSemana(nome = "quinta", abreviacao = "QUI", numero = 4,id_cadastro = usuario.id )
      sexta   = DiasDaSemana(nome = "sexta", abreviacao = "SEX", numero = 5,id_cadastro = usuario.id )
      sabado  = DiasDaSemana(nome = "sábado", abreviacao = "SAB", numero = 6,id_cadastro = usuario.id )
      db.session.add(domingo)
      db.session.add(segunda)
      db.session.add(terca)
      db.session.add(quarta)
      db.session.add(quinta)
      db.session.add(sexta)
      db.session.add(sabado)
      db.session.commit()
      db.session.close()
      
with app.app_context():
      create_tables()
      
@app.route("/", methods= ["GET","POST"])
def login():
   logged_in = session.get('logged_in', False)
   mensagens = get_flashed_messages()
   print(mensagens)

   if "logged_in" in session:
         return redirect(url_for('tela_principal'))
   
   if request.method == "POST":
      matricula = request.form['matricula']
      senha = request.form['senha']
      usuario = checagem_de_usuario(matricula,senha)
      if usuario:
         session['logged_in'] = True
         session['usuario.id'] = usuario.id
         session['admin'] = usuario.admin
         return redirect(url_for('tela_principal'))
      else:
         flash("matricula ou senha invalida", "info")
         return redirect(url_for('login'))
   return render_template('login.html',mensagens=mensagens,logged_in=logged_in)

@app.route('/cadastro_horarios', methods= ["GET","POST"])
def cadastro_horarios():
    admin = session.get('admin', False)
    logged_in = session.get('logged_in', False)
    dados = tabela()

    if (request.method == "POST") :
         tipo = request.form['tipo']
         print("tipo",tipo)

         if (tipo == "cadastrar_horario"):
            horario = request.form['input_horario']
            dias_semana = request.form.getlist('dia_semana')
            horario_id = ""
            print("até aqui")


            if ":" in horario:
               hora,minuto = map(int, horario.split(":"))
            else:
               flash("Formato de horário inválido")
            
            horario_existente = checagem_horario(hora,minuto)

            if (horario_existente == False):
               adicionar_horario(hora,minuto)

            horario_relacionamento = pegar_horario(hora=hora,minuto=minuto)
            horario_relacionamento_id = horario_relacionamento.id

            for dia in dias_semana:
               diaSemana = db.session.query(DiasDaSemana).filter_by(nome = dia).first()
               diaSemana_id = diaSemana.id
               checagem = checagem_ativacao(horario_relacionamento_id, diaSemana_id)
      
         
         if (tipo == "remover_horario"):
            diaSemanaNumero = request.form['diaSemana']
            horario = request.form['horario']

            print("dia",diaSemanaNumero)

            if ":" in horario:
               hora,minuto = map(int, horario.split(":"))
            else:
               flash("Formato de horário inválido")

            horario = db.session.query(Horarios).filter_by(hora=hora, minuto=minuto).first()
            diaSemana = db.session.query(DiasDaSemana).filter_by(numero=diaSemanaNumero).first()
            ativacao = db.session.query(Ativacoes).filter_by(id_semana=diaSemana.id, id_horario=horario.id).first()

            if (ativacao):
               db.session.delete(ativacao)
               db.session.commit()
               db.session.close()
            else:
               flash("horário inexistente")

         return redirect(url_for('cadastro_horarios'))   
            
    return render_template('cadastro_horarios.html', logged_in=logged_in,admin=admin,dados=dados)

@app.route("/logout")
def logout():
   logged_in = session.get('logged_in', False)
   if (logged_in):
      session.pop('logged_in', None)
      session.pop('usuario.id', None)
      session.pop('admin', None)
      flash("Sua sessão foi finalizada com sucesso", "info")
   return redirect(url_for('login'))


@app.route("/cadastro_usuario", methods = ["GET","POST"])
def cadastro_usuario():
   admin = session.get('admin', False)
   logged_in = session.get('logged_in', False)
   if (admin == True):
      pessoa = requests.get(url)
      pessoa = pessoa.json()
      email = pessoa["email"]
      if request.method == "POST":
         email = request.form['email']
         matriculaUsuario = request.form["matricula"]
         senha= request.form["senha"]
         confirmar_senha = request.form["confirmar_senha"]

         usuario = pegar_usuario(matricula=matriculaUsuario)
         if usuario is not None:
            flash ("Matrícula já existe, não é possível cadastrar outro usuário com a mesma matrícula.")
            return "Matrícula já existe, não é possível cadastrar outro usuário com a mesma matrícula."


         if senha == confirmar_senha:
            senhaUsuario = hashlib.sha256(senha.encode()).hexdigest()
            usuario = Usuarios(matricula = matriculaUsuario,senha = senhaUsuario, email = email)
            db.session.add(usuario)
            db.session.commit()
         else:
            flash('A senha e a confirmação de senha devem ser iguais')

         checar = pegar_usuario(id=session['usuario.id'])
         
         if (checar):
            flash('Usuário cadastrado com sucesso')
            # mensagem de confirmação de cadastro
            print(f"ID: {usuario.email}, Matricula: {usuario.matricula}")
         db.session.close()
      return render_template('cadastro_usuario.html',logged_in=logged_in,admin=admin, email=email)
   else:
      flash('Usuário não cadastrado')
      return redirect(url_for('login'))

@app.route('/usuarios_existentes', methods = ['GET', 'POST'])
def usuarios_existentes():
   admin = session.get('admin', False)
   logged_in = session.get('logged_in', False)
   
   with db.session.begin():
      usuarios = db.session.query(Usuarios).filter_by(ativo=True).all()

      if (request.method == 'POST'):
         matricula_usuario = request.form['detalhes-matricula']
         email_usuario = request.form['detalhes-email']
         usuario = pegar_usuario(matricula=matricula_usuario,email=email_usuario)
         if usuario:
               usuario.ativo = False
               db.session.add(usuario)
               db.session.commit()

      #          total_usuarios = len(usuarios)
      #          progresso = 0

      #          progresso += 1
      #          progresso_percentual = int(progresso / total_usuarios * 100)

         
      #          # Simulação de atraso para demonstração
      #          time.sleep(1)

      #   # Atualiza o progresso para o cliente
      #          yield "data:" + str(progresso_percentual) + "\n\n"

               flash('Usuário excluído com sucesso')
               return redirect(url_for('usuarios_existentes'))

         else:
         # Lide com o caso em que o usuário não foi encontrado
            flash("Usuário não encontrado","error")
   return render_template('usuarios_existentes.html',logged_in=logged_in, admin=admin, usuarios= usuarios)



@app.route('/tela_principal')
def tela_principal():
   admin = session.get('admin', False)
   logged_in = session.get('logged_in', False)
   dados = tabela()

   return render_template('tela_principal.html',logged_in=logged_in, admin=admin,dados=dados)


def tabela():
    dias_da_semana = db.session.query(DiasDaSemana).all()

    # Criar uma lista de listas para representar os horários de cada dia da semana
    horarios_tabela = [[] for _ in range(7)]
   
    for dia_semana in dias_da_semana:
        horarios = dia_semana.ativacoes
        indice = dia_semana.numero

        for horario in horarios:
           hora = horario.hora
           minuto = horario.minuto

           hora_formatada = f"{hora:02d}"
           minuto_formatado = f"{minuto:02d}"
           
           horarios_tabela[indice].append((hora_formatada, minuto_formatado))
           horarios_tabela[indice] = sorted(horarios_tabela[indice])
   
    maior_tamanho = max(len(dia) for dia in horarios_tabela)
    # Crie dados no form/ato desejado para a renderização no template
    dados = {
        'cabecalho': ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'],
        'horarios': horarios_tabela,
        'maior_tamanho': maior_tamanho
   }

    return dados

def checagem_horario(hora,minuto):
   horario_existente = Horarios.query.filter_by(hora = hora, minuto = minuto).first()
   horario_id = ""

   if (horario_existente):
      checagem = True
   else:
      checagem = False

   return checagem

def adicionar_horario(hora,minuto):
   horario = Horarios(hora=hora,minuto=minuto,id_cadastro=session['usuario.id'])

   db.session.add(horario)
   db.session.commit()
   db.session.close()

def checagem_ativacao(horario_id, diaSemana_id):
   ativacao_existente = Ativacoes.query.filter_by(id_horario = horario_id, id_semana = diaSemana_id).first()

   if (ativacao_existente):
      mensagem = flash("Esse horário de ativação já está cadastrado")
      return mensagem
   else:
      nova_ativacao = Ativacoes(id_horario = horario_id, id_semana = diaSemana_id)
      db.session.add(nova_ativacao)
      db.session.commit()
      db.session.close()

   return True

@app.route("/excluir_relacionamento/<int:id_horario>", methods = ["POST"])
def excluir_relacionamento(id_horario):
   ativacoes = Ativacoes.query.get(id_horario)

   if ativacoes is not None:
        db.session.delete(ativacoes)
        db.session.commit()
   else:
      return "Relacionamento não encontrado", 404 

   return redirect (url_for('cadastro_horarios'))

def localizar_ativacao(hora,minuto,diaSemana):
   dia_da_semana = db.session.query(DiasDaSemana).filter_by(nome = diaSemana).first()
   horario = db.session.query(Horarios).filter_by(hora = hora, minuto = minuto).first()
   if (dia_da_semana and horario):
      ativacao = db.session.query(Ativacoes).filter_by(id_semana = dia_da_semana.id, id_horario = horario.id).first()
   
      return ativacao
   else:
      return print("dia da semana ou horario inexistentes")
      

def pegar_ativacoes():
   ativacoes = db.session.query(Ativacoes).all()
   lista_ativacoes = [[] for _ in range(3)]
   for ativacao in ativacoes:
      horario = ativacao.horario
      hora = horario.hora
      minuto = horario.minuto

      dia_semana = db.session.query(DiasDaSemana).filter_by(id=ativacao.id_semana).first()
      dia_semana_numero =  dia_semana.numero

      lista_ativacoes[0].append(dia_semana_numero)
      lista_ativacoes[1].append(hora)
      lista_ativacoes[2].append(minuto)
   
   return lista_ativacoes

def checagem_de_usuario(matricula,senha):
   senha_hash = hashlib.sha256(senha.encode()).hexdigest()
   usuario = Usuarios.query.filter_by(matricula = matricula, senha = senha_hash).first()
   
   
   if usuario and usuario.ativo:
      return usuario
   else:
      return False
      
   
def checagem_de_token(token):
   tokenReal = "8ejfçv.~gprkglje794jfy75jhgfi95hfkt8"
   if token == tokenReal:
      return True
   else:
      return False
   
def pegar_horario(id=None,hora=None,minuto=None):
   if (id != None):
      horario = db.session.query(Horarios).filter_by(id=id).first()

   elif (not hora == None) and (not minuto == None):
      horario = db.session.query(Horarios).filter_by(hora=hora,minuto=minuto).first()
   
   else:
      horario = "valores passados inválidos"
   
   print(horario)
   return horario

def pegar_usuario(matricula=None,email=None,id=None):
   if (matricula):
      if (email):
         usuario = db.session.query(Usuarios).filter_by(matricula=matricula,email=email).first()
      else: 
         usuario = db.session.query(Usuarios).filter_by(matricula=matricula).first()

   elif (id):
      usuario = db.session.query(Usuarios).filter_by(matricula=matricula).first()
   
   if (usuario):
      return usuario
   else:
      print('usuario inexistente')
      return False

if __name__ == "__main__":
   app.run(debug=True)
