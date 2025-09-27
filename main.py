import pygame
import sys
import json
import os
import settings 
from task import TaskNode
from modal import EditModal

# --- INICIALIZAÇÃO ---
pygame.init()
pygame.key.set_repeat(400, 35) # ### NOVO: Habilita repetição de teclas
tela = pygame.display.set_mode((settings.LARGURA_TELA, settings.ALTURA_TELA))
pygame.display.set_caption("Planejador de Abstração")
fonte_titulo = pygame.font.Font(None, settings.TAMANHO_FONTE_TITULO)
fonte_menu = pygame.font.Font(None, settings.TAMANHO_FONTE_MENU)
# Ficheiro: main.py (na secção INICIALIZAÇÃO)
fonte_titulo = pygame.font.Font(None, settings.TAMANHO_FONTE_TITULO)
fonte_menu = pygame.font.Font(None, settings.TAMANHO_FONTE_MENU)
fonte_arvore = pygame.font.Font(None, settings.TREE_FONT_SIZE) # ### ADICIONE ESTA LINHA ###
# --- FUNÇÕES DE SALVAR E CARREGAR ---
def salvar_projeto(node, filename):
    """Salva a árvore de tarefas e a lista de barras de progresso."""
    # Converte a lista de nós da barra de progresso numa lista dos seus caminhos
    progress_bar_paths = [n.get_path() for n in progress_bar_nodes]
    
    project_data = {
        'tree': node.to_dict(),
        'progress_bars': progress_bar_paths
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=4, ensure_ascii=False)
    print(f"Projeto salvo em {filename}")

def find_node_by_path(root, path_str):
    """Encontra um nó na árvore com base no seu caminho em string."""
    path_parts = path_str.split(" > ")
    current_node = root
    for part in path_parts:
        found_child = None
        for child in current_node.children:
            if child.title == part:
                found_child = child
                break
        if found_child:
            current_node = found_child
        else:
            return None
    return current_node
