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

# --- Função Auxiliar: Carregar Programas para o Dropdown ---
def get_lista_programas():
    """Busca os programas existentes para preencher o seletor."""
    try:
        df = pd.read_sql("SELECT Id_programa, Nome_Programa FROM Programa_Auxilio", engine)
        # Cria um dicionário: {'Nome do Programa (ID: 1)': 1, ...}
        return {f"{row['nome_programa']} (ID: {row['id_programa']})": row['id_programa'] for _, row in df.iterrows()}
    except:
        return {}

# --- Widgets ---

# ID do Edital (Controle)
id_edital = pn.widgets.IntInput(
    name='ID do Edital (Busca/Alteração)', 
    value=0, step=1, start=0
)

# Datas (DatePickers)
data_inicio = pn.widgets.DatePicker(
    name='Data de Início', 
    value=datetime.date.today()
)

data_fim = pn.widgets.DatePicker(
    name='Data de Fim', 
    value=datetime.date.today() + datetime.timedelta(days=30)
)

# Status (Dropdown)
status = pn.widgets.Select(
    name='Status do Edital', 
    options=['Aberto', 'Fechado', 'Em Análise', 'Cancelado'],
    value='Aberto'
)

# Seletor de Programa (Chave Estrangeira)
# Carrega dinamicamente os programas disponíveis
select_programa = pn.widgets.Select(
    name='Programa Vinculado',
    options=get_lista_programas()
)

# Botão para atualizar a lista de programas (caso alguém insira um novo programa enquanto usa esta tela)
btn_refresh_progs = pn.widgets.Button(name='🔄', width=40, align='end')

def refresh_programas(event=None):
    select_programa.options = get_lista_programas()
btn_refresh_progs.on_click(refresh_programas)


# Botões de Ação CRUD
btn_consultar = pn.widgets.Button(name='🔍 Consultar', button_type='primary')
btn_inserir   = pn.widgets.Button(name='➕ Criar Edital', button_type='success')
btn_atualizar = pn.widgets.Button(name='✏️ Atualizar', button_type='warning')
btn_excluir   = pn.widgets.Button(name='🗑️ Excluir', button_type='danger')


# --- Funções CRUD ---

def carregar_tabela():
    """Carrega a tabela unindo com o nome do programa para ficar legível."""
    try:
        sql = """
        SELECT 
            E.Id_edital, 
            E.Data_inicio, 
            E.Data_fim, 
            E.Status, 
            P.Nome_Programa 
        FROM Edital E
        LEFT JOIN Programa_Auxilio P ON E.Id_programa = P.Id_programa
        ORDER BY E.Id_edital DESC
        """
        df = pd.read_sql_query(sql, engine)
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, sizing_mode='stretch_width')
    except Exception as e:
        return pn.pane.Alert(f'Erro: {str(e)}', alert_type='danger')

def on_consultar(event=None):
    """Busca filtrada por ID ou Status."""
    try:
        query = """
            SELECT E.*, P.Nome_Programa 
            FROM Edital E
            LEFT JOIN Programa_Auxilio P ON E.Id_programa = P.Id_programa
            WHERE 1=1
        """
        params = {}

        if id_edital.value > 0:
            query += " AND E.Id_edital = %(id)s"
            params['id'] = id_edital.value
        
        # Se não filtrou por ID, considera o status selecionado se o usuário quiser (opcional)
        # Aqui vamos fazer uma busca simples: Se ID=0, traz tudo.
        
        query += " ORDER BY E.Id_edital DESC"
        
        df = pd.read_sql_query(query, engine, params=params)
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, sizing_mode='stretch_width')
    except Exception as e:
        pn.state.notifications.error(f'Erro na consulta: {str(e)}')
        return pn.pane.Alert(f'Erro: {str(e)}')

def on_inserir(event=None):
    try:
        if not select_programa.value:
            pn.state.notifications.error('Selecione um Programa!')
            return on_consultar()

        with con.cursor() as cursor:
            sql = """
                INSERT INTO Edital (Data_inicio, Data_fim, Status, Id_programa)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (data_inicio.value, data_fim.value, status.value, select_programa.value))
            con.commit()
        
        pn.state.notifications.success('Edital criado com sucesso!')
        return carregar_tabela()
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Erro ao inserir: {str(e)}')
        return on_consultar()

def on_atualizar(event=None):
    try:
        if id_edital.value <= 0:
            pn.state.notifications.warning('ID inválido.')
            return on_consultar()

        with con.cursor() as cursor:
            # Verifica se existe
            cursor.execute("SELECT 1 FROM Edital WHERE Id_edital = %s", (id_edital.value,))
            if not cursor.fetchone():
                pn.state.notifications.warning('Edital não encontrado.')
                return on_consultar()

            sql = """
                UPDATE Edital 
                SET Data_inicio=%s, Data_fim=%s, Status=%s, Id_programa=%s
                WHERE Id_edital=%s
            """
            cursor.execute(sql, (data_inicio.value, data_fim.value, status.value, select_programa.value, id_edital.value))
            con.commit()

        pn.state.notifications.success(f'Edital {id_edital.value} atualizado!')
        return carregar_tabela()
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Erro: {str(e)}')
        return on_consultar()

def on_excluir(event=None):
    try:
        if id_edital.value <= 0:
            pn.state.notifications.warning('ID inválido.')
            return on_consultar()

        with con.cursor() as cursor:
            sql = "DELETE FROM Edital WHERE Id_edital = %s"
            cursor.execute(sql, (id_edital.value,))
            if cursor.rowcount == 0:
                pn.state.notifications.warning('ID não encontrado.')
            else:
                con.commit()
                pn.state.notifications.success('Edital excluído!')
        
        return carregar_tabela()
    except Exception as e:
        con.rollback()
        if 'foreign key' in str(e).lower():
            pn.state.notifications.error('Impossível excluir: Existem Inscrições vinculadas a este Edital.')
        else:
            pn.state.notifications.error(f'Erro: {str(e)}')
        return on_consultar()

# --- Painel Reativo ---
def painel_reativo(consultar, inserir, atualizar, excluir):
    if inserir: return on_inserir()
    if atualizar: return on_atualizar()
    if excluir: return on_excluir()
    return on_consultar()

tabela_resultado = pn.bind(painel_reativo, btn_consultar, btn_inserir, btn_atualizar, btn_excluir)

# --- Layout (Template Profissional) ---
template = pn.template.FastListTemplate(
    title='📅 Gestão de Editais',
    sidebar=[
        pn.pane.Markdown("### Controles"),
        id_edital,
        pn.layout.Divider(),
        pn.pane.Markdown("**Dados do Edital**"),
        data_inicio,
        data_fim,
        status,
        pn.pane.Markdown("**Vincular Programa**"),
        pn.Row(select_programa, btn_refresh_progs),
        pn.layout.Divider(),
        btn_consultar,
        btn_inserir,
        btn_atualizar,
        btn_excluir
    ],
    main=[
        pn.pane.Markdown("### Editais Cadastrados"),
        tabela_resultado
    ],
    accent_base_color="#2F4F4F",
    header_background="#2F4F4F",
)

template.servable()