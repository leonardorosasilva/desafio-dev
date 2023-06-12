from flask import Flask, render_template
import pandas as pd
import mysql.connector

app = Flask(__name__)

# Configurações do banco de dados MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="310304Leo.",
    database="mydatabase"
)

# Função para processar os dados e armazená-los no banco de dados
def processar_dados(df):
    # Mapear os nomes dos produtos para as categorias correspondentes
    categorias = {
        'A': 'MAQUINA DE CORTAR GRAMA',
        'B': 'MANGUEIRAS',
        'C': 'UTILIDADES DOMÉSTICAS',
        'D': 'LIMPEZA',
        'E': 'JARDINAGEM'
    }

    # Manipular os dados conforme necessário
    df['DATA'] = pd.to_datetime(df['DATA'], dayfirst=True)
    df['MES'] = df['DATA'].dt.month
    df['PRODUTO'] = df['Produtos:'].str.split().str[1]
    df['CATEGORIA'] = df['PRODUTO'].map(categorias)
    df['Quantidade De venda:'] = df['QUANTIDADE_VENDIDA'].astype(int)

    # Armazenar os dados no banco de dados MySQL
    cursor = db.cursor()

    for _, row in df.iterrows():
        mes = row['MES']
        produto = row['PRODUTO']
        categoria = row['CATEGORIA']
        quantidade = row['Quantidade De venda:']

        # Verificar se já existe um registro para o mês e produto no banco de dados
        cursor.execute("SELECT * FROM vendas WHERE mes=%s AND produto=%s", (mes, produto))
        result = cursor.fetchone()

        if result:
            # Atualizar o registro existente
            cursor.execute("UPDATE vendas SET quantidade=%s WHERE mes=%s AND produto=%s", (quantidade, mes, produto))
        else:
            # Inserir um novo registro
            cursor.execute("INSERT INTO vendas (mes, produto, categoria, quantidade) VALUES (%s, %s, %s, %s)",
                           (mes, produto, categoria, quantidade))

    db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar')
def processar():
    try:
        # Ler o arquivo Excel
        df = pd.read_excel('Base-Dados-Desafio-DEV-01.xlsx', sheet_name='VENDAS')

        # Processar os dados e armazená-los no banco de dados
        processar_dados(df)

        # Recuperar os dados do banco de dados para exibir em dados.html
        cursor = db.cursor()
        cursor.execute("SELECT * FROM vendas")
        dados = cursor.fetchall()

        return render_template('dados.html', dados=dados)
    except Exception as e:
        return f'Erro ao processar o arquivo: {str(e)}'

