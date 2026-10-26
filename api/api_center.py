import sqlite3 as sql
import re as regex
from flask import Flask, g, request, jsonify

import os
import sqlite3

app = Flask(__name__)
port = 5000
base_url = f"http://127.0.0.1:{port}"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'marquei.db'))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def formata_e_valida_telefone(telefone: str) -> str:

    apenas_numeros = regex.sub(r'\D', '', str(telefone))

    # Verifica se tem exatamente 11 dígitos (DDD de 2 dígitos + 9 dígitos do celular)
    if len(apenas_numeros) != 11:
        raise ValueError(f"Telefone inválido: '{telefone}'. O telefone deve conter 11 dígitos (ex: 11999998888).")

    # Aplica a máscara (XX) XXXXX-XXXX
    telefone_formatado = f"({apenas_numeros[:2]}) {apenas_numeros[2:7]}-{apenas_numeros[7:]}"
    return telefone_formatado

############################################################################################################ CLIENTES
@app.route("/busca_cliente", methods=["GET"])
def listar_clientes():
    db = get_db()
    cursor = db.execute("SELECT id_cliente, ds_cliente, ds_contato, dh_primeiro_agendamento, dh_ultimo_agendamento, dh_inclusao FROM cliente")
    clientes = [dict(row) for row in cursor.fetchall()]
    return jsonify(clientes)

@app.route("/insere_cliente", methods=["POST"]) # Rota para inserir um cliente no banco de dados
def insere_cliente():

    db = get_db()
    
    dados = request.get_json(silent=True) or {}

    ds_cliente = dados.get("ds_cliente")
    ds_contato = dados.get("ds_contato")
    dh_primeiro_agendamento = dados.get("dh_primeiro_agendamento")
    dh_ultimo_agendamento = dados.get("dh_ultimo_agendamento")

    if ds_cliente == None or ds_cliente.strip() == "":
        return jsonify({"error": "O campo 'ds_cliente' é obrigatório."}), 400
    elif ds_contato == None or ds_contato.strip() == "":
        return jsonify({"error": "O campo 'ds_contato' é obrigatório."}), 400

    try:
        ds_contato = formata_e_valida_telefone(ds_contato)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    query = """
        INSERT INTO cliente (
            ds_cliente, 
            ds_contato, 
            dh_primeiro_agendamento, 
            dh_ultimo_agendamento, 
            dh_inclusao, 
            dh_alteracao
        )
        VALUES (?, ?, ?, ?, date('now'), date('now'))
    """
    
    db.execute(query, (ds_cliente, ds_contato, dh_primeiro_agendamento, dh_ultimo_agendamento))
    db.commit()

    return jsonify({"message": "Cliente inserido com sucesso!"}), 201

@app.route("/edita_cliente/<int:id_cliente>", methods=["PUT"])  # Rota para atualizar um cliente no banco de dados
def edita_cliente(id_cliente):
    db = get_db()
    
    dados = request.get_json(silent=True) or {}

    ds_cliente = dados.get("ds_cliente")
    ds_contato = dados.get("ds_contato")
    dh_primeiro_agendamento = dados.get("dh_primeiro_agendamento")
    dh_ultimo_agendamento = dados.get("dh_ultimo_agendamento")

    if ds_cliente == None or ds_cliente.strip() == "":
        return jsonify({"error": "O campo 'ds_cliente' é obrigatório."}), 400
    elif ds_contato == None or ds_contato.strip() == "":
        return jsonify({"error": "O campo 'ds_contato' é obrigatório."}), 400

    try:
        ds_contato = formata_e_valida_telefone(ds_contato)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    query = """
        UPDATE cliente
        SET 
            ds_cliente = ?, 
            ds_contato = ?, 
            dh_primeiro_agendamento = ?, 
            dh_ultimo_agendamento = ?, 
            dh_alteracao = date('now')
            WHERE id_cliente = ?"""

    db.execute(query, (ds_cliente, ds_contato, dh_primeiro_agendamento, dh_ultimo_agendamento, id_cliente))
    db.commit()
    return jsonify({"message": "Cliente atualizado com sucesso!"}), 200

