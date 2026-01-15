import os
from dotenv import load_dotenv
import pandas as pd
import psycopg2 as pg
import sqlalchemy
import panel as pn

# --- Configuração Inicial ---
load_dotenv()
pn.extension()
pn.extension('tabulator')
pn.extension(notifications=True) # Ativa notificações popup

# --- Conexão com Banco de Dados ---
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'fbd-conexao')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'root')

# Engine para Leituras (Pandas)
str_conn = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
engine = sqlalchemy.create_engine(str_conn)

# Conexão para Escritas (Inserir/Atualizar/Deletar)
try:
    con = pg.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
except Exception as e:
    pn.pane.Alert(f"Erro fatal de conexão: {e}", alert_type='danger').servable()

# --- Widgets (Campos do Formulário) ---

# ID para controle
id_programa = pn.widgets.IntInput(
    name='ID do Programa (Use para Buscar/Atualizar/Excluir)', 
    value=0, 
    step=1, 
    start=0
)

# Campos de Dados
nome_prog = pn.widgets.TextInput(
    name='Nome do Programa', 
    placeholder='Ex: Auxílio Moradia'
)

descricao = pn.widgets.TextAreaInput(
    name='Descrição', 
    placeholder='Detalhes sobre o auxílio...', 
    height=100
)

valor = pn.widgets.FloatInput(
    name='Valor (R$)', 
    value=0.00, 
    step=10.00, 
    start=0
)

# Dropdown para o Tipo (Padronização)
tipo = pn.widgets.Select(
    name='Tipo de Auxílio', 
    options=['Assistência', 'Pesquisa', 'Extensão', 'Alimentação', 'Transporte', 'Outro'],
    value='Assistência'
)

vagas = pn.widgets.IntInput(
    name='Quantidade de Vagas', 
    value=10, 
    step=1, 
    start=0
)

# Botões de Ação
btn_consultar = pn.widgets.Button(name='🔍 Consultar', button_type='primary')
btn_inserir   = pn.widgets.Button(name='➕ Inserir Novo', button_type='success')
btn_atualizar = pn.widgets.Button(name='✏️ Atualizar (pelo ID)', button_type='warning')
btn_excluir   = pn.widgets.Button(name='🗑️ Excluir (pelo ID)', button_type='danger')

# --- Funções CRUD ---

def carregar_dados_tabela():
    """Função auxiliar para recarregar a tabela visualmente"""
    try:
        query = "SELECT * FROM Programa_Auxilio ORDER BY Id_programa"
        df = pd.read_sql_query(query, engine)
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, sizing_mode='stretch_width')
    except Exception as e:
        return pn.pane.Alert(f'Erro ao carregar tabela: {str(e)}', alert_type='danger')

def on_consultar(event=None):
    """
    Busca programas. 
    Se ID > 0, busca exata. 
    Se Nome preenchido, busca parcial (ILIKE).
    Caso contrário, traz tudo.
    """
    try:
        query = "SELECT * FROM Programa_Auxilio WHERE 1=1"
        params = {}

        if id_programa.value > 0:
            query += " AND Id_programa = %(id)s"
            params['id'] = id_programa.value
        elif nome_prog.value_input:
            query += " AND Nome_Programa ILIKE %(nome)s"
            params['nome'] = f"%{nome_prog.value_input}%"
        
        query += " ORDER BY Id_programa ASC"
        
        df = pd.read_sql_query(query, engine, params=params)
        return pn.widgets.Tabulator(df, pagination='remote', page_size=10, sizing_mode='stretch_width')
    
    except Exception as e:
        pn.state.notifications.error(f'Erro na consulta: {str(e)}')
        return pn.pane.Alert(f'Erro: {str(e)}')

def on_inserir(event=None):
    """Insere novo programa. ID é gerado pelo banco."""
    try:
        if not nome_prog.value:
            pn.state.notifications.warning('O Nome do Programa é obrigatório!')
            return on_consultar()

        with con.cursor() as cursor:
            sql = """
                INSERT INTO Programa_Auxilio (Nome_Programa, Descricao, Valor, Tipo, Vagas)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (nome_prog.value, descricao.value, valor.value, tipo.value, vagas.value))
            con.commit()
        
        pn.state.notifications.success('Programa criado com sucesso!')
        return carregar_dados_tabela()
    
    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Erro ao inserir: {str(e)}')
        return on_consultar()

def on_atualizar(event=None):
    """Atualiza dados baseando-se no ID informado."""
    try:
        if id_programa.value <= 0:
            pn.state.notifications.warning('Selecione um ID válido para atualizar.')
            return on_consultar()

        with con.cursor() as cursor:
            # Verifica existência
            cursor.execute("SELECT 1 FROM Programa_Auxilio WHERE Id_programa = %s", (id_programa.value,))
            if not cursor.fetchone():
                pn.state.notifications.warning('Programa não encontrado com este ID.')
                return on_consultar()

            sql = """
                UPDATE Programa_Auxilio 
                SET Nome_Programa=%s, Descricao=%s, Valor=%s, Tipo=%s, Vagas=%s
                WHERE Id_programa=%s
            """
            cursor.execute(sql, (nome_prog.value, descricao.value, valor.value, tipo.value, vagas.value, id_programa.value))
            con.commit()

        pn.state.notifications.success(f'Programa {id_programa.value} atualizado!')
        return carregar_dados_tabela()

    except Exception as e:
        con.rollback()
        pn.state.notifications.error(f'Erro ao atualizar: {str(e)}')
        return on_consultar()

def on_excluir(event=None):
    """Exclui programa pelo ID."""
    try:
        if id_programa.value <= 0:
            pn.state.notifications.warning('Selecione um ID válido para excluir.')
            return on_consultar()

        with con.cursor() as cursor:
            # Tenta excluir
            sql = "DELETE FROM Programa_Auxilio WHERE Id_programa = %s"
            cursor.execute(sql, (id_programa.value,))
            
            if cursor.rowcount == 0:
                pn.state.notifications.warning('ID não encontrado.')
            else:
                con.commit()
                pn.state.notifications.success('Programa excluído com sucesso!')

        return carregar_dados_tabela()

    except Exception as e:
        con.rollback()
        # Captura erro de chave estrangeira (se houver Editais vinculados)
        if 'foreign key' in str(e).lower():
            pn.state.notifications.error('ERRO: Não é possível excluir este Programa pois existem Editais vinculados a ele.')
        else:
            pn.state.notifications.error(f'Erro ao excluir: {str(e)}')
        return on_consultar()

# --- Painel Reativo ---
def painel_reativo(consultar, inserir, atualizar, excluir):
    if inserir: return on_inserir()
    if atualizar: return on_atualizar()
    if excluir: return on_excluir()
    return on_consultar()

tabela_resultado = pn.bind(painel_reativo, btn_consultar, btn_inserir, btn_atualizar, btn_excluir)

# --- Layout Final ---
template = pn.template.FastListTemplate(
    title='Gestão de Programas',
    sidebar=[
        pn.pane.Markdown("## Controles"),
        id_programa,
        nome_prog,
        descricao,
        tipo,
        pn.Row(valor, vagas),
        pn.layout.Divider(),
        btn_consultar, btn_inserir, btn_atualizar, btn_excluir
    ],
    main=[
        pn.pane.Markdown("## Resultados"),
        tabela_resultado
    ],
    accent_base_color="#88d8b0",
    header_background="#88d8b0",
)

template.servable()