def carregar_projeto(filename):
    """Carrega a árvore de tarefas de um ficheiro JSON. Se não existir, cria uma nova."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            print(f"Projeto carregado de {filename}")
            
            # Lida com ambos os formatos de save, antigo e novo
            if 'tree' in project_data:
                root = TaskNode.from_dict(project_data['tree'])
                # Restaura as barras de progresso
                progress_bar_paths = project_data.get('progress_bars', [])
                for path in progress_bar_paths:
                    node = find_node_by_path(root, path)
                    if node:
                        progress_bar_nodes.append(node)
            else: # Formato antigo
                root = TaskNode.from_dict(project_data)

            return root
        except (json.JSONDecodeError, KeyError):
            # Se o ficheiro estiver corrompido ou mal formatado, cria um novo
            print("Ficheiro de save corrompido. A criar novo projeto.")
    
    # Se o ficheiro não existe ou está corrompido, cria um novo projeto
    print("Nenhum arquivo de save válido encontrado. A criar novo projeto.")
    root = TaskNode("Raiz", "Nó raiz do sistema")
    tarefa_inicial = TaskNode("Meu Primeiro Projeto", "", parent=root, pos=(20, 20), size=settings.TAMANHO_RETANGULO)
    root.add_child(tarefa_inicial)
    return root # <--- Esta é a linha crucial que estava em falta
def draw_task_tree(surface, node, x, y, level, ui_elements):
    """Desenha recursivamente um nó, os seus filhos, e regista os elementos de UI."""
    for child in node.children:
        indentation = level * settings.TREE_INDENT_WIDTH
        
        # --- LÓGICA DE DESENHAR E REGISTAR O ITEM ---
        
        # 1. Símbolo de expandir/recolher
        toggle_symbol = ''
        if child.children:
            toggle_symbol = 'v' if child.is_expanded else '>'
        
        text_surface_toggle = fonte_arvore.render(toggle_symbol, True, settings.COR_TEXTO_TITULO)
        toggle_rect = text_surface_toggle.get_rect(topleft=(x + indentation, y))
        surface.blit(text_surface_toggle, toggle_rect)
        
        # Regista o retângulo do símbolo na nossa lista de UI
        if child.children:
            ui_elements.append({'rect': toggle_rect, 'node': child, 'action': 'toggle_expand'})

        # 2. Título da tarefa
        display_title = child.title
        if len(display_title) > settings.TREE_MAX_CHARS:
            display_title = display_title[:settings.TREE_MAX_CHARS] + "..."
        
        title_x_pos = x + indentation + 20
        text_surface_title = fonte_arvore.render(display_title, True, settings.COR_TEXTO_TITULO)
        title_rect = text_surface_title.get_rect(topleft=(title_x_pos, y))
        surface.blit(text_surface_title, title_rect)

        # Regista o retângulo do título na nossa lista de UI
        ui_elements.append({'rect': title_rect, 'node': child, 'action': 'navigate'})

        y += settings.TREE_LINE_SPACING
        
        if child.is_expanded:
            # Passa a lista para a chamada recursiva
            y = draw_task_tree(surface, child, x, y, level + 1, ui_elements)
            
    return y
def calculate_completion(node):
    """
    Calcula recursivamente o número de tarefas completas e totais
    a partir de um determinado nó.
    """
    # Caso Base: Se o nó não tem filhos, ele é a sua própria tarefa.
    if not node.children:
        total = 1
        completed = 1 if node.status == 'completed' else 0
        return completed, total

    # Passo Recursivo: Se o nó tem filhos, a sua completude é a soma da completude dos filhos.
    else:
        total_completed = 0
        total_tasks = 0
        for child in node.children:
            # Chama a função para cada filho e soma os resultados
            completed, total = calculate_completion(child)
            total_completed += completed
            total_tasks += total
        
        # Evita divisão por zero se um container estiver vazio
        if total_tasks == 0:
            return 0, 0
            
        return total_completed, total_tasks



# --- CONTROLE DE INTERAÇÃO ---
selected_task_drag = None
offset_x, offset_y = 0, 0
context_menu = {'active': False, 'pos': (0, 0), 'task': None, 'options': []}
last_click_time = 0
active_modal = None

# --- FUNÇÃO DE DESENHO DO MENU ---
def draw_context_menu():
    if not context_menu['active']: return
    mouse_pos = pygame.mouse.get_pos()
    max_width = settings.MENU_MIN_WIDTH_ABS
    for option in context_menu['options']:
        text_width = fonte_menu.size(option['text'])[0]
        max_width = max(max_width, text_width + settings.MENU_PADDING_ABS * 2)
    option_height = fonte_menu.get_height()
    row_height = option_height + settings.MENU_ITEM_SPACING
    menu_height = (row_height * len(context_menu['options'])) - settings.MENU_ITEM_SPACING + (settings.MENU_PADDING_ABS * 2)
    menu_rect = pygame.Rect(context_menu['pos'][0], context_menu['pos'][1], max_width, menu_height)
    pygame.draw.rect(tela, settings.COR_MENU_FUNDO, menu_rect)
    pygame.draw.rect(tela, settings.COR_MENU_BORDA, menu_rect, width=1)
    current_y = context_menu['pos'][1] + settings.MENU_PADDING_ABS
    for i, option in enumerate(context_menu['options']):
        option_rect = pygame.Rect(context_menu['pos'][0], current_y - settings.MENU_ITEM_SPACING / 2, max_width, row_height)
        context_menu['options'][i]['rect'] = option_rect
        is_hovered = option['enabled'] and option_rect.collidepoint(mouse_pos)
        if is_hovered:
            hover_rect = pygame.Rect(context_menu['pos'][0] + 1, option_rect.y, max_width - 2, row_height)
            pygame.draw.rect(tela, settings.COR_MENU_HOVER_FUNDO, hover_rect)
        text_color = settings.COR_MENU_HOVER_TEXTO if is_hovered else (settings.COR_TEXTO_MENU_ATIVO if option['enabled'] else settings.COR_TEXTO_MENU_INATIVO)
        text_surface = fonte_menu.render(option['text'], True, text_color)
        text_rect = text_surface.get_rect(left=context_menu['pos'][0] + settings.MENU_PADDING_ABS, centery=option_rect.centery)
        tela.blit(text_surface, text_rect)
        current_y += row_height
active_modal = None
tree_view_ui_elements = []
tree_context_menu = {'active': False, 'pos': (0,0), 'node': None} # ### ADICIONE ESTA LINHA ###
progress_bar_nodes = [] # Trocamos por uma lista vazia # ### ADICIONE ESTA LINHA ###
progress_bar_ui_elements = []
progress_bar_context_menu = {'active': False, 'pos': (0,0), 'node': None, 'options': []}
def draw_tree_context_menu(surface, menu_data):
    """Desenha o menu de contexto para a lista da árvore."""
    if not menu_data['active']:
        return

    options = menu_data.get('options', [])
    if not options: return

    # (A lógica de desenho do menu aqui é a mesma que a do 'draw_context_menu' principal)
    # Para simplificar, vamos criar um menu simples por agora
    option_surf = fonte_menu.render(options[0]['text'], True, settings.COR_TEXTO_MENU_ATIVO)
    option_rect = option_surf.get_rect(topleft=menu_data['pos'])
    
    # Adiciona um padding
    menu_bg_rect = option_rect.inflate(20, 20)
    
    pygame.draw.rect(surface, settings.COR_MENU_FUNDO, menu_bg_rect)
    pygame.draw.rect(surface, settings.COR_MENU_BORDA, menu_bg_rect, 1)
    
    surface.blit(option_surf, (menu_bg_rect.x + 10, menu_bg_rect.y + 10))
    
    # Guarda o retângulo da opção para detetar o clique
    options[0]['rect'] = pygame.Rect(menu_bg_rect.x + 10, menu_bg_rect.y + 10, option_surf.get_width(), option_surf.get_height())
def draw_progress_bar_context_menu(surface, menu_data):
    """Desenha o menu de contexto para a barra de progresso."""
    if not menu_data.get('active', False):
        return

    options = menu_data.get('options', [])
    if not options: return

    # A lógica de desenho é idêntica à dos outros menus
    option_surf = fonte_menu.render(options[0]['text'], True, settings.COR_TEXTO_MENU_ATIVO)
    option_rect = option_surf.get_rect(topleft=menu_data['pos'])
    
    menu_bg_rect = option_rect.inflate(20, 20)
    
    pygame.draw.rect(surface, settings.COR_MENU_FUNDO, menu_bg_rect)
    pygame.draw.rect(surface, settings.COR_MENU_BORDA, menu_bg_rect, 1)
    
    surface.blit(option_surf, (menu_bg_rect.x + 10, menu_bg_rect.y + 10))
    
    # Guarda o retângulo da opção para detetar o clique
    options[0]['rect'] = pygame.Rect(menu_bg_rect.x + 10, menu_bg_rect.y + 10, option_surf.get_width(), option_surf.get_height())
def find_node_by_path(root, path_str):
    """Encontra um nó na árvore com base no seu caminho em string."""
    path_parts = path_str.split(" > ")
    current_node = root
    for part in path_parts:
        found_child = None
        for child in current_node.children:
            if child.title == part:
                found_child = child
                break
        if found_child:
            current_node = found_child
        else:
            return None # Caminho não encontrado
    return current_node
# --- ESTRUTURA DE DADOS ---
root_node = carregar_projeto(settings.ARQUIVO_SAVE)
current_node = root_node 
# --- LOOP PRINCIPAL ---
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            salvar_projeto(root_node, settings.ARQUIVO_SAVE)
            pygame.quit()
            sys.exit()

        # --- PROCESSAMENTO DE EVENTOS ---
        # Se um modal está ativo, ele tem prioridade total sobre os eventos
        if active_modal:
            result = active_modal.handle_event(event)
            if result == 'close':
                active_modal = None
        # Se nenhum modal estiver ativo, a tela principal processa os eventos
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_node.parent:
                        current_node = current_node.parent

            if event.type == pygame.MOUSEBUTTONDOWN:
            # --- LÓGICA DO CLIQUE ESQUERDO (Botão 1) ---
                if event.button == 1:
                    # 1. Primeiro, verifica se um dos menus de contexto está ativo
                    if progress_bar_context_menu['active']:
                        for option in progress_bar_context_menu.get('options', []):
                            if 'rect' in option and option['rect'].collidepoint(event.pos):
                                if option['action'] == 'hide_this_progress':
                                    node_to_remove = progress_bar_context_menu['node']
                                    if node_to_remove in progress_bar_nodes:
                                        progress_bar_nodes.remove(node_to_remove)
                                break
                        progress_bar_context_menu['active'] = False
                    
                    
                    
                    elif tree_context_menu['active']:
                        for option in tree_context_menu.get('options', []):
                            if 'rect' in option and option['rect'].collidepoint(event.pos):
                                node_clicked = tree_context_menu['node']
                                
                                # ### LÓGICA ATUALIZADA AQUI ###
                                if option['action'] == 'show_progress':
                                    # Adiciona à lista se ainda não estiver lá
                                    if node_clicked not in progress_bar_nodes:
                                        progress_bar_nodes.append(node_clicked)
                                elif option['action'] == 'hide_progress':
                                    # Remove da lista se estiver lá
                                    if node_clicked in progress_bar_nodes:
                                        progress_bar_nodes.remove(node_clicked)
                                break
                        tree_context_menu['active'] = False

                    
                    elif context_menu['active']:
                        for option in context_menu.get('options', []):
                            if option.get('enabled', False) and 'rect' in option and option['rect'].collidepoint(event.pos):
                                action_text = option['text']
                                clicked_task_ctx = context_menu['task'] # Tarefa associada ao menu

                                # --- LÓGICA DAS AÇÕES QUE ESTAVA EM FALTA ---
                                if action_text == 'Criar Nova Tarefa':
                                    nova_tarefa = TaskNode(title="Nova Tarefa", body="", parent=current_node, pos=context_menu['pos'], size=settings.TAMANHO_RETANGULO)
                                    current_node.add_child(nova_tarefa)
                                elif action_text == 'Deletar':
                                    if clicked_task_ctx in current_node.children:
                                        current_node.children.remove(clicked_task_ctx)
                                elif action_text == 'Abrir':
                                    current_node = clicked_task_ctx
                                elif action_text == 'Editar':
                                    active_modal = EditModal(clicked_task_ctx)
                                elif action_text == 'Marcar como Completo':
                                    if clicked_task_ctx: clicked_task_ctx.set_status('completed')
                                elif action_text == 'Marcar como Em Desenvolvimento':
                                    if clicked_task_ctx: clicked_task_ctx.set_status('developing')
                                elif "Desmarcar" in action_text:
                                    if clicked_task_ctx: clicked_task_ctx.set_status('normal')
                                
                                break # Ação executada, sai do loop
                        
                        context_menu['active'] = False # Fecha o menu

                    # 2. Se nenhum menu estava ativo, verifica a UI principal
                    else:
                        was_click_on_tree = False
                        # Verifica cliques nos elementos da árvore
                        for element in tree_view_ui_elements:
                            if element['rect'].collidepoint(event.pos):
                                if element['action'] == 'toggle_expand':
                                    element['node'].is_expanded = not element['node'].is_expanded
                                elif element['action'] == 'navigate':
                                    current_node = element['node']
                                was_click_on_tree = True
                                break
                        
                        # Se não foi na árvore, verifica os retângulos principais
                        if not was_click_on_tree:
                            clicked_on_task = next((task for task in current_node.children if task.rect.collidepoint(event.pos)), None)
                            if clicked_on_task:
                                # Lógica de duplo-clique e arrastar
                                current_time = pygame.time.get_ticks()
                                if current_time - last_click_time < settings.DOUBLE_CLICK_TIME:
                                    current_node = clicked_on_task
                                else:
                                    selected_task_drag = clicked_on_task
                                    offset_x, offset_y = clicked_on_task.rect.x - event.pos[0], clicked_on_task.rect.y - event.pos[1]
                                last_click_time = current_time

                elif event.button == 3: # Clique Direito
                    # Reseta todos os menus no início
                    context_menu['active'] = False
                    tree_context_menu['active'] = False
                    progress_bar_context_menu['active'] = False
                    
                    was_click_handled = False
                    
                    # 1. Verifica PRIMEIRO as barras de progresso
                    for element in progress_bar_ui_elements:
                        if element['rect'].collidepoint(event.pos):
                            progress_bar_context_menu['active'] = True
                            
                            # ### ALTERADO: Calcula a posição para ser ACIMA da barra ###
                            menu_height_estimate = 40 # Uma estimativa da altura do menu
                            new_pos = (event.pos[0], element['rect'].top - menu_height_estimate)
                            progress_bar_context_menu['pos'] = new_pos
                            
                            progress_bar_context_menu['node'] = element['node']
                            progress_bar_context_menu['options'] = [{'text': 'Ocultar', 'action': 'hide_this_progress'}]
                            was_click_handled = True
                            break
                    
                    # 2. Se não foi, verifica a lista da árvore
                    if not was_click_handled:
                        for element in tree_view_ui_elements:
                            if element['rect'].collidepoint(event.pos) and element['action'] == 'navigate':
                                tree_context_menu['active'] = True
                                tree_context_menu['pos'] = event.pos
                                tree_context_menu['node'] = element['node']
                                if element['node'] in progress_bar_nodes:
                                    tree_context_menu['options'] = [{'text': 'Ocultar Progresso', 'action': 'hide_progress'}]
                                else:
                                    tree_context_menu['options'] = [{'text': 'Mostrar Progresso', 'action': 'show_progress'}]
                                was_click_handled = True
                                break
                    
                    # 3. Se não foi em nenhum desses, executa a lógica para os retângulos
                    if not was_click_handled:
                        clicked_on_task_main = next((task for task in current_node.children if task.rect.collidepoint(event.pos)), None)
                        context_menu['active'] = True
                        context_menu['pos'] = event.pos
                        context_menu['task'] = clicked_on_task_main
                        
                        # (A sua lógica de construir as opções para o menu dos retângulos vai aqui)
                        # Exemplo:
                        options = []
                        if clicked_on_task_main:
                        # Adiciona as opções padrão
                            options.extend([
                                {'text': 'Abrir', 'enabled': True},
                                {'text': 'Editar', 'enabled': True}
                            ])
                            # Adiciona as opções de estado dinâmicas
                            if clicked_on_task_main.status == 'completed':
                                options.append({'text': "Desmarcar 'Completo'", 'enabled': True})
                            elif clicked_on_task_main.status == 'developing':
                                options.append({'text': "Desmarcar 'Em Desenvolvimento'", 'enabled': True})
                            else: # Se o estado for 'normal'
                                options.extend([
                                    {'text': 'Marcar como Completo', 'enabled': True},
                                    {'text': 'Marcar como Em Desenvolvimento', 'enabled': True}
                                ])
                            
                            options.append({'text': 'Deletar', 'enabled': True})
                        else:
                            # Menu para quando se clica no fundo
                            options.append({'text': 'Criar Nova Tarefa', 'enabled': True})
                        
                        context_menu['options'] = options
                        

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    selected_task_drag = None

            if event.type == pygame.MOUSEMOTION:
                if selected_task_drag:
                    selected_task_drag.rect.x, selected_task_drag.rect.y = event.pos[0] + offset_x, event.pos[1] + offset_y
    
    # --- LÓGICA DE ATUALIZAÇÃO ---
    # Coisas que acontecem a cada frame, como o cursor piscando
    if active_modal:
        active_modal.update()

    # --- DESENHO ---
    # A tela principal é sempre desenhada primeiro
    tela.fill(settings.COR_FUNDO)
     # ...
    tree_view_ui_elements.clear()
    # Passe a lista como o novo argumento final
    draw_task_tree(tela, root_node, settings.TREE_VIEW_X_START, settings.TREE_VIEW_Y_START, 0, tree_view_ui_elements)
    for task in current_node.children:
        # ### LÓGICA DE ESCOLHA DE COR ATUALIZADA ###
        if task.status == 'completed':
            cor_fundo_retangulo = settings.COR_RETANGULO_COMPLETO
        elif task.status == 'developing':
            cor_fundo_retangulo = settings.COR_RETANGULO_DESENVOLVIMENTO
        else: # Se o status for 'normal'
            if task.children:
                cor_fundo_retangulo = settings.COR_RETANGULO_COM_FILHOS
            else:
                cor_fundo_retangulo = settings.COR_RETANGULO

        pygame.draw.rect(tela, cor_fundo_retangulo, task.rect)
        pygame.draw.rect(tela, settings.COR_BORDA_RETANGULO, task.rect, width=2)
        texto_surface = fonte_titulo.render(task.title, True, settings.COR_TEXTO_TITULO)
        elipse_surface = None
        if task.body and task.body.strip():
            elipse_surface = fonte_titulo.render("...", True, settings.COR_TEXTO_CORPO)
        altura_total_conteudo = texto_surface.get_height()
        if elipse_surface:
            altura_total_conteudo += settings.PADDING_TITULO_ELIPSE + elipse_surface.get_height()
        start_y = task.rect.centery - (altura_total_conteudo / 2)
        texto_rect = texto_surface.get_rect(midtop=(task.rect.centerx, start_y))
        tela.blit(texto_surface, texto_rect)
        if elipse_surface:
            elipse_rect = elipse_surface.get_rect(midtop=(task.rect.centerx, texto_rect.bottom + settings.PADDING_TITULO_ELIPSE))
            tela.blit(elipse_surface, elipse_rect)
    
    # Desenha os menus por cima
    # Desenha os menus
    draw_context_menu()
    draw_tree_context_menu(tela, tree_context_menu)
    draw_progress_bar_context_menu(tela, progress_bar_context_menu)

    # ### NOVO: LÓGICA FINAL PARA DESENHAR A BARRA DE PROGRESSO ###
    # ### LÓGICA ATUALIZADA PARA DESENHAR MÚLTIPLAS BARRAS DE PROGRESSO ###
    progress_bar_ui_elements.clear()
    bar_y_offset = 15 # Posição Y inicial para a primeira barra
    for node in progress_bar_nodes:
        completed, total = calculate_completion(node)
        
        title = node.title
        if len(title) > 20: title = title[:20] + "..."
        
        if total > 0:
            percentage = (completed / total) * 100
            progress_text = f"Progresso '{title}': {completed}/{total} ({percentage:.0f}%)"
        else:
            percentage = 0
            progress_text = f"Progresso '{title}': Nenhuma tarefa"

        # Desenha a barra
        bar_width = 300
        bar_height = 20
        bar_x = settings.LARGURA_TELA - bar_width - 15
        
        # Fundo da barra
        bg_bar_rect = pygame.Rect(bar_x, bar_y_offset, bar_width, bar_height)
        pygame.draw.rect(tela, (200, 200, 200), bg_bar_rect)
        
        # Progresso da barra
        progress_width = bar_width * (percentage / 100)
        progress_bar_rect = pygame.Rect(bar_x, bar_y_offset, progress_width, bar_height)
        pygame.draw.rect(tela, (100, 200, 100), progress_bar_rect)
        
        # Texto
        progress_surface = fonte_menu.render(progress_text, True, settings.COR_TEXTO_TITULO)
        tela.blit(progress_surface, (bar_x, bar_y_offset + bar_height + 5))

        # Prepara a posição Y para a próxima barra
        text_height = fonte_menu.get_height()
        full_bar_height = settings.MODAL_DONE_BUTTON_HEIGHT + 5 + text_height
        full_bar_rect = pygame.Rect(bar_x, bar_y_offset, bar_width, full_bar_height)
        progress_bar_ui_elements.append({'rect': full_bar_rect, 'node': node})
        
        # Prepara a posição Y para a próxima barra
        bar_y_offset += full_bar_height + 10 # Altura da barra + espaçamento

    if active_modal:
        active_modal.draw(tela)

    pygame.display.flip()