@app.route("/deleta_cliente/<int:id_cliente>", methods=["DELETE"])
def deleta_cliente(id_cliente):
    db = get_db()
    
    query = """
        DELETE FROM cliente
        WHERE id_cliente = ?;
    """

    cursor = db.execute(query, (id_cliente,))
    db.commit()

    if cursor.rowcount == 0:
        return jsonify({"error": "Cliente não encontrado"}), 404

    return jsonify({"message": "Cliente deletado com sucesso!"}), 200

############################################################################################################ PRODUTO / SERVICO
@app.route("/busca_produto_servico", methods=["GET"]) 
def listar_produto_servico():
    db = get_db()
    cursor = db.execute("SELECT id_produto_servico, ds_produto_servico, ds_categoria, qt_estoque, vl_unitario_produto_compra, vl_unitario_produto_venda, dh_ultima_movimentacao FROM produto_servico;")
    produto_servico = [dict(row) for row in cursor.fetchall()]
    return jsonify(produto_servico)

@app.route("/busca_produto", methods=["GET"]) 
def listar_produto():
    db = get_db()
    cursor = db.execute("SELECT id_produto_servico, ds_produto_servico, ds_categoria, qt_estoque, vl_unitario_produto_compra, vl_unitario_produto_venda, dh_ultima_movimentacao FROM produto_servico WHERE ds_categoria = 'PRODUTO';")
    produto = [dict(row) for row in cursor.fetchall()]
    return jsonify(produto)

@app.route("/busca_servico", methods=["GET"]) 
def listar_servico():
    db = get_db()
    cursor = db.execute("SELECT id_produto_servico, ds_produto_servico, ds_categoria, qt_estoque, vl_unitario_produto_compra, vl_unitario_produto_venda, dh_ultima_movimentacao FROM produto_servico WHERE ds_categoria = 'SERVICO';")
    servico = [dict(row) for row in cursor.fetchall()]
    return jsonify(servico)

@app.route("/insere_produto_servico", methods=["POST"])
def insere_produto_servico():
    db = get_db()
    dados = request.get_json(silent=True) or {}

    ds_produto_servico = str(dados.get("ds_produto_servico") or "").strip()
    ds_categoria = str(dados.get("ds_categoria") or "").strip().upper()
    vl_unitario_produto_compra = str(dados.get("vl_unitario_produto_compra") or "").strip()
    vl_unitario_produto_venda = str(dados.get("vl_unitario_produto_venda") or "").strip()
    qt_estoque = dados.get("qt_estoque")

    # Validações
    if not ds_produto_servico:
        return jsonify({"error": "O campo 'ds_produto_servico' é obrigatório."}), 400

    if not vl_unitario_produto_compra:
        return (jsonify({"error": "O campo 'vl_unitario_produto_compra' é obrigatório."}),400,)

    if not vl_unitario_produto_venda:
        return (jsonify({"error": "O campo 'vl_unitario_produto_venda' é obrigatório."}),400,)

    query = """
        INSERT INTO produto_servico (
            ds_produto_servico,
            ds_categoria, 
            qt_estoque,
            vl_unitario_produto_compra, 
            vl_unitario_produto_venda, 
            dh_inclusao,
            dh_alteracao
        )
        VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """

    db.execute(query, (ds_produto_servico, ds_categoria, qt_estoque, vl_unitario_produto_compra, vl_unitario_produto_venda))
    db.commit()

    return jsonify({"message": "Produto inserido com sucesso!"}), 201

