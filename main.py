import flet as ft
import os
import sqlite3
import sys

usuario = os.getlogin()

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

    # Função para conectar ao banco de dados
    def conectar_banco():
        try:
            diretorio_raiz = os.path.dirname(os.path.abspath(__file__))
            caminho_banco = os.path.join(diretorio_raiz, 'consultor.db')
            
            if not os.path.exists(caminho_banco):
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("⚠ Banco de dados não encontrado!", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED_700,
                )
                page.snack_bar.open = True
                page.update()
                return None
            
            return sqlite3.connect(caminho_banco)
        except sqlite3.Error as e:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✗ Erro ao conectar: {e}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700,
            )
            page.snack_bar.open = True
            page.update()
            return None

    # Função para buscar dados do banco
    def buscar_dados(filtro=''):
        conn = conectar_banco()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            if filtro:
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
                '''
                filtro_like = f'%{filtro}%'
                cursor.execute(query, tuple([filtro_like] * 6))
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
            conn.close()
            return dados
        except sqlite3.Error as e:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✗ Erro ao buscar dados: {e}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700,
            )
            page.snack_bar.open = True
            page.update()
            conn.close()
            return []

    anchor = ft.SearchBar(
        view_elevation=4,
        divider_color=ft.Colors.BLUE_100,
        bar_hint_text="Contrato, CNPJ, E-mail, RAIZ CNPJ e Etc...",
        expand=True,
        on_submit=lambda e: atualizar_tabela(e.control.value),
    )

    # AppBar Barra superior
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
                ft.Image(
                    src="assets/logo1.png",
                    width=40,
                    height=40,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Text(
                    f"Olá, {usuario}!",
                    size=20,
                    weight="bold",
                    color=ft.Colors.WHITE,
                    text_align="right",
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Seja bem Vindo, ao App Consultor!",
                            size=20,
                            weight="bold",
                            color=ft.Colors.WHITE,
                            text_align="center",
                        )
                    ],
                    expand=True,
                ),
                ft.Image(
                    src="assets/logo2.png",
                    width=60,
                    height=60,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Container(width=30),
            ]
        )
    )

    # Função para copiar célula individual
    def copiar_celula(e, valor):
        page.set_clipboard(str(valor))
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"✓ Valor copiado: {valor}", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN_700,
        )
        page.snack_bar.open = True
        page.update()

    # Container para a tabela
    table_container = ft.Container()

    # Função para criar a tabela
    def criar_tabela(dados):
        if not dados:
            return ft.Container(
                content=ft.Text(
                    "Nenhum registro encontrado",
                    size=16,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER
                ),
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
                                padding=ft.padding.symmetric(horizontal=4, vertical=4)
                            ),
                            on_tap=lambda e, v=col: copiar_celula(e, v) if v else None
                        )
                        for col in row
                    ],
                    selected=False,
                ) for row in dados
            ]
        )
    # Função para atualizar a tabela
    def atualizar_tabela(filtro=''):
        dados = buscar_dados(filtro)
        table_container.content = criar_tabela(dados)
        
        if dados:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✓ {len(dados)} registro(s) encontrado(s)", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLUE_700,
            )
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Nenhum registro encontrado", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.ORANGE_700,
            )
        
        page.snack_bar.open = True
        page.update()

    # Função de pesquisa
    def pesquisar(e):
        atualizar_tabela(anchor.value)

    # Row com barra de pesquisa + botão
    search_row = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        controls=[
            ft.Container(anchor, expand=True),
            ft.Container(
                content=ft.OutlinedButton(
                    content=ft.Text("Pesquisar", size=20, weight="bold"),
                    on_click=pesquisar,
                    width=150,
                    height=55,
                ),
            )
        ]
    )

    # Carrega dados iniciais
    dados_iniciais = buscar_dados()
    table_container.content = criar_tabela(dados_iniciais)

    # Container com scroll para a tabela
    scroll_table = ft.Container(
        content=ft.Column(
            controls=[table_container],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        expand=True,
        padding=5,
    )

    # Footer com copyright
    footer = ft.Container(
        alignment=ft.alignment.center,
        padding=ft.padding.all(10),
        content=ft.Text(
            "© MISNEOBPO2025",
            size=14,
            color=ft.Colors.BLACK87,
            italic=False
        )
    )

    page.add(search_row, scroll_table, footer)

ft.app(target=main)