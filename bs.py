import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2 as pg
import sqlalchemy
import panel as pn
import datetime

# --- Configurações Iniciais ---
load_dotenv()
pn.extension()
pn.extension('tabulator')
pn.extension(notifications=True)

# --- Conexão Banco de Dados ---
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'fbd-conexao')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'root')

str_conn = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
engine = sqlalchemy.create_engine(str_conn)

try:
    con = pg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
except Exception as e:
    pn.pane.Alert(f"Erro de conexão: {e}", alert_type='danger').servable()

# --- Funções Auxiliares (Preencher Dropdowns) ---

def get_inscricoes_disponiveis():
    """Busca inscrições para vincular. Mostra ID e Nome do Aluno."""
    try:
        sql = """
            SELECT I.Id_inscricao, U.Nome 
            FROM Inscricao I
            JOIN Estudante E ON I.Id_Estudante = E.Id_Estudante
            JOIN Usuario U ON E.Id_Estudante = U.Id_usuario
        """
        df = pd.read_sql(sql, engine)
        return {f"Inscrição #{row['id_inscricao']} - {row['nome']}": row['id_inscricao'] for _, row in df.iterrows()}
    except:
        return {}

def get_servidores():
    """Busca lista de servidores (orientadores)."""
    try:
        sql = """
            SELECT S.Id_Servidor, U.Nome, S.Cargo 
            FROM Servidor S
            JOIN Usuario U ON S.Id_Servidor = U.Id_usuario
        """
        df = pd.read_sql(sql, engine)
        return {f"{row['nome']} ({row['cargo']})": row['id_servidor'] for _, row in df.iterrows()}
    except:
        return {}

def get_estudantes():
    """Busca lista de estudantes para garantir a integridade do vínculo."""
    try:
        sql = """
            SELECT E.Id_Estudante, U.Nome, E.Matricula 
            FROM Estudante E
            JOIN Usuario U ON E.Id_Estudante = U.Id_usuario
        """
        df = pd.read_sql(sql, engine)
        return {f"{row['nome']} (Mat: {row['matricula']})": row['id_estudante'] for _, row in df.iterrows()}
    except:
        return {}

# --- Widgets ---

# PK: Seleção da Inscrição (Serve como ID)
select_inscricao = pn.widgets.Select(
    name='Vincular à Inscrição (ID)',
    options=get_inscricoes_disponiveis(),
    description='Selecione a inscrição que se tornará bolsista. O ID da inscrição será o ID do Bolsista.'
)

# Dados do Bolsista
data_inicio = pn.widgets.DatePicker(name='Data Início', value=datetime.date.today())
data_fim = pn.widgets.DatePicker(name='Data Fim', value=datetime.date.today() + datetime.timedelta(days=365))
data_desligamento = pn.widgets.DatePicker(name='Data Desligamento', value=None, disabled=True)

# Checkbox para ativar campo de desligamento
check_desligar = pn.widgets.Checkbox(name='Informar Desligamento?')
def toggle_desligamento(event):
    data_desligamento.disabled = not event.new
check_desligar.param.watch(toggle_desligamento, 'value')

frequencia = pn.widgets.Select(
    name='Frequência de Pagamento',
    options=['Mensal', 'Semestral', 'Anual', 'Parcela Única'],
    value='Mensal'
)

# Foreign Keys
select_orientador = pn.widgets.Select(name='Orientador (Servidor)', options=get_servidores())
select_estudante  = pn.widgets.Select(name='Estudante Vinculado', options=get_estudantes())

# Botão Refresh (útil se cadastrarem novos usuários em outra tela)
btn_refresh = pn.widgets.Button(name='🔄 Atualizar Listas', width=100)
def refresh_lists(event=None):
    select_inscricao.options = get_inscricoes_disponiveis()
    select_orientador.options = get_servidores()
    select_estudante.options = get_estudantes()
btn_refresh.on_click(refresh_lists)

# Botões CRUD
btn_consultar = pn.widgets.Button(name='🔍 Consultar', button_type='primary')
btn_inserir   = pn.widgets.Button(name='➕ Inserir Bolsista', button_type='success')
btn_atualizar = pn.widgets.Button(name='✏️ Atualizar', button_type='warning')
btn_excluir   = pn.widgets.Button(name='🗑️ Excluir', button_type='danger')


# --- Funções CRUD ---

def carregar_tabela():
    try:
        # Query complexa para trazer nomes legíveis em vez de IDs
        sql = """
        SELECT 
            B.Id_inscricao AS "ID/Inscrição",
            U_Aluno.Nome AS "Estudante",
            U_Prof.Nome AS "Orientador",
            B.Data_inicio,
            B.Data_fim,
            B.Frequencia
        FROM Bolsista B
        JOIN Estudante E ON B.Id_Estudante = E.Id_Estudante
        JOIN Usuario U_Aluno ON E.Id_Estudante = U_Aluno.Id_usuario
        JOIN Servidor S ON B.Id_Orientador = S.Id_Servidor
        JOIN Usuario U_Prof ON S.Id_Servidor = U_Prof.Id_usuario
        ORDER BY B.Data_inicio DESC
        """
        df = pd.read_sql_query(sql, engine)
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, sizing_mode='stretch_width')
    except Exception as e:
        return pn.pane.Alert(f'Erro: {str(e)}', alert_type='danger')