@app.route("/edita_produto_servico/<int:id_produto_servico>", methods=["PUT"])
def edita_produto_servico(id_produto_servico):
    db = get_db()
    
    dados = request.get_json(silent=True) or {}

    ds_produto_servico = str(dados.get("ds_produto_servico") or "").strip()
    ds_categoria = str(dados.get("ds_categoria") or "").strip().upper()
    qt_estoque = dados.get("qt_estoque")
    vl_unitario_produto_compra = str(dados.get("vl_unitario_produto_compra") or "").strip()
    vl_unitario_produto_venda = str(dados.get("vl_unitario_produto_venda") or "").strip()

    if ds_produto_servico == None or ds_produto_servico.strip() == "":
        return jsonify({"error": "O campo 'ds_produto_servico' é obrigatório."}), 400
    elif vl_unitario_produto_compra == None or vl_unitario_produto_compra.strip() == "":
        return jsonify({"error": "O campo 'vl_unitario_produto_compra' é obrigatório."}), 400
    elif vl_unitario_produto_venda == None or vl_unitario_produto_venda.strip() == "":
        return jsonify({"error": "O campo 'vl_unitario_produto_venda' é obrigatório."}), 400

    query = """
        UPDATE produto_servico
        SET ds_produto_servico = ?,
            ds_categoria = ?,
            qt_estoque = ?,
            vl_unitario_produto_compra = ?,
            vl_unitario_produto_venda = ?,
            dh_alteracao = DATE('now')
        WHERE id_produto_servico = ?;
        """

    db.execute(query, (ds_produto_servico, ds_categoria, qt_estoque, vl_unitario_produto_compra, vl_unitario_produto_venda, id_produto_servico))
    db.commit()
    return jsonify({"message": "Cliente atualizado com sucesso!"}), 200

@app.route("/deleta_produto_servico/<int:id_produto_servico>", methods=["DELETE"])
def deleta_produto_servico(id_produto_servico):
    db = get_db()
    
    query = """
        DELETE FROM produto_servico
        WHERE id_produto_servico = ?;
    """

    cursor = db.cursor()
    cursor.execute(query, (id_produto_servico,))
    db.commit()

    if cursor.rowcount == 0:
        return jsonify({"error": "Produto/Servico não encontrado"}), 404

    return jsonify({"message": "Produto/Servico deletado com sucesso!"}), 200

############################################################################################################ FUNCIONARIO

@app.route("/busca_funcionario", methods=["GET"])
def listar_funcionario():
    db = get_db()
    cursor = db.execute("SELECT id_funcionario, ds_funcionario, ds_contato, dh_primeiro_agendamento, dh_ultimo_agendamento, pe_comissao FROM funcionario;")
    funcionarios = [dict(row) for row in cursor.fetchall()]
    return jsonify(funcionarios)

@app.route("/insere_funcionario", methods=["POST"])
def insere_funcionario():

    db = get_db()
    
    dados = request.get_json(silent=True) or {}

    ds_funcionario = str(dados.get("ds_funcionario") or "").strip()
    ds_contato = str(dados.get("ds_contato") or "").strip()
    dh_primeiro_agendamento = dados.get("dh_primeiro_agendamento")
    dh_ultimo_agendamento = dados.get("dh_ultimo_agendamento")
    pe_comissao = dados.get("pe_comissao")

    if ds_funcionario == None or ds_funcionario.strip() == "":
        return jsonify({"error": "O campo 'ds_funcionario' é obrigatório."}), 400
    elif ds_contato == None or ds_contato.strip() == "":
        return jsonify({"error": "O campo 'ds_funcionario' é obrigatório."}), 400

    try:
        ds_contato = formata_e_valida_telefone(ds_contato)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    query = """
        INSERT INTO funcionario (
            ds_funcionario,
            ds_contato,
            dh_primeiro_agendamento,
            dh_ultimo_agendamento,
            pe_comissao,
            dh_inclusao,
            dh_alteracao
        )
        VALUES (?, ?, ?, ?, ?, TIME('now'), TIME('now'));
    """
    
    db.execute(query, (ds_funcionario, ds_contato, dh_primeiro_agendamento, dh_ultimo_agendamento, pe_comissao))
    db.commit()

    return jsonify({"message": "Cliente inserido com sucesso!"}), 201

