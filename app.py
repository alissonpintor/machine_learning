from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import environ
import numpy as np
import pandas as pd
import streamlit as st

load_dotenv()

ip = environ['IP_ORACLE']
port = environ['PORT']
user = environ['USER']
password = environ['PASSWORD']

@st.cache_data
def get_produtos():
    # conex o com o banco de dados Oracle
    engine = create_engine(f'oracle+cx_oracle://{user}:{password}@{ip}:{port}/ORCL')
    # consulta a ser executada
    query = "SELECT * FROM TGFPRO WHERE ATIVO='S'"
    # executa a consulta e retorna um dataframe
    df = pd.read_sql_query(query, con=engine)
    return df
@st.cache_data
def get_vendas_produtos():
    engine = create_engine(f'oracle+cx_oracle://{user}:{password}@{ip}:{port}/ORCL')
    query = '''
        SELECT
            CAB.NUNOTA	
            , PRO.CODPROD
            , PRO.DESCRPROD 
            , PRO.MARCA
            , ITE.QTDNEG
            , VOA.QTDEMB
        FROM 
            TGFCAB CAB JOIN TGFITE ITE ON
                CAB.NUNOTA = ITE.NUNOTA
                AND CAB.CODTIPOPER = 3200
                AND CAB.DTFATUR >= SYSDATE - 180
            JOIN TGFPRO PRO ON
                PRO.CODPROD = ITE.CODPROD
                AND PRO.ATIVO = 'S'
                AND PRO.USOPROD = 'R'
                AND PRO.AGRUPMIN = 1
            JOIN (SELECT CODPROD, MIN(QUANTIDADE) AS QTDEMB FROM TGFVOA WHERE QUANTIDADE > 1 GROUP BY CODPROD) VOA ON
                PRO.CODPROD = VOA.CODPROD
    '''
    df = pd.read_sql_query(query, con=engine)
    return df

st.set_page_config(layout="wide")

df = get_vendas_produtos()
df_diferenca = df.loc[df['qtdneg'] >= df['qtdemb'], :].groupby(['codprod'])['nunota'].count().reset_index()
df_diferenca.columns = ['codprod', 'qtd']
df_medidas = df.groupby(['codprod', 'descrprod', 'marca', 'qtdemb'])['qtdneg'].agg(['min', 'max', 'mean', 'median', 'count']).reset_index()

condition = (
    (df_medidas['qtdemb'] == df_medidas['mean']) |
    (df_medidas['qtdemb'] == df_medidas['median'])
)

df1 = df_medidas.loc[condition, :]
# imprime o dataframe
df_merge = df_medidas.merge(df_diferenca, how='left')
df_merge['qtd'].fillna(0, inplace=True)
df_merge['diferenca'] = np.round(df_merge['qtd'] / df_merge['count'] * 100, 2) 

st.dataframe(df_merge)
