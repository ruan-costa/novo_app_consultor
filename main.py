import flet as ft
import os
import sqlite3
import sys
import atexit
import asyncio

usuario = os.getlogin()

# Lista global para controlar conexões ativas
_conexoes_globais = []

# Registra limpeza automática ao sair
def cleanup_final():
    """Garante que tudo seja fechado ao sair"""
    for conn in _conexoes_globais:
        try:
            conn.close()
        except:
            pass
    _conexoes_globais.clear()
    
atexit.register(cleanup_final)

def main(page: ft.Page):
    page.title = "App Consultor"
    page.window.width = 1400
    page.window.height = 800
    page.window.resizable = True

    # Determina o caminho correto dos assets
    if getattr(sys, 'frozen', False):
        # Rodando como EXE
        base_path = sys._MEIPASS
    else:
        # Rodando como script Python
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    icon_path = os.path.join(base_path, "assets", "logo.ico")
    page.window.icon = icon_path
    
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE,
            on_surface=ft.Colors.BLACK,
        )
    )

    # Função para limpar recursos ao fechar
    def limpar_recursos(e=None):
        """Limpa todas as conexões ativas antes de fechar"""
        try:
            for conn in _conexoes_globais:
                try:
                    conn.close()
                except:
                    pass
            _conexoes_globais.clear()
        except:
            pass
        finally:
            try:
                page.window.destroy()
            except:
                pass
            os._exit(0)

    page.window.on_event = lambda e: limpar_recursos() if e.data == "close" else None
    page.window.prevent_close = False

    # Função para conectar ao banco de dados
    def conectar_banco():
        try:
            if getattr(sys, 'frozen', False):
                diretorio_raiz = os.path.dirname(sys.executable)
            else:
                diretorio_raiz = os.path.dirname(os.path.abspath(__file__))

            caminho_banco = os.path.join(diretorio_raiz, "consultor.db")

            if not os.path.exists(caminho_banco):
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠ Banco de dados não encontrado!", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED_700,
                )
                page.snack_bar.open = True
                page.update()
                return None
            
            conn = sqlite3.connect(
                caminho_banco,
                timeout=30.0,
                check_same_thread=False,
            )
            
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA cache_size=10000")
            
            _conexoes_globais.append(conn)
            return conn
            
        except sqlite3.Error as e:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✗ Erro ao conectar: {e}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700,
            )
            page.snack_bar.open = True
            page.update()
            return None

    # Função para buscar dados do banco com filtro específico
    def buscar_dados(filtro='', campo_filtro='todos'):
        conn = conectar_banco()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            if filtro:
                # Mapeamento dos campos
                campos_map = {
                    'contrato': 'contrato',
                    'cnpj': 'cnpj',
                    'raiz': 'raiz',
                    'razao_social': 'razao_social',
                    'consultor': 'consultor',
                    'email': 'email'
                }
                
                if campo_filtro == 'todos':
                    # Busca em todos os campos (comportamento antigo)
                    query = '''
                        SELECT 
                            ROWID as id,
                            contrato,
                            razao_social,
                            cnpj,
                            raiz,
                            consultor,
                            contato,
                            email,
                            municipio,
                            estado,
                            produto
                        FROM tb_base_contrato_consultor
                        WHERE contrato LIKE ? 
                           OR cnpj LIKE ? 
                           OR consultor LIKE ?
                           OR razao_social LIKE ? 
                           OR email LIKE ?
                           OR raiz LIKE ?
                        LIMIT 1000
                    '''
                    filtro_like = f'{filtro}%'
                    cursor.execute(query, tuple([filtro_like]*6))
                else:
                    # Busca específica no campo selecionado
                    campo_db = campos_map.get(campo_filtro, 'contrato')
                    query = f'''
                        SELECT 
                            ROWID as id,
                            contrato,
                            razao_social,
                            cnpj,
                            raiz,
                            consultor,
                            contato,
                            email,
                            municipio,
                            estado,
                            produto
                        FROM tb_base_contrato_consultor
                        WHERE {campo_db} LIKE ?
                        LIMIT 1000
                    '''
                    filtro_like = f'{filtro}%'
                    cursor.execute(query, (filtro_like,))
            else:
                query = '''
                    SELECT 
                        ROWID as id,
                        contrato,
                        razao_social,
                        cnpj,
                        raiz,
                        consultor,
                        contato,
                        email,
                        municipio,
                        estado,
                        produto
                    FROM tb_base_contrato_consultor
                    LIMIT 100
                '''
                cursor.execute(query)
            
            dados = cursor.fetchall()
            return dados
            
        except sqlite3.Error as e:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✗ Erro ao buscar dados: {e}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700,
            )
            page.snack_bar.open = True
            page.update()
            return []
        finally:
            if conn:
                try:
                    conn.close()
                    if conn in _conexoes_globais:
                        _conexoes_globais.remove(conn)
                except:
                    pass

    # Dropdown para seleção do campo de filtro
    filtro_dropdown = ft.Dropdown(
        width=200,
        label="Filtrar por",
        value="contrato",
        options=[
            ft.dropdown.Option("contrato", "Contrato"),
            ft.dropdown.Option("cnpj", "CNPJ"),
            ft.dropdown.Option("raiz", "Raiz CNPJ"),
            ft.dropdown.Option("razao_social", "Razão Social"),
            ft.dropdown.Option("consultor", "Consultor"),
            ft.dropdown.Option("email", "E-mail"),
        ],
        text_size=14,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.BLUE,
        border_radius=10,
    )

    anchor = ft.TextField(
        hint_text="Digite o valor para pesquisar...",
        expand=True,
        text_size=16,
        border_color=ft.Colors.BLUE,
        focused_border_color=ft.Colors.BLUE,
        border_radius=10,
        on_submit=lambda e: asyncio.run(atualizar_tabela_async(e.control.value, filtro_dropdown.value)),
    )

    # AppBar
    page.appbar = ft.Container(
        height=60,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=20),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#071437", "#1b84ff"]
        ),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Image(src="assets/logo1.png", width=40, height=40, fit=ft.ImageFit.CONTAIN),
                ft.Text(f"Olá, {usuario}!", size=20, weight="bold", color=ft.Colors.WHITE),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[ft.Text("Seja bem Vindo, ao App Consultor!", size=20, weight="bold", color=ft.Colors.WHITE)],
                    expand=True,
                ),
                ft.Image(src="assets/logo2.png", width=60, height=60, fit=ft.ImageFit.CONTAIN),
                ft.Container(width=30),
            ]
        )
    )

    # Copiar célula
    def copiar_celula(e, valor):
        page.set_clipboard(str(valor))
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"✓ Valor copiado: {valor}", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_700,
        )
        page.snack_bar.open = True
        page.update()

    # Container tabela
    table_container = ft.Container()

    # Dialog de loading
    loading_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Container(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
                controls=[
                    ft.ProgressRing(width=50, height=50),
                    ft.Container(height=10),
                    ft.Text("Aguarde, buscando dados...", size=16, weight="bold"),
                ],
            ),
            padding=20,
        ),
    )

    # Criar tabela
    def criar_tabela(dados):
        if not dados:
            return ft.Container(
                content=ft.Text("Nenhum registro encontrado", size=16, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center,
                padding=10
            )
        return ft.DataTable(
            border=ft.border.all(0.5, ft.Colors.BLACK38),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(0.5, ft.Colors.BLACK38),
            horizontal_lines=ft.border.BorderSide(0.5, ft.Colors.BLACK38),
            show_checkbox_column=True,
            heading_row_height=50,
            data_row_max_height=60,
            data_row_min_height=40,
            column_spacing=10,
            horizontal_margin=5,
            columns=[
                ft.DataColumn(ft.Text("ID", weight="bold", no_wrap=True), numeric=True),
                ft.DataColumn(ft.Text("Contrato", weight="bold", no_wrap=True)),
                ft.DataColumn(ft.Text("Razão Social", weight="bold", no_wrap=True)),
                ft.DataColumn(ft.Text("CNPJ", weight="bold", no_wrap=True)),
                ft.DataColumn(ft.Text("Raiz CNPJ", weight="bold", no_wrap=True)),
                ft.DataColumn(ft.Text("Consultor", weight="bold", no_wrap=True)),
                ft.DataColumn(ft.Text("Contato", weight="bold", no_wrap=True)),
                ft.DataColumn(ft.Text("E-mail", weight="bold", no_wrap=True)),
                ft.DataColumn(ft.Text("Cidade", weight="bold", no_wrap=True)),
                ft.DataColumn(ft.Text("Estado", weight="bold", no_wrap=True)),
                ft.DataColumn(ft.Text("Produto", weight="bold", no_wrap=True)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(col) if col else "", no_wrap=True, size=13),
                                padding=ft.padding.symmetric(horizontal=4, vertical=4),
                                tooltip="Clique para copiar"
                            ),
                            on_tap=lambda e, v=col: copiar_celula(e, v) if v else None
                        )
                        for col in row
                    ],
                    selected=False,
                ) for row in dados
            ]
        )

    # Função assíncrona para atualizar tabela
    async def atualizar_tabela_async(filtro='', campo_filtro='todos'):
        page.dialog = loading_dialog
        loading_dialog.open = True
        page.update()
        try:
            loop = asyncio.get_event_loop()
            dados = await loop.run_in_executor(None, lambda: buscar_dados(filtro, campo_filtro))
            table_container.content = criar_tabela(dados)
            if dados:
                campo_texto = filtro_dropdown.options[[opt.key for opt in filtro_dropdown.options].index(campo_filtro)].text
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✓ {len(dados)} registro(s) encontrado(s) em '{campo_texto}'", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.BLUE_700,
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Nenhum registro encontrado", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.ORANGE_700,
                )
            page.snack_bar.open = True
        finally:
            loading_dialog.open = False
            page.update()

    # Botão pesquisar
    def pesquisar(e):
        asyncio.run(atualizar_tabela_async(anchor.value, filtro_dropdown.value))

    search_row = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=10,
        controls=[
            ft.Container(
                content=filtro_dropdown,
                height=56,
            ),
            ft.Container(
                content=anchor,
                expand=True,
                height=56,
            ),
            ft.Container(
                content=ft.OutlinedButton(
                    content=ft.Text("Pesquisar", size=18, weight="bold"),
                    on_click=pesquisar,
                    width=150,
                    height=45,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        side=ft.BorderSide(1, ft.Colors.BLUE),
                    ),
                ),
                height=48,
            )
        ]
    )

    # Dados iniciais
    dados_iniciais = buscar_dados()
    table_container.content = criar_tabela(dados_iniciais)

    scroll_table = ft.Container(
        content=ft.Column(
            controls=[table_container],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        expand=True,
        padding=5,
    )

    footer = ft.Container(
        alignment=ft.alignment.center,
        padding=ft.padding.all(10),
        content=ft.Text("© MISNEOHYPE2025", size=14, color=ft.Colors.BLACK87)
    )

    page.add(search_row, scroll_table, footer)

if __name__ == "__main__":
    try:
        ft.app(target=main)
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        sys.exit(0)