@app.route("/edita_funcionario/<int:id_funcionario>", methods=["PUT"])
def edita_funcionario(id_funcionario):
    db = get_db()
    
    dados = request.get_json(silent=True) or {}

    ds_funcionario = str(dados.get("ds_funcionario") or "").strip()
    ds_contato = str(dados.get("ds_contato") or "").strip()
    dh_primeiro_agendamento = dados.get("dh_primeiro_agendamento")
    dh_ultimo_agendamento = dados.get("dh_ultimo_agendamento")
    pe_comissao = dados.get("pe_comissao")

    if ds_funcionario == None or ds_funcionario.strip() == "":
        return jsonify({"error": "O campo 'ds_funcionario' é obrigatório."}), 400
    elif ds_contato == None or ds_contato.strip() == "":
        return jsonify({"error": "O campo 'ds_contato' é obrigatório."}), 400
    elif pe_comissao == None:
        pe_comissao = 0

    try:
        ds_contato = formata_e_valida_telefone(ds_contato)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    query = """
        UPDATE funcionario
        SET 
            ds_funcionario = ?, 
            ds_contato = ?, 
            dh_primeiro_agendamento = ?, 
            dh_ultimo_agendamento = ?, 
            pe_comissao = ?,
            dh_alteracao = date('now')
            WHERE id_funcionario = ?
            """

    db.execute(query, (ds_funcionario, ds_contato, dh_primeiro_agendamento, dh_ultimo_agendamento, pe_comissao, id_funcionario))
    db.commit()
    return jsonify({"message": "Funcionario atualizado com sucesso!"}), 200

@app.route("/deleta_funcionario/<int:id_funcionario>", methods=["DELETE"])
def deleta_funcionario(id_funcionario):
    db = get_db()
    
    query = """
        DELETE FROM funcionario
        WHERE id_funcionario = ?;
    """

    cursor = db.execute(query, (id_funcionario,))
    db.commit()

    if cursor.rowcount == 0:
        return jsonify({"error": "Funcionario não encontrado"}), 404

    return jsonify({"message": "Funcionario deletado com sucesso!"}), 200

############################################################################################################ AGENDAMENTO

@app.route("/insere_agendamento", methods=["POST"])
def insere_agendamento():

    db = get_db()
    
    dados = request.get_json(silent=True) or {}

    id_cliente = str(dados.get("id_cliente"))
    id_funcionario = str(dados.get("id_funcionario"))
    vl_total_bruto_agendamento = dados.get("vl_total_bruto_agendamento")
    vl_desconto_agendamento = dados.get("vl_desconto_agendamento")
    vl_gorjeta = dados.get("vl_gorjeta")
    vl_total_liquido_agendamento = dados.get("vl_total_liquido_agendamento")
    dh_agendamento = dados.get("dh_agendamento")

    if id_cliente == None:
        return jsonify({"error": "O campo 'id_cliente' é obrigatório."}), 400
    if id_funcionario == None:
        return jsonify({"error": "O campo 'id_funcionario' é obrigatório."}), 400

    ds_status = str(dados.get("ds_status")).strip().upper()
    if ds_status not in ["AGENDADO", "CANCELADO", "CONCLUIDO"]:
        return jsonify({"error": "O campo 'ds_status' deve ser 'AGENDADO', 'CANCELADO' ou 'CONCLUIDO'."}), 400
    elif ds_status == None or ds_status.strip() == "":
        ds_status = "AGENDADO"
    else:
        ds_status = ds_status

    query = """
        INSERT INTO agendamento (
            id_cliente,
            id_funcionario,
            ds_status,
            vl_total_bruto_agendamento,
            vl_desconto_agendamento,
            vl_gorjeta_agendamento,
            vl_total_liquido_agendamento,
            dh_agendamento,
            dh_inclusao,
            dh_alteracao
            )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATETIME('now'), DATETIME('now'));
    """
    
    db.execute(query,(id_cliente, id_funcionario, ds_status, vl_total_bruto_agendamento, vl_desconto_agendamento, vl_gorjeta, vl_total_liquido_agendamento, dh_agendamento))
    db.commit()

    return jsonify({"message": "Cliente inserido com sucesso!"}), 201

def busca_categoria_produto_servico(id_produto_servico):
    db = get_db()
    cursor = db.execute("SELECT ds_categoria FROM produto_servico WHERE id_produto_servico = ?", (id_produto_servico,))
    row = cursor.fetchone()
    return row["ds_categoria"] if row else None

