# 📊 App Consultor

Aplicação desktop desenvolvida em Python com Flet para consulta e visualização de dados de contratos e consultores, com sincronização automática de banco de dados SQL Server para SQLite local.

## 🎯 Funcionalidades

- ✅ Interface gráfica moderna e responsiva
- 🔍 Busca avançada por múltiplos campos (Contrato, CNPJ, E-mail, Razão Social, Consultor, Raiz CNPJ)
- 📋 Visualização em tabela com dados organizados
- 📄 Cópia rápida de células individuais com um clique
- 🔄 Sincronização de dados SQL Server → SQLite
- 📊 Visualização de até 100 registros iniciais (ou todos com filtro)
- 🎨 Design moderno com gradientes e tema personalizado

## 🖥️ Tecnologias Utilizadas

- **Python 3.x**
- **Flet** - Framework para interface gráfica
- **SQLite3** - Banco de dados local
- **PyODBC** - Conexão com SQL Server
- **PyInstaller** - Geração de executável

## 📋 Pré-requisitos

```bash
Python 3.8 ou superior
pip (gerenciador de pacotes Python)
Acesso à rede para conexão com SQL Server (10.223.241.20)
Windows Authentication habilitada
```

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd NOVO_APP_CONSULTOR
```

### 2. Crie e ative o ambiente virtual

```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure os assets

Certifique-se de que a pasta `assets/` contém:
- `logo.ico` - Ícone da aplicação
- `logo1.png` - Logo principal
- `logo2.png` - Logo secundário

## 📦 Estrutura do Projeto

```
NOVO_APP_CONSULTOR/
│
├── assets/
│   ├── logo.ico
│   ├── logo1.png
│   └── logo2.png
│
├── main.py                 # Aplicação principal
├── sincronizar.py          # Script de sincronização
├── criar_banco.py          # Criação do banco SQLite (se necessário)
├── consultor.db            # Banco de dados local (gerado)
├── requirements.txt        # Dependências Python
├── .gitignore             # Arquivos ignorados pelo Git
└── README.md              # Este arquivo
```

## 🔧 Configuração

### Banco de Dados SQL Server

Edite o arquivo `sincronizar.py` se necessário:

```python
SQL_SERVER = '10.223.241.20'
SQL_DATABASE = 'DB_ALELO'
SQL_TABLE = 'tb_base_contrato_consultor'
```

### Primeira Execução

1. Execute a sincronização para criar/popular o banco local:

```bash
python sincronizar.py
```

2. Execute a aplicação:

```bash
python main.py
```

## 📖 Como Usar

### Pesquisa

1. Digite no campo de busca: Contrato, CNPJ, E-mail, Razão Social, Consultor ou Raiz CNPJ
2. Pressione **Enter** ou clique em **Pesquisar**
3. Os resultados aparecem na tabela abaixo

### Copiar Dados

- Clique em qualquer célula da tabela para copiar seu conteúdo
- Uma notificação confirmará a cópia

### Sincronização de Dados

Execute periodicamente para atualizar os dados:

```bash
python sincronizar.py
```

**Atenção:** Este processo irá:
- ✓ Conectar ao SQL Server via Windows Authentication
- ✓ Buscar todos os dados atualizados
- ⚠️ **TRUNCAR (limpar)** a tabela local
- ✓ Inserir os dados atualizados

## 🏗️ Gerar Executável

Para criar um arquivo `.exe` standalone:

```bash
pyinstaller --onefile --windowed --icon=assets/logo.ico --add-data "assets;assets" main.py
```

O executável será gerado em `dist/main.exe`

## 📊 Campos da Tabela

| Campo | Descrição |
|-------|-----------|
| **ID** | Identificador único |
| **Contrato** | Número do contrato |
| **Razão Social** | Nome da empresa |
| **CNPJ** | CNPJ completo |
| **Raiz CNPJ** | Raiz do CNPJ |
| **Consultor** | Nome do consultor responsável |
| **Contato** | Telefone/contato |
| **E-mail** | E-mail de contato |
| **Cidade** | Município |
| **Estado** | UF |
| **Produto** | Produto/serviço contratado |

## ⚙️ Funcionalidades Técnicas

### Interface
- Responsiva e ajustável (1400x800 padrão)
- Tema azul com gradientes
- AppBar personalizada com logo e saudação
- Footer com copyright

### Tabela
- Padding interno reduzido (4px)
- Sem quebra de texto (`no_wrap`)
- Bordas e linhas divisórias
- Checkbox para seleção múltipla
- Altura de linhas otimizada

### Banco de Dados
- Consultas otimizadas com LIKE para múltiplos campos
- Limite de 100 registros sem filtro (performance)
- Transações em lote para sincronização rápida
- Log de importações

## 🐛 Solução de Problemas

### Banco de dados não encontrado
```bash
# Execute primeiro:
python criar_banco.py
python sincronizar.py
```

### Erro de conexão SQL Server
- Verifique conectividade de rede
- Confirme Windows Authentication habilitada
- Teste acesso manual ao servidor

### Aplicação não abre
- Verifique se as imagens em `assets/` existem
- Confirme que `consultor.db` foi criado
- Execute via terminal para ver erros

## 👥 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📝 Licença

© MISNEOBPO2025 - Todos os direitos reservados

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no repositório
- Entre em contato com a equipe de desenvolvimento

---

