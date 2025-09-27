# Ficheiro: settings.py (VERSÃO CORRETA PARA O TESTE)

ARQUIVO_SAVE = "projeto.json"
LARGURA_TELA, ALTURA_TELA = 1280, 720

# Tema Claro
COR_FUNDO = (240, 240, 240)
COR_RETANGULO = (255, 255, 255)
COR_RETANGULO_COM_FILHOS = (200, 220, 255)   

COR_RETANGULO_COMPLETO = (210, 245, 210)             # Verde claro (Completo)
COR_RETANGULO_DESENVOLVIMENTO = (255, 250, 205)      # Amarelo claro (Em Desenvolvimento)
COR_BORDA_RETANGULO = (0, 0, 0)
COR_TEXTO_TITULO = (20, 20, 20)
COR_TEXTO_CORPO = (20, 20, 20)   # Corpo do texto em preto, igual ao título

# Cores do Menu de Contexto
COR_MENU_FUNDO = (250, 250, 250)
COR_MENU_BORDA = (180, 180, 180)
COR_TEXTO_MENU_ATIVO = (20, 20, 20)
COR_TEXTO_MENU_INATIVO = (150, 150, 150)
COR_MENU_HOVER_FUNDO = (205, 230, 255)
COR_MENU_HOVER_TEXTO = (0, 0, 0)

LARGURA_RETANGULO_ABS = int(LARGURA_TELA * 0.15)
ALTURA_RETANGULO_ABS = int(LARGURA_TELA * 0.12)
TAMANHO_RETANGULO = (LARGURA_RETANGULO_ABS, ALTURA_RETANGULO_ABS)

# Fontes
TAMANHO_FONTE_TITULO = 18
TAMANHO_FONTE_MENU = 16
PADDING_TITULO_ELIPSE = 5

# Configurações do Menu de Contexto
MENU_PADDING_ABS = int(LARGURA_TELA * 0.008)
MENU_MIN_WIDTH_ABS = int(LARGURA_TELA * 0.12)
MENU_ITEM_SPACING = 5

# Constante para detetar o duplo-clique (em milissegundos)
DOUBLE_CLICK_TIME = 500 

# Configurações da Janela Modal
MODAL_WIDTH_REL = 0.6
MODAL_HEIGHT_REL = 0.7

# Botão de Fechar (X)
MODAL_CLOSE_BUTTON_SIZE = 30
MODAL_CLOSE_BUTTON_MARGIN = 10
MODAL_CLOSE_X_COLOR_NORMAL = (20, 20, 20)
MODAL_CLOSE_X_COLOR_HOVER = (255, 255, 255)
MODAL_CLOSE_BG_COLOR_HOVER = (255, 100, 100)

# ### ATUALIZADO: Configurações do Botão Concluído (Versão Final) ###
MODAL_DONE_BUTTON_WIDTH = 100
MODAL_DONE_BUTTON_HEIGHT = 30
MODAL_DONE_BUTTON_MARGIN = 15
MODAL_DONE_BG_COLOR_NORMAL = (225, 225, 225)      # Cinza claro sólido
MODAL_DONE_BG_COLOR_HOVER = (200, 200, 200)       # Cinza um pouco mais escuro para o hover
MODAL_DONE_BORDER_COLOR = (0, 0, 0)                # Cor da borda preta
MODAL_DONE_BORDER_WIDTH = 2          # Borda BEM grossa para o teste

# Configurações dos Campos de Edição
MODAL_INPUT_BG_COLOR = (255, 255, 255)
MODAL_INPUT_BORDER_INACTIVE = (180, 180, 180)
MODAL_INPUT_BORDER_ACTIVE = (0, 120, 215)
MODAL_INPUT_PADDING = 10
CURSOR_BLINK_RATE = 500

# Ficheiro: settings.py (ADICIONE ÀS CONSTANTES DE FONTE)

# Fontes
TAMANHO_FONTE_TITULO = 18
TAMANHO_FONTE_CORPO = 16 # ### NOVO
TAMANHO_FONTE_MENU = 16
PADDING_TITULO_ELIPSE = 5
# ### ADICIONE ESTA CONSTANTE ###
MODAL_BODY_SCROLL_SPEED = 20 # pixels por "tick" da roda do rato
# ### NOVO: Configurações da Scrollbar ###
SCROLLBAR_WIDTH = 15
SCROLLBAR_PADDING = 3                   # ### ADICIONE ESTA LINHA ###
SCROLLBAR_TRACK_COLOR = (220, 220, 220)
SCROLLBAR_THUMB_COLOR = (160, 160, 160)
SCROLLBAR_MIN_THUMB_HEIGHT = 20
# Ficheiro: settings.py (ADICIONE AO FINAL)

# ### NOVO: Configurações da Lista de Navegação (Tree View) ###
TREE_VIEW_X_START = 15      # Posição X inicial da lista
TREE_VIEW_Y_START = 15      # Posição Y inicial da lista
TREE_INDENT_WIDTH = 20      # Espaço de indentação por cada nível
TREE_MAX_CHARS = 30         # Máximo de caracteres a mostrar por título
TREE_FONT_SIZE = 16
TREE_LINE_SPACING = 20      # Espaço vertical entre cada item