@app.route("/remove_estoque_agendamento", methods=["PUT"])
def remove_estoque_agendamento():

    categoria = busca_categoria_produto_servico(request.get_json(silent=True).get("id_produto_servico"))
    db = get_db()
    
    dados = request.get_json(silent=True) or {}

    vl_subtracao = dados.get("vl_subtracao")
    id_produto_servico = dados.get("id_produto_servico")

    if vl_subtracao is None or vl_subtracao <= 0:
        return jsonify({"error": "O campo 'vl_subtracao' deve ser maior que zero."}), 400
    if id_produto_servico is None:
        return jsonify({"error": "O campo 'id_produto_servico' é obrigatório."}), 400

    if categoria == "PRODUTO":
        query = """
            UPDATE produto_servico
            SET qt_estoque = qt_estoque - ?,
            dh_ultima_movimentacao = DATETIME('now')
            WHERE id_produto_servico = ?
        """

        try:
            cursor = db.execute(query, (vl_subtracao, id_produto_servico))
            db.commit()
        except sql.IntegrityError as e:
            db.rollback()
            if "qt_estoque" in str(e):
                return jsonify({
                    "error": "Não é possível diminuir o estoque de um produto/serviço cujo valor ficará menor que zero."
                }), 400
            return jsonify({"error": "Erro de integridade no banco de dados."}), 400

    if categoria == "SERVICO":
        query = """
            UPDATE produto_servico
            SET dh_ultima_movimentacao = DATETIME('now')
            WHERE id_produto_servico = ?
        """

        try:
            cursor = db.execute(query, (id_produto_servico,))
            db.commit()
        except sql.IntegrityError as e:
            db.rollback()
            if "qt_estoque" in str(e):
                return jsonify({
                    "error": "Não é possível diminuir o estoque de um produto/serviço cujo valor ficará menor que zero."
                }), 400
            return jsonify({"error": "Erro de integridade no banco de dados."}), 400
    
    

    if cursor.rowcount == 0:
        return jsonify({"error": "Produto não encontrado."}), 404

    return jsonify({"message": "Estoque atualizado com sucesso!"}), 200

@app.route("/deleta_agendamento/<int:id_agendamento>", methods=["DELETE"])
def deleta_agendamento(id_agendamento):
    db = get_db()
    
    query = """
        DELETE FROM agendamento
        WHERE id_agendamento = ?;
    """

    cursor = db.execute(query, (id_agendamento,))
    db.commit()

    query_produto_servico = """
        DELETE FROM agendamento_produto_servico
        WHERE id_agendamento = ?;
        """

    cursor = db.execute(query_produto_servico, (id_agendamento,))
    db.commit()

    if cursor.rowcount == 0:
        return jsonify({"error": "Agendamento não encontrado"}), 404

    return jsonify({"message": "Agendamento deletado com sucesso!"}), 200

@app.route("/busca_agendamento", methods=["GET"])
def listar_agendamento():
    db = get_db()
    cursor = db.execute("""
        SELECT a.id_agendamento,
            a.ds_status,
            f.id_funcionario,
            f.ds_funcionario,
            c.id_cliente,
            c.ds_cliente,
            a.dh_agendamento,
            a.vl_total_liquido_agendamento
        FROM agendamento a
        JOIN funcionario f ON f.id_funcionario = a.id_funcionario
        JOIN cliente c ON c.id_cliente = a.id_cliente;""")
    funcionarios = [dict(row) for row in cursor.fetchall()]
    return jsonify(funcionarios)

@app.route("/busca_id_agendamento_insere_agendamento_produto_servico", methods=["GET"])
def busca_id_agendamento_insere_agendamento_produto_servico():    
    db = get_db()
    cursor = db.execute("SELECT MAX(id_agendamento) FROM agendamento;")
    row = cursor.fetchone()
    
    if not row or row[0] is None:
        return jsonify({"id_agendamento": None}), 200
        
    return jsonify({"id_agendamento": int(row[0])}), 200

def busca_agendamento_insere_agendamento_produto_servico():
    try:
        db = get_db()
        cursor = db.execute("SELECT MAX(id_agendamento) FROM agendamento;")
        row = cursor.fetchone()
        
        if not row or row[0] is None:
            return None
            
        return int(row[0])
    except Exception as e:
        print(f">>> ERRO NA BUSCA DO ID: {e}")
        return None

