import sqlite3
import os

def criar_banco():
    """Cria o banco de dados SQLite na raiz do projeto"""
    
    # Obtém o diretório do script atual (raiz do projeto)
    diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
    caminho_banco = os.path.join(diretorio_raiz, 'consultor.db')
    
    print(f"Criando banco de dados em: {caminho_banco}")
    
    # Conecta ao banco (cria se não existir)
    conn = sqlite3.connect(caminho_banco)
    cursor = conn.cursor()
    
    # Cria a tabela tb_base_contrato_consultor
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tb_base_contrato_consultor (
            data_atualizacao TEXT,
            contrato TEXT,
            tipo_mercado TEXT,
            tipo_venda TEXT,
            produto TEXT,
            safra TEXT,
            dt_safra TEXT,
            razao_social TEXT,
            cnpj TEXT,
            raiz TEXT,
            municipio TEXT,
            estado TEXT,
            grupo_vendedor TEXT,
            agencia TEXT,
            cod_cnae TEXT,
            des_cnae TEXT,
            cod_setor TEXT,
            des_setor TEXT,
            cod_sub_setor TEXT,
            des_sub_setor TEXT,
            canal_entrada TEXT,
            vendedor_pf TEXT,
            dt_prim_fat TEXT,
            dt_ult_fat TEXT,
            forma_pgto TEXT,
            dias_prazo_pagto TEXT,
            grupo_rel TEXT,
            agencia_grupo_rel TEXT,
            cod_cnae_grupo_rel TEXT,
            des_cnae_grupo_rel TEXT,
            cod_setor_grupo_rel TEXT,
            des_setor_grupo_rel TEXT,
            cod_sub_setor_grupo_rel TEXT,
            des_sub_setor_grupo_rel TEXT,
            segmento_comercial TEXT,
            segmento_analitycs TEXT,
            segmento_bradesco TEXT,
            segmento_bb TEXT,
            diretor TEXT,
            superintendente TEXT,
            gerente_nacional TEXT,
            gerente_regional TEXT,
            consultor TEXT,
            matricula TEXT,
            email TEXT,
            contato TEXT,
            carteira TEXT,
            id_grupo_rel TEXT,
            segmento_grupo_rel TEXT,
            consultor_hunter_auto TEXT,
            cancelamento_de_contrato_renegociacao_de_tarifas TEXT,
            interesse_em_novos_produtos_prospects TEXT
        )
    ''')
    
    # Cria índices para melhorar a performance das buscas
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_contrato 
        ON tb_base_contrato_consultor(contrato)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_cnpj 
        ON tb_base_contrato_consultor(cnpj)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_raiz 
        ON tb_base_contrato_consultor(raiz)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_email 
        ON tb_base_contrato_consultor(email)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_razao_social 
        ON tb_base_contrato_consultor(razao_social)
    ''')
    
    # Cria a tabela de log de importações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS log_importacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arquivo TEXT,
            registros_inseridos INTEGER,
            registros_atualizados INTEGER,
            data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    
    # Verifica quantos registros existem
    cursor.execute('SELECT COUNT(*) FROM tb_base_contrato_consultor')
    total = cursor.fetchone()[0]
    
    print(f"\n{'='*60}")
    print(f"✓ Banco de dados criado com sucesso!")
    print(f"✓ Tabela: tb_base_contrato_consultor")
    print(f"✓ Total de colunas: 51")
    print(f"✓ Índices criados para: contrato, cnpj, raiz, email, razao_social")
    print(f"✓ Total de registros no banco: {total}")
    print(f"\nArquivo criado: consultor.db")
    print(f"Localização: {caminho_banco}")
    print(f"{'='*60}\n")
    
    conn.close()

if __name__ == "__main__":
    criar_banco()