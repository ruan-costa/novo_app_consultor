import pyodbc
import sqlite3
import os
from datetime import datetime

# Configurações do SQL Server
SQL_SERVER = '10.223.141.20'  # Ex: 'localhost' ou '192.168.1.100'
SQL_DATABASE = 'DB_ALELO'
SQL_TABLE = 'tb_base_contrato_consultor'

# Configurações do SQLite
SQLITE_DB = 'consultor.db'

def conectar_sqlserver():
    """Conecta ao SQL Server usando Windows Authentication (Trusted Connection)"""
    try:
        connection_string = (
            f'DRIVER={{SQL Server}};'
            f'SERVER={SQL_SERVER};'
            f'DATABASE={SQL_DATABASE};'
            f'Trusted_Connection=yes;'
        )
        
        print(f"Conectando ao SQL Server: {SQL_SERVER}...")
        conn = pyodbc.connect(connection_string, timeout=30)
        print("✓ Conectado ao SQL Server com sucesso!")
        return conn
    except pyodbc.Error as e:
        print(f"✗ Erro ao conectar ao SQL Server: {e}")
        return None

def conectar_sqlite():
    """Conecta ao banco SQLite local"""
    try:
        diretorio_raiz = r'\\fileserver\Operacoes\Alelo\Alelo_PAT\MIS' #os.path.dirname(os.path.abspath(__file__))
        caminho_banco = os.path.join(diretorio_raiz, SQLITE_DB)
        
        if not os.path.exists(caminho_banco):
            print(f"✗ Erro: Banco de dados '{SQLITE_DB}' não encontrado!")
            print(f"   Execute 'criar_banco.py' primeiro.")
            return None
        
        print(f"Conectando ao SQLite: {caminho_banco}...")
        conn = sqlite3.connect(caminho_banco)
        print("✓ Conectado ao SQLite com sucesso!")
        return conn
    except sqlite3.Error as e:
        print(f"✗ Erro ao conectar ao SQLite: {e}")
        return None

def buscar_dados_sqlserver(conn):
    """Busca todos os dados da tabela no SQL Server"""
    try:
        cursor = conn.cursor()
        query = f"SELECT * FROM {SQL_TABLE}"
        
        print(f"\nBuscando dados de [{SQL_TABLE}]...")
        cursor.execute(query)
        
        # Obtém os nomes das colunas
        colunas = [column[0] for column in cursor.description]
        
        # Busca todos os registros
        dados = cursor.fetchall()
        
        print(f"✓ {len(dados)} registros encontrados")
        print(f"✓ {len(colunas)} colunas")
        
        return colunas, dados
    except pyodbc.Error as e:
        print(f"✗ Erro ao buscar dados: {e}")
        return None, None

def truncar_tabela_sqlite(conn):
    """Trunca (limpa) a tabela no SQLite"""
    try:
        cursor = conn.cursor()
        print(f"\nLimpando tabela {SQL_TABLE} no SQLite...")
        cursor.execute(f"DELETE FROM {SQL_TABLE}")
        conn.commit()
        print("✓ Tabela truncada com sucesso!")
        return True
    except sqlite3.Error as e:
        print(f"✗ Erro ao truncar tabela: {e}")
        return False

def inserir_dados_sqlite(conn, colunas, dados):
    """Insere os dados no SQLite"""
    try:
        cursor = conn.cursor()
        
        # Monta o SQL de inserção
        placeholders = ','.join(['?' for _ in colunas])
        colunas_str = ','.join(colunas)
        insert_sql = f"INSERT INTO {SQL_TABLE} ({colunas_str}) VALUES ({placeholders})"
        
        print(f"\nInserindo {len(dados)} registros no SQLite...")
        
        # Insere em lotes para melhor performance
        batch_size = 1000
        total_inserido = 0
        
        for i in range(0, len(dados), batch_size):
            batch = dados[i:i + batch_size]
            cursor.executemany(insert_sql, batch)
            conn.commit()
            total_inserido += len(batch)
            print(f"  Progresso: {total_inserido}/{len(dados)} registros ({(total_inserido/len(dados)*100):.1f}%)")
        
        print(f"✓ {total_inserido} registros inseridos com sucesso!")
        return True
    except sqlite3.Error as e:
        print(f"✗ Erro ao inserir dados: {e}")
        conn.rollback()
        return False

def registrar_log(conn_sqlite, total_registros):
    """Registra o log da sincronização"""
    try:
        cursor = conn_sqlite.cursor()
        cursor.execute('''
            INSERT INTO log_importacoes (arquivo, registros_inseridos, registros_atualizados)
            VALUES (?, ?, ?)
        ''', (f'SQL Server - {SQL_TABLE}', total_registros, 0))
        conn_sqlite.commit()
    except sqlite3.Error as e:
        print(f"⚠ Aviso: Não foi possível registrar log: {e}")

def sincronizar():
    """Função principal de sincronização"""
    print("="*70)
    print("  SINCRONIZAÇÃO SQL SERVER → SQLite")
    print("="*70)
    print(f"Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    # Conecta ao SQL Server
    conn_sqlserver = conectar_sqlserver()
    if not conn_sqlserver:
        return
    
    # Conecta ao SQLite
    conn_sqlite = conectar_sqlite()
    if not conn_sqlite:
        conn_sqlserver.close()
        return
    
    try:
        # Busca dados do SQL Server
        colunas, dados = buscar_dados_sqlserver(conn_sqlserver)
        if dados is None:
            return
        
        # Trunca a tabela no SQLite
        if not truncar_tabela_sqlite(conn_sqlite):
            return
        
        # Insere os dados no SQLite
        if inserir_dados_sqlite(conn_sqlite, colunas, dados):
            # Registra log
            registrar_log(conn_sqlite, len(dados))
            
            print("\n" + "="*70)
            print("  ✓ SINCRONIZAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*70)
            print(f"Total de registros sincronizados: {len(dados)}")
            print(f"Término: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print("="*70 + "\n")
    
    except Exception as e:
        print(f"\n✗ Erro durante a sincronização: {e}")
    
    finally:
        # Fecha as conexões
        conn_sqlserver.close()
        conn_sqlite.close()
        print("Conexões fechadas.")

if __name__ == "__main__":
    # Pergunta confirmação antes de executar
    print("\n⚠ ATENÇÃO: Este script irá:")
    print("  1. Conectar ao SQL Server (Trusted Connection)")
    print("  2. Buscar todos os dados de tb_base_contrato_consultor")
    print("  3. TRUNCAR (limpar) a tabela no SQLite")
    print("  4. Inserir os dados atualizados\n")
    
    #resposta = input("Deseja continuar? (S/N): ").strip().upper()
    
    #if resposta == 'S':
    sincronizar()
    #else:
    #    print("\n✗ Operação cancelada pelo usuário.\n")