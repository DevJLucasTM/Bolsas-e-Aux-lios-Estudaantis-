import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2 as pg
import sqlalchemy
import panel as pn

# Carrega configurações
load_dotenv()
pn.extension()
pn.extension('tabulator')
pn.extension(notifications=True)

# --- Configuração do Banco de Dados ---
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'fbd-conexao') # Ajuste para seu banco
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'root')

# Conexão para Transações (INSERT, UPDATE, DELETE)
con = pg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

# Conexão para Consultas (Pandas/SQLAlchemy)
str_conn = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
engine = sqlalchemy.create_engine(str_conn)

# --- Widgets (Campos de Entrada) ---
# ID é usado apenas para Atualizar/Excluir/Buscar Específico
id_usuario = pn.widgets.IntInput(name='ID do Usuário (Para Alterar/Excluir)', value=0, step=1)

cpf = pn.widgets.TextInput(name='CPF', placeholder='000.000.000-00')
nome = pn.widgets.TextInput(name='Nome Completo', placeholder='Digite o nome')
email = pn.widgets.TextInput(name='E-mail', placeholder='exemplo@email.com')
senha = pn.widgets.PasswordInput(name='Senha', placeholder='Digite a senha') # Campo de senha oculto
endereco = pn.widgets.TextInput(name='Endereço', placeholder='Rua, Número, Bairro')
telefone = pn.widgets.TextInput(name='Telefone', placeholder='(00) 00000-0000')

# Botões
btn_consultar = pn.widgets.Button(name='🔍 Consultar', button_type='primary')
btn_inserir   = pn.widgets.Button(name='➕ Inserir', button_type='success')
btn_atualizar = pn.widgets.Button(name='✏️ Atualizar (pelo ID)', button_type='warning')
btn_excluir   = pn.widgets.Button(name='🗑️ Excluir (pelo ID)', button_type='danger')

# --- Funções do CRUD ---

def carregar_todos():
    """Busca todos os usuários para recarregar a tabela."""
    try:
        # Ordenamos por ID para manter a tabela organizada
        df = pd.read_sql_query("SELECT * FROM Usuario ORDER BY Id_usuario", engine)
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, sizing_mode='stretch_width')
    except Exception as e:
        return pn.pane.Alert(f'Erro ao carregar dados: {str(e)}', alert_type='danger')

def on_consultar(event=None):
    """
    Busca dinâmica:
    - Se ID > 0 informado: Busca pelo ID.
    - Se Nome preenchido: Busca por parte do nome (ILIKE).
    - Se vazio: Busca tudo.
    """
    try:
        query = "SELECT * FROM Usuario WHERE 1=1"
        params = {}
        
        if id_usuario.value > 0:
            query += " AND Id_usuario = %(id)s"
            params['id'] = id_usuario.value
        elif nome.value_input:
            query += " AND Nome ILIKE %(nome)s"
            params['nome'] = f"%{nome.value_input}%"
            
        query += " ORDER BY Id_usuario"
        
        df = pd.read_sql_query(query, engine, params=params)
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, sizing_mode='stretch_width')
    except Exception as e:
        return pn.pane.Alert(f'Erro na consulta: {str(e)}', alert_type='danger')

def on_inserir(event=None):
    """Insere novo usuário. O ID é gerado automaticamente (SERIAL)."""
    try:
        if not cpf.value or not nome.value or not email.value or not senha.value:
            pn.state.notifications.warning('Preencha CPF, Nome, Email e Senha!')
            return on_consultar()

        with con.cursor() as cursor:
            sql = """
                INSERT INTO Usuario (CPF, Nome, Email, Senha, Endereco, Telefone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (cpf.value, nome.value, email.value, senha.value, endereco.value, telefone.value))
            con.commit()
        
        pn.state.notifications.success('Usuário inserido com sucesso!')
        return carregar_todos()
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Erro ao inserir: {str(e)}')
        return on_consultar()

def on_atualizar(event=None):
    """Atualiza os dados do usuário baseado no ID informado no widget."""
    try:
        if id_usuario.value <= 0:
            pn.state.notifications.warning('Informe um ID válido para atualizar!')
            return on_consultar()

        with con.cursor() as cursor:
            # Verifica se o ID existe antes
            cursor.execute("SELECT 1 FROM Usuario WHERE Id_usuario = %s", (id_usuario.value,))
            if not cursor.fetchone():
                pn.state.notifications.warning('ID não encontrado.')
                return on_consultar()

            sql = """
                UPDATE Usuario 
                SET CPF=%s, Nome=%s, Email=%s, Senha=%s, Endereco=%s, Telefone=%s
                WHERE Id_usuario=%s
            """
            cursor.execute(sql, (cpf.value, nome.value, email.value, senha.value, endereco.value, telefone.value, id_usuario.value))
            con.commit()

        pn.state.notifications.success(f'Usuário ID {id_usuario.value} atualizado!')
        return carregar_todos()
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Erro ao atualizar: {str(e)}')
        return on_consultar()

def on_excluir(event=None):
    """Exclui o usuário baseado no ID informado."""
    try:
        if id_usuario.value <= 0:
            pn.state.notifications.warning('Informe um ID válido para excluir!')
            return on_consultar()

        with con.cursor() as cursor:
            # Atenção: Isso pode falhar se o usuário tiver vínculos (FK) com Estudante/Servidor
            # Idealmente, tratar a constraint exception
            sql = "DELETE FROM Usuario WHERE Id_usuario = %s"
            cursor.execute(sql, (id_usuario.value,))
            
            if cursor.rowcount == 0:
                pn.state.notifications.warning('ID não encontrado para exclusão.')
            else:
                con.commit()
                pn.state.notifications.success('Usuário excluído com sucesso!')

        return carregar_todos()
    except Exception as e:
        con.rollback()
        # Tratamento simples para erro de chave estrangeira
        if 'foreign key constraint' in str(e).lower():
             pn.state.notifications.error('Não é possível excluir: Usuário possui vínculos (Estudante/Servidor).')
        else:
            pn.state.notifications.error(f'Erro ao excluir: {str(e)}')
        return on_consultar()

# --- Binding (Lógica dos Botões) ---
def painel_reativo(consultar, inserir, atualizar, excluir):
    # A lógica aqui identifica qual botão foi clicado baseando-se no 'watch' do Panel
    # Mas para simplificar e garantir retorno visual:
    if inserir: return on_inserir()
    if atualizar: return on_atualizar()
    if excluir: return on_excluir()
    return on_consultar() # Padrão ou botão consultar

tabela_resultado = pn.bind(painel_reativo, btn_consultar, btn_inserir, btn_atualizar, btn_excluir)

# --- Layout ---
layout = pn.Row(
    pn.Column(
        pn.pane.Markdown("# 👤 Gerenciamento de Usuários"),
        pn.pane.Markdown("Use o **ID** apenas para buscar específico, atualizar ou excluir."),
        id_usuario,
        pn.layout.Divider(),
        cpf,
        nome,
        email,
        senha,
        endereco,
        telefone,
        pn.layout.Divider(),
        pn.Row(btn_consultar, btn_inserir),
        pn.Row(btn_atualizar, btn_excluir),
        width=400
    ),
    pn.Column(
        pn.pane.Markdown("### 📋 Lista de Usuários"),
        tabela_resultado,
        sizing_mode='stretch_width'
    )
)

layout.servable()