@app.route("/busca_agendamento_front/<dh_agendamento>", methods=["GET"])
def listar_agendamento_front(dh_agendamento):
    db = get_db()
    
    query = """
        SELECT
            a.ds_status,
            a.id_agendamento,
            f.ds_funcionario,
            c.ds_cliente,
            a.dh_agendamento,
            a.vl_total_liquido_agendamento
        FROM agendamento a
        JOIN funcionario f
            ON f.id_funcionario = a.id_funcionario
        JOIN cliente c
            ON c.id_cliente = a.id_cliente
        WHERE a.dh_agendamento LIKE ?
        ORDER BY a.dh_agendamento;
    """
    
    cursor = db.execute(query, (f"{dh_agendamento}%",))
    agendamento_front = [dict(row) for row in cursor.fetchall()]

    # Validação de retorno vazio
    if not agendamento_front:
        return jsonify({
            "status": "error",
            "mensagem": f"Nenhum agendamento encontrado para a data {dh_agendamento}."
        }), 404

    return jsonify(agendamento_front), 200

@app.route("/busca_agendamento_detalhes/<int:id_agendamento>", methods=["GET"])
def listar_agendamento_detalhes(id_agendamento):
    db = get_db()
    
    query = """
        SELECT a.id_agendamento,
               a.ds_status,
               a.vl_desconto_agendamento,
               a.vl_gorjeta_agendamento,
               f.ds_funcionario,
               c.ds_cliente,
              ps.ds_produto_servico,
             aps.qt_produto,
             aps.vl_unitario_produto,
             aps.vl_total_produto,
               a.dh_agendamento
        FROM agendamento_produto_servico aps
        JOIN produto_servico ps ON aps.id_produto_servico = ps.id_produto_servico
        JOIN agendamento a ON aps.id_agendamento = a.id_agendamento
        JOIN funcionario f ON a.id_funcionario = f.id_funcionario
        JOIN cliente c ON a.id_cliente = c.id_cliente
        WHERE a.id_agendamento = ?
    """
    
    cursor = db.execute(query, (id_agendamento,))
    agendamento_detalhes = [dict(row) for row in cursor.fetchall()]

    # Validação de retorno vazio
    if not agendamento_detalhes:
        return jsonify({
            "status": "error",
            "mensagem": f"Nenhum detalhe encontrado para o agendamento ID {id_agendamento}."
        }), 404

    return jsonify(agendamento_detalhes), 200

############################################################################################################ AGENDAMENTO_PRODUTO_SERVICO

@app.route("/insere_agendamento_produto_servico", methods=["POST"])
def insere_agendamento_produto_servico():
    db = get_db()
    dados = request.get_json(silent=True) or {}

    # 1. Obtém o ID (retorna int ou None)
    id_agendamento = busca_agendamento_insere_agendamento_produto_servico()

    if id_agendamento is None:
        return jsonify({"error": "Nenhum agendamento encontrado no banco."}), 400

    # 2. Extrai e trata os campos do JSON
    id_produto_servico = dados.get("id_produto_servico")
    if id_produto_servico is None:
        return jsonify({"error": "O campo 'id_produto_servico' é obrigatório."}), 400

    # Força a conversão para tipos primitivos aceitos pelo SQLite
    try:
        id_agendamento = id_agendamento
        id_produto_servico = id_produto_servico
        qt_produto = int(dados.get("qt_produto", 1))
        vl_unitario_produto = float(dados.get("vl_unitario_produto", 0.0))
        vl_total_produto = float(dados.get("vl_total_produto", 0.0))
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Erro nos tipos dos dados enviados: {str(e)}"}), 400
    # 3. Inserção no banco
    query = """
        INSERT INTO agendamento_produto_servico (
            id_agendamento,
            id_produto_servico,
            qt_produto,
            vl_unitario_produto,
            vl_total_produto,
            dh_inclusao,
            dh_alteracao
        )
        VALUES (?, ?, ?, ?, ?, DATETIME('now'), DATETIME('now'));
    """

    db.execute(query, (id_agendamento, id_produto_servico, qt_produto, vl_unitario_produto, vl_total_produto))
    db.commit()

    return jsonify({"message": "Produto/Serviço inserido no agendamento com sucesso!"}), 201

