from flask import Flask, render_template, request
import pandas as pd
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="310304Leo.",
    database="mydatabase"
)

def processar_dados(df):
    # Mapear os nomes dos produtos para as categorias correspondentes
    categorias = {
        'A': 'MAQUINA DE CORTAR GRAMA',
        'B': 'MANGUEIRAS',
        'C': 'UTILIDADES DOMÉSTICAS',
        'D': 'LIMPEZA',
        'E': 'JARDINAGEM'
    }

    # Agrupar os dados por mês e produto
    df['DATA'] = pd.to_datetime(df['DATA'], dayfirst=True)
    df['MES'] = df['DATA'].dt.month
    df['PRODUTO'] = df['Produtos:'].str.split().str[1]
    df['CATEGORIA'] = df['PRODUTO'].map(categorias)
    df['Quantidade De venda:'] = df['Quantidade De venda:'].astype(int)

    vendas_mes = df.groupby(['MES', 'PRODUTO', 'CATEGORIA'])['Quantidade De venda:'].sum().reset_index()

    # Salvar as informações no banco de dados MySQL
    cursor = db.cursor()

    for _, row in vendas_mes.iterrows():
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

@app.route('/dados', methods=['POST'])
def dados():
    if 'fileExcel' not in request.files:
        return 'Nenhum arquivo selecionado'

    file = request.files['fileExcel']
    if file.filename == '':
        return 'Nenhum arquivo selecionado'

    try:
        df = pd.read_excel(file, sheet_name='Base-Dados-Desafio-DEV-01')
        processar_dados(df)

        cursor = db.cursor()
        cursor.execute("SELECT * FROM vendas")
        dados = cursor.fetchall()

        return render_template('dados.html', dados=dados)
    except Exception as e:
        return f'Erro ao processar o arquivo: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)
