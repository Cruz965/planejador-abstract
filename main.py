import pygame
import sys
import json
import os
from task import TaskNode 
# --- CONFIGURACOES E CONSTANTES --- (Sem alterações)
ARQUIVO_SAVE = "projeto.json"
LARGURA_TELA, ALTURA_TELA = 1280, 720
COR_FUNDO = (240, 240, 240)
COR_RETANGULO = (255, 255, 255)
COR_BORDA_RETANGULO = (0, 0, 0)
COR_TEXTO_TITULO = (20, 20, 20)
COR_TEXTO_CORPO = (80, 80, 80)
COR_MENU_FUNDO = (250, 250, 250)
COR_MENU_BORDA = (180, 180, 180)
COR_TEXTO_MENU_ATIVO = (20, 20, 20)
COR_TEXTO_MENU_INATIVO = (150, 150, 150)
COR_MENU_HOVER_FUNDO = (205, 230, 255)
COR_MENU_HOVER_TEXTO = (0, 0, 0)
LARGURA_RETANGULO_ABS = int(LARGURA_TELA * 0.15)
ALTURA_RETANGULO_ABS = int(ALTURA_TELA * 0.12)
TAMANHO_RETANGULO = (LARGURA_RETANGULO_ABS, ALTURA_RETANGULO_ABS)
TAMANHO_FONTE_TITULO = 18
TAMANHO_FONTE_MENU = 16
PADDING_TITULO_ELIPSE = 5
MENU_PADDING_ABS = int(LARGURA_TELA * 0.008)
MENU_MIN_WIDTH_ABS = int(LARGURA_TELA * 0.12)
MENU_ITEM_SPACING = 5
ARQUIVO_SAVE = "projeto.json"
# --- INICIALIZAÇÃO --- (Sem alterações)
pygame.init()
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Planejador de Abstração")
fonte_titulo = pygame.font.Font(None, TAMANHO_FONTE_TITULO)
fonte_menu = pygame.font.Font(None, TAMANHO_FONTE_MENU)

# --- FUNÇÕES DE SALVAR E CARREGAR (COM A CORREÇÃO) ---
def salvar_projeto(node, filename):
    """Salva a árvore de tarefas a partir do nó raiz em um arquivo JSON."""
    data = node.to_dict()
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Projeto salvo em {filename}")