@app.route("/lanca_compra_produto", methods=["PUT"])
def lanca_compra_produto():
    db = get_db()
    dados = request.get_json(silent=True) or {}

    id_produto_servico = dados.get("id_produto_servico")
    vl_edicao = dados.get("vl_edicao")
    vl_unitario_produto_compra = dados.get("vl_unitario_produto_compra")

    if id_produto_servico is None:
        return jsonify({"error": "O campo 'id_produto_servico' é obrigatório."}), 400
    if vl_edicao is None or vl_edicao == 0:
        return jsonify({"error": "O campo 'vl_edicao' é obrigatório e deve ser diferente de zero."}), 400
    if vl_unitario_produto_compra is None or vl_unitario_produto_compra == 0:
        return jsonify({"error": "O campo 'vl_unitario_produto_compra' é obrigatório e deve ser diferente de zero."}), 400

    query = """
        UPDATE produto_servico
        SET qt_estoque = qt_estoque + ?,
            vl_unitario_produto_compra = ?,
            dh_alteracao = DATETIME('now')
        WHERE id_produto_servico = ?
    """

    db.execute(query, (vl_edicao, vl_unitario_produto_compra, id_produto_servico))
    db.commit()

    return jsonify({"message": "Estoque atualizado com sucesso!"}), 200

@app.route("/lanca_baixa_produto", methods=["PUT"])
def lanca_baixa_produto():
    db = get_db()
    dados = request.get_json(silent=True) or {}

    id_produto_servico = dados.get("id_produto_servico")
    vl_edicao = dados.get("vl_edicao")
    vl_unitario_produto_compra = dados.get("vl_unitario_produto_compra")

    if id_produto_servico is None:
        return jsonify({"error": "O campo 'id_produto_servico' é obrigatório."}), 400
    if vl_edicao is None or vl_edicao == 0:
        return jsonify({"error": "O campo 'vl_edicao' é obrigatório e deve ser diferente de zero."}), 400

    query = """
        UPDATE produto_servico
        SET qt_estoque = qt_estoque - ?,
            dh_alteracao = DATETIME('now')
        WHERE id_produto_servico = ?
    """

    db.execute(query, (vl_edicao, id_produto_servico))
    db.commit()

    return jsonify({"message": "Estoque atualizado com sucesso!"}), 200

############################################################################################################ FINANCEIRO

@app.route("/insere_financeiro", methods=["POST"])
def insere_financeiro():

    db = get_db()
    
    dados = request.get_json(silent=True) or {}

    id_agendamento = str(dados.get("id_agendamento") or "").strip()
    vl_total = str(dados.get("vl_total") or "").strip()
    
    if vl_total == None or vl_total.strip() == "":
        return jsonify({"error": "O campo 'vl_total' é obrigatório."}), 400
    if id_agendamento == None or id_agendamento.strip() == "":
        id_agendamento = "null"

    query = """
        INSERT INTO financeiro (
            id_agendamento,
            vl_total,
            dh_inclusao,
            dh_alteracao
        )
        VALUES (?, ?, TIME('now'), TIME('now'));
    """
    
    db.execute(query, (id_agendamento, vl_total))
    db.commit()

    return jsonify({"message": "Financeiro inserido com sucesso!"}), 201

@app.route("/edita_financeiro", methods=["PUT"])
def edita_financeiro():

    db = get_db()
    
    dados = request.get_json(silent=True) or {}

    id_agendamento = str(dados.get("id_agendamento") or "").strip()
    vl_total = str(dados.get("vl_total") or "").strip()
    
    if vl_total == None or vl_total.strip() == "":
        return jsonify({"error": "O campo 'vl_total' é obrigatório."}), 400
    if id_agendamento == None or id_agendamento.strip() == "":
        id_agendamento = "null"

    query = """
        UPDATE financeiro
        SET id_agendamento = ?,
            vl_total = ?,
            dh_alteracao = TIME('now')
        WHERE id_agendamento = ?
    """

    db.execute(query, (id_agendamento, vl_total, id_agendamento))
    db.commit()

    return jsonify({"message": "Financeiro atualizado com sucesso!"}), 200

############################################################################################################ DASHBOARDS

@app.route("/busca_produto_estoque_zero", methods=["GET"])
def busca_produto_estoque_zero():
    db = get_db()
    cursor = db.execute("SELECT COUNT(id_produto_servico) FROM produto_servico WHERE qt_estoque <= 0 AND ds_categoria = 'PRODUTO';")
    
    return jsonify({"contagem": cursor.fetchone()[0]})