def on_consultar(event=None):
    # Por simplicidade, recarrega a tabela completa com os joins
    return carregar_tabela()

def on_inserir(event=None):
    try:
        if not select_inscricao.value:
            pn.state.notifications.error('Selecione uma Inscrição!')
            return

        with con.cursor() as cursor:
            # Verifica se já existe bolsista para essa inscrição
            cursor.execute("SELECT 1 FROM Bolsista WHERE Id_inscricao = %s", (select_inscricao.value,))
            if cursor.fetchone():
                pn.state.notifications.error('Erro: Esta inscrição JÁ possui cadastro de bolsista.')
                return on_consultar()

            sql = """
                INSERT INTO Bolsista (Id_inscricao, Data_inicio, Data_fim, Data_desligamento, Frequencia, Id_Orientador, Id_Estudante)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            # Trata data de desligamento vazia
            dt_deslig = data_desligamento.value if check_desligar.value else None
            
            cursor.execute(sql, (
                select_inscricao.value, 
                data_inicio.value, 
                data_fim.value, 
                dt_deslig, 
                frequencia.value, 
                select_orientador.value, 
                select_estudante.value
            ))
            con.commit()
        
        pn.state.notifications.success('Bolsista cadastrado com sucesso!')
        return carregar_tabela()
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Erro ao inserir: {str(e)}')
        return on_consultar()

def on_atualizar(event=None):
    """Atualiza dados do bolsista (Datas, Orientador, Frequência)."""
    try:
        pk_id = select_inscricao.value
        if not pk_id:
            pn.state.notifications.warning('Selecione a inscrição (ID) para atualizar.')
            return

        with con.cursor() as cursor:
            dt_deslig = data_desligamento.value if check_desligar.value else None
            
            sql = """
                UPDATE Bolsista 
                SET Data_inicio=%s, Data_fim=%s, Data_desligamento=%s, Frequencia=%s, Id_Orientador=%s, Id_Estudante=%s
                WHERE Id_inscricao=%s
            """
            cursor.execute(sql, (
                data_inicio.value, data_fim.value, dt_deslig, frequencia.value, 
                select_orientador.value, select_estudante.value, pk_id
            ))
            
            if cursor.rowcount == 0:
                pn.state.notifications.warning('Registro não encontrado para atualização.')
            else:
                con.commit()
                pn.state.notifications.success(f'Bolsista {pk_id} atualizado!')

        return carregar_tabela()
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Erro: {str(e)}')
        return on_consultar()

def on_excluir(event=None):
    """Remove o registro de Bolsista (não apaga a inscrição, apenas o vínculo de bolsa)."""
    try:
        pk_id = select_inscricao.value
        if not pk_id:
            pn.state.notifications.warning('Selecione a inscrição (ID) para excluir.')
            return

        with con.cursor() as cursor:
            sql = "DELETE FROM Bolsista WHERE Id_inscricao = %s"
            cursor.execute(sql, (pk_id,))
            
            if cursor.rowcount == 0:
                pn.state.notifications.warning('Registro não encontrado.')
            else:
                con.commit()
                pn.state.notifications.success('Registro de bolsista removido!')
        
        return carregar_tabela()
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Erro ao excluir: {str(e)}')
        return on_consultar()

# --- Lógica de UI ---
def painel_reativo(consultar, inserir, atualizar, excluir):
    if inserir: return on_inserir()
    if atualizar: return on_atualizar()
    if excluir: return on_excluir()
    return on_consultar()

tabela_resultado = pn.bind(painel_reativo, btn_consultar, btn_inserir, btn_atualizar, btn_excluir)

# --- Template ---
template = pn.template.FastListTemplate(
    title='🎓 Gestão de Bolsistas',
    sidebar=[
        pn.pane.Markdown("### Vínculo"),
        pn.pane.Markdown("A chave do bolsista é a Inscrição aprovada."),
        select_inscricao,
        select_estudante,
        select_orientador,
        btn_refresh,
        pn.layout.Divider(),
        pn.pane.Markdown("### Detalhes"),
        data_inicio,
        data_fim,
        pn.Row(check_desligar, data_desligamento),
        frequencia,
        pn.layout.Divider(),
        btn_consultar, btn_inserir, btn_atualizar, btn_excluir
    ],
    main=[
        pn.pane.Markdown("### Quadro de Bolsistas Ativos"),
        tabela_resultado
    ],
    accent_base_color="#E91E63", # Cor rosa/avermelhada para diferenciar
    header_background="#C2185B",
)

template.servable()