def carregar_projeto(filename):
    """Carrega a árvore de tarefas de um arquivo JSON. Se não existir, cria uma nova."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Projeto carregado de {filename}")
        # --- MUDANÇA AQUI: Passamos TAMANHO_RETANGULO como argumento ---
        return TaskNode.from_dict(data, TAMANHO_RETANGULO)
    else:
        print("Nenhum arquivo de save encontrado. Criando novo projeto.")
        root = TaskNode("Raiz", "Nó raiz do sistema")
        tarefa_inicial = TaskNode("Meu Primeiro Projeto", "Clique com o direito para começar.", parent=root, pos=(20, 20), size=TAMANHO_RETANGULO)
        root.add_child(tarefa_inicial)
        return root

# --- ESTRUTURA DE DADOS ---
root_node = carregar_projeto(ARQUIVO_SAVE)
current_node = root_node 

# --- CONTROLE DE INTERAÇÃO --- (Sem alterações)
selected_task_drag = None
offset_x = 0
offset_y = 0
context_menu = {'active': False, 'pos': (0, 0), 'task': None, 'options': []}

# --- FUNÇÃO DE DESENHO DO MENU --- (Sem alterações)
def draw_context_menu():
    if not context_menu['active']:
        return
    mouse_pos = pygame.mouse.get_pos()
    max_width = MENU_MIN_WIDTH_ABS
    for option in context_menu['options']:
        text_width = fonte_menu.size(option['text'])[0]
        max_width = max(max_width, text_width + MENU_PADDING_ABS * 2)
    option_height = fonte_menu.get_height()
    row_height = option_height + MENU_ITEM_SPACING
    menu_height = (row_height * len(context_menu['options'])) - MENU_ITEM_SPACING + (MENU_PADDING_ABS * 2)
    menu_rect = pygame.Rect(context_menu['pos'][0], context_menu['pos'][1], max_width, menu_height)
    pygame.draw.rect(tela, COR_MENU_FUNDO, menu_rect)
    pygame.draw.rect(tela, COR_MENU_BORDA, menu_rect, width=1)
    current_y = context_menu['pos'][1] + MENU_PADDING_ABS
    for i, option in enumerate(context_menu['options']):
        option_rect = pygame.Rect(context_menu['pos'][0], current_y - MENU_ITEM_SPACING / 2, max_width, row_height)
        context_menu['options'][i]['rect'] = option_rect
        is_hovered = option['enabled'] and option_rect.collidepoint(mouse_pos)
        if is_hovered:
            hover_rect = pygame.Rect(context_menu['pos'][0] + 1, option_rect.y, max_width - 2, row_height)
            pygame.draw.rect(tela, COR_MENU_HOVER_FUNDO, hover_rect)
        text_color = COR_MENU_HOVER_TEXTO if is_hovered else (COR_TEXTO_MENU_ATIVO if option['enabled'] else COR_TEXTO_MENU_INATIVO)
        text_surface = fonte_menu.render(option['text'], True, text_color)
        text_rect = text_surface.get_rect(left=context_menu['pos'][0] + MENU_PADDING_ABS, centery=option_rect.centery)
        tela.blit(text_surface, text_rect)
        current_y += row_height

# --- LOOP PRINCIPAL ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            salvar_projeto(root_node, ARQUIVO_SAVE)
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked_on_task = next((task for task in current_node.children if task.rect.collidepoint(event.pos)), None)
            
            if event.button == 1:
                if context_menu['active']:
                    for option in context_menu['options']:
                        if option['enabled'] and 'rect' in option and option['rect'].collidepoint(event.pos):
                            action_text = option['text']

                            if action_text == 'Criar Nova Tarefa':
                                new_pos = context_menu['pos']
                                nova_tarefa = TaskNode(title="Nova Tarefa", body="", parent=current_node, pos=new_pos, size=TAMANHO_RETANGULO)
                                current_node.add_child(nova_tarefa)
                            
                            ### NOVO: IMPLEMENTAÇÃO DO DELETAR ###
                            elif action_text == 'Deletar':
                                task_to_delete = context_menu['task']
                                if task_to_delete in current_node.children:
                                    current_node.children.remove(task_to_delete)
                            
                            else:
                                print(f"Ação: '{action_text}' selecionada para a tarefa: '{context_menu['task'].title if context_menu['task'] else 'Nenhuma'}'")
                            break
                    context_menu['active'] = False
                else:
                    if clicked_on_task:
                        selected_task_drag = clicked_on_task
                        offset_x = selected_task_drag.rect.x - event.pos[0]
                        offset_y = selected_task_drag.rect.y - event.pos[1]

            elif event.button == 3:
                context_menu['active'] = True
                context_menu['pos'] = event.pos
                context_menu['task'] = clicked_on_task
                context_menu['options'] = [
                    {'text': 'Criar Nova Tarefa', 'enabled': not clicked_on_task},
                    {'text': 'Abrir', 'enabled': bool(clicked_on_task)},
                    {'text': 'Editar', 'enabled': bool(clicked_on_task)},
                    {'text': 'Deletar', 'enabled': bool(clicked_on_task)},
                ]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                selected_task_drag = None

        elif event.type == pygame.MOUSEMOTION:
            if selected_task_drag:
                selected_task_drag.rect.x = event.pos[0] + offset_x
                selected_task_drag.rect.y = event.pos[1] + offset_y
                
    # --- DESENHO --- (Sem alterações)
    tela.fill(COR_FUNDO)
    for task in current_node.children:
        pygame.draw.rect(tela, COR_RETANGULO, task.rect)
        pygame.draw.rect(tela, COR_BORDA_RETANGULO, task.rect, width=2)
        texto_surface = fonte_titulo.render(task.title, True, COR_TEXTO_TITULO)
        elipse_surface = None
        if task.body and task.body.strip():
            elipse_surface = fonte_titulo.render("...", True, COR_TEXTO_CORPO)
        altura_total_conteudo = texto_surface.get_height()
        if elipse_surface:
            altura_total_conteudo += PADDING_TITULO_ELIPSE + elipse_surface.get_height()
        start_y = task.rect.centery - (altura_total_conteudo / 2)
        texto_rect = texto_surface.get_rect(midtop=(task.rect.centerx, start_y))
        tela.blit(texto_surface, texto_rect)
        if elipse_surface:
            elipse_rect = elipse_surface.get_rect(midtop=(task.rect.centerx, texto_rect.bottom + PADDING_TITULO_ELIPSE))
            tela.blit(elipse_surface, elipse_rect)
    draw_context_menu()
    pygame.display.flip()