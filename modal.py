# Ficheiro: modal.py (VERSÃO CORRIGIDA E COMPLETA)
import pygame
import settings
import pyperclip

class EditModal:
    # __init__ e _save_changes_and_close não mudam
    def __init__(self, task_to_edit):
        self.task = task_to_edit
        self.font_titulo = pygame.font.Font(None, settings.TAMANHO_FONTE_TITULO)
        self.font_corpo = pygame.font.Font(None, settings.TAMANHO_FONTE_CORPO)
        self.font_menu = pygame.font.Font(None, settings.TAMANHO_FONTE_MENU)
        
        self.title_text = task_to_edit.title
        self.title_selection_start = 0
        self.title_selection_end = 0

        self.body_text = task_to_edit.body
        self.body_selection_start = 0
        self.body_selection_end = 0
        
        modal_width = settings.LARGURA_TELA * settings.MODAL_WIDTH_REL
        modal_height = settings.ALTURA_TELA * settings.MODAL_HEIGHT_REL
        self.modal_rect = pygame.Rect(0, 0, modal_width, modal_height)
        self.modal_rect.center = (settings.LARGURA_TELA / 2, settings.ALTURA_TELA / 2)
        self.close_button_rect = pygame.Rect(
            self.modal_rect.right - settings.MODAL_CLOSE_BUTTON_SIZE - settings.MODAL_CLOSE_BUTTON_MARGIN,
            self.modal_rect.top + settings.MODAL_CLOSE_BUTTON_MARGIN,
            settings.MODAL_CLOSE_BUTTON_SIZE,
            settings.MODAL_CLOSE_BUTTON_SIZE
        )
        self.concluido_button_rect = pygame.Rect(0, 0, settings.MODAL_DONE_BUTTON_WIDTH, settings.MODAL_DONE_BUTTON_HEIGHT)
        self.concluido_button_rect.bottomright = (
            self.modal_rect.right - settings.MODAL_DONE_BUTTON_MARGIN,
            self.modal_rect.bottom - settings.MODAL_DONE_BUTTON_MARGIN
        )
        self.active_field = None
        self.cursor_visible = True
        self.last_cursor_toggle = pygame.time.get_ticks()

        padding = 20
        label_height = 25
        self.title_input_rect = pygame.Rect(
            self.modal_rect.left + padding,
            self.modal_rect.top + 50 + label_height,
            self.modal_rect.width - (padding * 2),
            40
        )
        self.body_input_rect = pygame.Rect(
            self.modal_rect.left + padding,
            self.title_input_rect.bottom + padding + label_height,
            self.modal_rect.width - (padding * 2),
            self.modal_rect.bottom - self.title_input_rect.bottom - (padding * 3) - self.concluido_button_rect.height - label_height
        )
        self.is_selecting = False
        
        self.scroll_y = 0
        self.body_cursor_rect = pygame.Rect(0, 0, 0, 0)
    
    def _save_changes_and_close(self):
        self.task.title = self.title_text
        self.task.body = self.body_text
        return 'close'

    def _get_char_index_from_pos(self, pos):
        rel_x = pos[0] - (self.title_input_rect.x + settings.MODAL_INPUT_PADDING)
        if rel_x < 0: return 0
        current_width = 0
        for i, char in enumerate(self.title_text):
            char_width = self.font_titulo.size(char)[0]
            if rel_x < current_width + char_width / 2:
                return i
            current_width += char_width
        return len(self.title_text)

    def _get_body_char_index_from_pos(self, pos):
        """Calcula o índice do caractere no texto do corpo com base na posição (x, y) do rato."""
        lines = self.body_text.split('\n')
        char_index = 0
        
        # Posição relativa Y dentro da caixa de texto
        rel_y = pos[1] - (self.body_input_rect.y + settings.MODAL_INPUT_PADDING)
        
        # Descobre em que linha o clique ocorreu
        line_height = self.font_corpo.get_height()
        clicked_line_index = int(rel_y / line_height)
        clicked_line_index = max(0, min(clicked_line_index, len(lines) - 1)) # Garante que está dentro dos limites
        
        # Calcula o índice de caracteres até ao início da linha clicada
        for i in range(clicked_line_index):
            char_index += len(lines[i]) + 1 # +1 para o '\n'

        # Agora, calcula a posição X na linha clicada
        line_text = lines[clicked_line_index]
        rel_x = pos[0] - (self.body_input_rect.x + settings.MODAL_INPUT_PADDING)
        
        current_width = 0
        for i, char in enumerate(line_text):
            char_width = self.font_corpo.size(char)[0]
            if rel_x < current_width + char_width / 2:
                return char_index + i
            current_width += char_width
        
        return char_index + len(line_text)
    def _ensure_cursor_visible(self):
        """Ajusta o self.scroll_y para garantir que o cursor do corpo esteja na área visível."""
        # A posição do cursor (self.body_cursor_rect) é calculada no método draw
        cursor_top_abs = self.body_cursor_rect.y
        cursor_bottom_abs = self.body_cursor_rect.bottom
        
        visible_top_abs = self.body_input_rect.y
        visible_bottom_abs = self.body_input_rect.bottom

        # Se o cursor estiver renderizado acima da área visível
        if cursor_top_abs < visible_top_abs:
            self.scroll_y -= (visible_top_abs - cursor_top_abs)
        
        # Se o cursor estiver renderizado abaixo da área visível
        if cursor_bottom_abs > visible_bottom_abs:
            self.scroll_y += (cursor_bottom_abs - visible_bottom_abs)
        
        # Garante que não rolamos para além dos limites (clamp)
        self.scroll_y = max(0, self.scroll_y)
        lines = self.body_text.split('\n')
        total_text_height = len(lines) * self.font_corpo.get_height()
        visible_height = self.body_input_rect.height - (settings.MODAL_INPUT_PADDING * 2)
        max_scroll = max(0, total_text_height - visible_height)
        self.scroll_y = min(self.scroll_y, max_scroll)
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Lógica do scroll
            if event.button == 4 or event.button == 5:
                if self.body_input_rect.collidepoint(event.pos):
                    if event.button == 4: # Roda para cima
                        self.scroll_y -= settings.MODAL_BODY_SCROLL_SPEED
                    elif event.button == 5: # Roda para baixo
                        self.scroll_y += settings.MODAL_BODY_SCROLL_SPEED

                    # ### ADICIONE/ALTERE ESTE BLOCO DE CÓDIGO ###
                    # Garante que não rolamos para cima do início
                    self.scroll_y = max(0, self.scroll_y)
                    
                    # Calcula o limite máximo de rolagem para baixo
                    lines = self.body_text.split('\n')
                    total_text_height = len(lines) * self.font_corpo.get_height()
                    visible_height = self.body_input_rect.height - (settings.MODAL_INPUT_PADDING * 2)
                    max_scroll = max(0, total_text_height - visible_height)
                    
                    # Garante que não rolamos para baixo do fim
                    self.scroll_y = min(self.scroll_y, max_scroll)
                    
                    print(f"Scroll Y: {self.scroll_y} (Max: {max_scroll})") # Print de depuração útil

            # --- Lógica do Clique Esquerdo (Botão 1) ---
            elif event.button == 1:
                # O seu código funcional para o clique esquerdo vem aqui
                if self.close_button_rect.collidepoint(event.pos): return 'close'
                if self.concluido_button_rect.collidepoint(event.pos): return self._save_changes_and_close()

                if self.title_input_rect.collidepoint(event.pos):
                    self.active_field = 'title'
                    cursor_pos = self._get_char_index_from_pos(event.pos)
                    self.title_selection_start = self.title_selection_end = cursor_pos
                    self.is_selecting = True
                elif self.body_input_rect.collidepoint(event.pos):
                    self.active_field = 'body'
                    cursor_pos = self._get_body_char_index_from_pos(event.pos)
                    self.body_selection_start = self.body_selection_end = cursor_pos
                    self.is_selecting = True
                else:
                    self.active_field = None
                    self.is_selecting = False

        if event.type == pygame.MOUSEMOTION:
            if self.is_selecting:
                if self.active_field == 'title':
                    self.title_selection_end = self._get_char_index_from_pos(event.pos)
                # ### NOVO: Lógica de arrastar para o corpo ###
                elif self.active_field == 'body':
                    self.body_selection_end = self._get_body_char_index_from_pos(event.pos)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_selecting = False

        # Lógica de TECLADO
        if event.type == pygame.KEYDOWN:
            if self.active_field is None and event.key == pygame.K_RETURN: return self._save_changes_and_close()

            # --- Lógica para o campo TÍTULO ---
            if self.active_field == 'title':
                # ### NOVO: Lógica das setas direcionais ###
                if event.key == pygame.K_LEFT:
                    # Move o cursor para a esquerda, com um limite em 0
                    new_pos = max(0, self.title_selection_end - 1)
                    self.title_selection_start = self.title_selection_end = new_pos
                elif event.key == pygame.K_RIGHT:
                    # Move o cursor para a direita, com um limite no final do texto
                    new_pos = min(len(self.title_text), self.title_selection_end + 1)
                    self.title_selection_start = self.title_selection_end = new_pos
                if event.mod & pygame.KMOD_CTRL:
                    if event.key == pygame.K_a: self.title_selection_start, self.title_selection_end = 0, len(self.title_text)
                    elif event.key == pygame.K_c:
                        if self.title_selection_start != self.title_selection_end:
                            start, end = min(self.title_selection_start, self.title_selection_end), max(self.title_selection_start, self.title_selection_end)
                            pyperclip.copy(self.title_text[start:end])
                    elif event.key == pygame.K_x:
                        if self.title_selection_start != self.title_selection_end:
                            start, end = min(self.title_selection_start, self.title_selection_end), max(self.title_selection_start, self.title_selection_end)
                            pyperclip.copy(self.title_text[start:end])
                            self.title_text = self.title_text[:start] + self.title_text[end:]
                            self.title_selection_start = self.title_selection_end = start
                    elif event.key == pygame.K_v:
                        start, end = min(self.title_selection_start, self.title_selection_end), max(self.title_selection_start, self.title_selection_end)
                        clipboard_text = pyperclip.paste()
                        self.title_text = self.title_text[:start] + clipboard_text + self.title_text[end:]
                        self.title_selection_start = self.title_selection_end = start + len(clipboard_text)
                elif event.key == pygame.K_BACKSPACE:
                    if self.title_selection_start != self.title_selection_end:
                        start, end = min(self.title_selection_start, self.title_selection_end), max(self.title_selection_start, self.title_selection_end)
                        self.title_text = self.title_text[:start] + self.title_text[end:]
                        self.title_selection_start = self.title_selection_end = start
                    elif self.title_selection_end > 0:
                        pos = self.title_selection_end
                        self.title_text = self.title_text[:pos-1] + self.title_text[pos:]
                        self.title_selection_start = self.title_selection_end = pos - 1
                elif event.key == pygame.K_RETURN: self.active_field = None
                else:
                    start, end = min(self.title_selection_start, self.title_selection_end), max(self.title_selection_start, self.title_selection_end)
                    self.title_text = self.title_text[:start] + event.unicode + self.title_text[end:]
                    self.title_selection_start = self.title_selection_end = start + len(event.unicode)
            
            # --- Lógica para o campo CORPO (VERSÃO CORRIGIDA) ---
            elif self.active_field == 'body':
                # Combinação de teclas (Ctrl + algo)
                if event.mod & pygame.KMOD_CTRL:
                    if event.key == pygame.K_a:
                        self.body_selection_start, self.body_selection_end = 0, len(self.body_text)
                    elif event.key == pygame.K_c:
                        if self.body_selection_start != self.body_selection_end:
                            start, end = min(self.body_selection_start, self.body_selection_end), max(self.body_selection_start, self.body_selection_end)
                            pyperclip.copy(self.body_text[start:end])
                    elif event.key == pygame.K_x:
                        if self.body_selection_start != self.body_selection_end:
                            start, end = min(self.body_selection_start, self.body_selection_end), max(self.body_selection_start, self.body_selection_end)
                            pyperclip.copy(self.body_text[start:end])
                            self.body_text = self.body_text[:start] + self.body_text[end:]
                            self.body_selection_start = self.body_selection_end = start
                    elif event.key == pygame.K_v:
                        start, end = min(self.body_selection_start, self.body_selection_end), max(self.body_selection_start, self.body_selection_end)
                        clipboard_text = pyperclip.paste()
                        self.body_text = self.body_text[:start] + clipboard_text + self.body_text[end:]
                        self.body_selection_start = self.body_selection_end = start + len(clipboard_text)

                # Teclas de Ação (Backspace, Enter, Setas)
                elif event.key == pygame.K_BACKSPACE:
                    if self.body_selection_start != self.body_selection_end:
                        start, end = min(self.body_selection_start, self.body_selection_end), max(self.body_selection_start, self.body_selection_end)
                        self.body_text = self.body_text[:start] + self.body_text[end:]
                        self.body_selection_start = self.body_selection_end = start
                    elif self.body_selection_end > 0:
                        pos = self.body_selection_end
                        self.body_text = self.body_text[:pos-1] + self.body_text[pos:]
                        self.body_selection_start = self.body_selection_end = pos - 1
                
                elif event.key == pygame.K_RETURN:
                    start, end = min(self.body_selection_start, self.body_selection_end), max(self.body_selection_start, self.body_selection_end)
                    self.body_text = self.body_text[:start] + '\n' + self.body_text[end:]
                    self.body_selection_start = self.body_selection_end = start + 1

                elif event.key == pygame.K_LEFT:
                    new_pos = max(0, self.body_selection_end - 1)
                    self.body_selection_start = self.body_selection_end = new_pos
                
                elif event.key == pygame.K_RIGHT:
                    new_pos = min(len(self.body_text), self.body_selection_end + 1)
                    self.body_selection_start = self.body_selection_end = new_pos
                
                # Digitação Normal
                else:
                    start, end = min(self.body_selection_start, self.body_selection_end), max(self.body_selection_start, self.body_selection_end)
                    self.body_text = self.body_text[:start] + event.unicode + self.body_text[end:]
                    self.body_selection_start = self.body_selection_end = start + len(event.unicode)
                lines = self.body_text.split('\n')
                char_count = 0
                cursor_line_index = 0
                for i, line in enumerate(lines):
                    if char_count + len(line) >= self.body_selection_end:
                        cursor_line_index = i
                        break
                    char_count += len(line) + 1
                
                line_height = self.font_corpo.get_height()
                # Posição Y do cursor relativa ao topo da caixa de texto
                cursor_y_rel = (cursor_line_index * line_height)
                
                # Área visível
                visible_height = self.body_input_rect.height - (settings.MODAL_INPUT_PADDING * 2)
                
                # Verifica se o cursor está fora dos limites visíveis
                if cursor_y_rel < self.scroll_y:
                    self.scroll_y = cursor_y_rel
                elif cursor_y_rel + line_height > self.scroll_y + visible_height:
                    self.scroll_y = cursor_y_rel + line_height - visible_height
                self._ensure_cursor_visible()

        return None
    
    # update e draw não mudam
    def update(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_cursor_toggle > settings.CURSOR_BLINK_RATE:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = time_now

    # Ficheiro: modal.py (SUBSTITUA O MÉTODO DRAW INTEIRO)
 # NOVO método para centralizar o cálculo da posição do cursor
    def update_cursor_rect(self):
        if self.active_field == 'body':
            lines = self.body_text.split('\n')
            char_index = 0
            cursor_found = False
            y_offset = self.body_input_rect.y + settings.MODAL_INPUT_PADDING - self.scroll_y

            for line in lines:
                if char_index <= self.body_selection_end <= char_index + len(line):
                    local_cursor_pos = self.body_selection_end - char_index
                    text_up_to_cursor = line[:local_cursor_pos]
                    cursor_x = self.body_input_rect.x + settings.MODAL_INPUT_PADDING + self.font_corpo.size(text_up_to_cursor)[0]
                    self.body_cursor_rect = pygame.Rect(cursor_x, y_offset, 2, self.font_corpo.get_height())
                    cursor_found = True
                    break
                char_index += len(line) + 1
                y_offset += self.font_corpo.get_height()
            
            if not cursor_found: # Se o cursor estiver no final
                last_line_y = y_offset - self.font_corpo.get_height()
                self.body_cursor_rect = pygame.Rect(self.body_input_rect.x + settings.MODAL_INPUT_PADDING, last_line_y, 2, self.font_corpo.get_height())
    def draw(self, screen):
        overlay = pygame.Surface((settings.LARGURA_TELA, settings.ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, settings.COR_FUNDO, self.modal_rect)
        pygame.draw.rect(screen, settings.COR_BORDA_RETANGULO, self.modal_rect, 2)
        mouse_pos = pygame.mouse.get_pos()
        
        # Desenho dos Botões
        is_hovering_close = self.close_button_rect.collidepoint(mouse_pos)
        text_color_x = settings.MODAL_CLOSE_X_COLOR_NORMAL
        if is_hovering_close:
            pygame.draw.rect(screen, settings.MODAL_CLOSE_BG_COLOR_HOVER, self.close_button_rect)
            text_color_x = settings.MODAL_CLOSE_X_COLOR_HOVER
        close_text = self.font_titulo.render("X", True, text_color_x)
        close_text_rect = close_text.get_rect(center=self.close_button_rect.center)
        screen.blit(close_text, close_text_rect)
        
        is_hovering_done = self.concluido_button_rect.collidepoint(mouse_pos)
        bg_color = settings.MODAL_DONE_BG_COLOR_HOVER if is_hovering_done else settings.MODAL_DONE_BG_COLOR_NORMAL
        pygame.draw.rect(screen, bg_color, self.concluido_button_rect)
        pygame.draw.rect(screen, settings.MODAL_DONE_BORDER_COLOR, self.concluido_button_rect, settings.MODAL_DONE_BORDER_WIDTH)
        concluido_text = self.font_menu.render("Concluido", True, (0, 0, 0))
        concluido_text_rect = concluido_text.get_rect(center=self.concluido_button_rect.center)
        screen.blit(concluido_text, concluido_text_rect)
        
        # Desenho dos Títulos dos Campos
        title_label_surface = self.font_menu.render("Nome da Tarefa:", True, settings.COR_TEXTO_TITULO)
        screen.blit(title_label_surface, (self.title_input_rect.left, self.title_input_rect.top - 20))
        body_label_surface = self.font_menu.render("Descrição da Tarefa:", True, settings.COR_TEXTO_TITULO)
        screen.blit(body_label_surface, (self.body_input_rect.left, self.body_input_rect.top - 20))
        
        # Desenho do Campo de Título
        pygame.draw.rect(screen, settings.MODAL_INPUT_BG_COLOR, self.title_input_rect)
        border_color_title = settings.MODAL_INPUT_BORDER_ACTIVE if self.active_field == 'title' else settings.MODAL_INPUT_BORDER_INACTIVE
        pygame.draw.rect(screen, border_color_title, self.title_input_rect, 2)
        
        if self.active_field == 'title':
            text_x, text_y = self.title_input_rect.x + settings.MODAL_INPUT_PADDING, self.title_input_rect.y + settings.MODAL_INPUT_PADDING
            start_index, end_index = min(self.title_selection_start, self.title_selection_end), max(self.title_selection_start, self.title_selection_end)
            text_before, text_selected, text_after = self.title_text[:start_index], self.title_text[start_index:end_index], self.title_text[end_index:]
            surface_before = self.font_titulo.render(text_before, True, settings.COR_TEXTO_TITULO)
            surface_selected = self.font_titulo.render(text_selected, True, settings.COR_MENU_HOVER_TEXTO)
            surface_after = self.font_titulo.render(text_after, True, settings.COR_TEXTO_TITULO)
            screen.blit(surface_before, (text_x, text_y))
            if text_selected:
                selection_rect_x = text_x + surface_before.get_width()
                selection_rect = pygame.Rect(selection_rect_x, text_y, surface_selected.get_width(), surface_selected.get_height())
                pygame.draw.rect(screen, settings.COR_MENU_HOVER_FUNDO, selection_rect)
                screen.blit(surface_selected, (selection_rect_x, text_y))
            screen.blit(surface_after, (text_x + surface_before.get_width() + surface_selected.get_width(), text_y))
            if self.cursor_visible and self.title_selection_start == self.title_selection_end:
                cursor_pos_x = text_x + self.font_titulo.size(self.title_text[:self.title_selection_end])[0]
                cursor_height = self.font_titulo.get_height()
                pygame.draw.line(screen, settings.COR_TEXTO_TITULO, (cursor_pos_x, text_y), (cursor_pos_x, text_y + cursor_height), 2)
        else:
            title_surface = self.font_titulo.render(self.title_text, True, settings.COR_TEXTO_TITULO)
            screen.blit(title_surface, (self.title_input_rect.x + settings.MODAL_INPUT_PADDING, self.title_input_rect.y + settings.MODAL_INPUT_PADDING))

        # --- Desenho do Campo de Corpo ---
        pygame.draw.rect(screen, settings.MODAL_INPUT_BG_COLOR, self.body_input_rect)
        border_color_body = settings.MODAL_INPUT_BORDER_ACTIVE if self.active_field == 'body' else settings.MODAL_INPUT_BORDER_INACTIVE
        pygame.draw.rect(screen, border_color_body, self.body_input_rect, 2)

        lines = self.body_text.split('\n')
        total_text_height = len(lines) * self.font_corpo.get_height()
        visible_height = self.body_input_rect.height - (settings.MODAL_INPUT_PADDING * 2)

        # ### ALTERADO: Lógica para desenhar a pista da scrollbar ###
        if total_text_height > visible_height:
            # Calcula a posição e o tamanho da pista com as novas margens
            track_rect = pygame.Rect(
                self.body_input_rect.right - settings.SCROLLBAR_WIDTH - settings.SCROLLBAR_PADDING,
                self.body_input_rect.top + settings.SCROLLBAR_PADDING,
                settings.SCROLLBAR_WIDTH,
                self.body_input_rect.height - (settings.SCROLLBAR_PADDING * 2)
            )
            pygame.draw.rect(screen, settings.SCROLLBAR_TRACK_COLOR, track_rect)
            # ### NOVO: Lógica para desenhar o Polegar ###
            # 2. Calcula a altura do polegar
            thumb_height_ratio = visible_height / total_text_height
            thumb_height = track_rect.height * thumb_height_ratio
            thumb_height = max(thumb_height, settings.SCROLLBAR_MIN_THUMB_HEIGHT) # Garante a altura mínima

            # 3. Calcula a posição Y do polegar
            max_scroll = total_text_height - visible_height
            scroll_percentage = self.scroll_y / max_scroll if max_scroll > 0 else 0
            thumb_y = track_rect.y + (track_rect.height - thumb_height) * scroll_percentage

            # 4. Desenha o polegar
            thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_height)
            pygame.draw.rect(screen, settings.SCROLLBAR_THUMB_COLOR, thumb_rect)

        
        # ### ALTERE ESTA LINHA ###
        y_offset = self.body_input_rect.y + settings.MODAL_INPUT_PADDING - self.scroll_y
        
        char_index = 0
        sel_start, sel_end = min(self.body_selection_start, self.body_selection_end), max(self.body_selection_start, self.body_selection_end)
        
        cursor_y, cursor_x = -1, -1 # Mantemos isto para a lógica do cursor

        for line in lines:
            line_len = len(line)
            line_start_index = char_index
            line_end_index = char_index + line_len
            
            # Lógica para encontrar a posição do cursor no corpo do texto
            if self.active_field == 'body' and self.body_selection_start == self.body_selection_end:
                if line_start_index <= self.body_selection_end <= line_end_index:
                    local_cursor_pos = self.body_selection_end - line_start_index
                    text_up_to_cursor = line[:local_cursor_pos]
                    cursor_x = self.body_input_rect.x + settings.MODAL_INPUT_PADDING + self.font_corpo.size(text_up_to_cursor)[0]
                    cursor_y = y_offset
            
            # Desenho da linha (com seleção visual)
            local_sel_start = max(0, sel_start - line_start_index)
            local_sel_end = min(line_len, sel_end - line_start_index)
            part_before, part_selected, part_after = line[:local_sel_start], line[local_sel_start:local_sel_end], line[local_sel_end:]
            surf_before = self.font_corpo.render(part_before, True, settings.COR_TEXTO_CORPO)
            surf_selected = self.font_corpo.render(part_selected, True, settings.COR_MENU_HOVER_TEXTO)
            surf_after = self.font_corpo.render(part_after, True, settings.COR_TEXTO_CORPO)
            x_offset = self.body_input_rect.x + settings.MODAL_INPUT_PADDING
            
            screen.set_clip(self.body_input_rect.inflate(-10, -10))
            screen.blit(surf_before, (x_offset, y_offset))
            x_offset += surf_before.get_width()
            if part_selected:
                selection_rect = pygame.Rect(x_offset, y_offset, surf_selected.get_width(), surf_selected.get_height())
                pygame.draw.rect(screen, settings.COR_MENU_HOVER_FUNDO, selection_rect)
                screen.blit(surf_selected, (x_offset, y_offset))
                x_offset += surf_selected.get_width()
            screen.blit(surf_after, (x_offset, y_offset))
            screen.set_clip(None)
            
            y_offset += self.font_corpo.get_height()
            char_index += line_len + 1

        # Desenha o cursor piscando para o corpo
        if self.active_field == 'body' and self.cursor_visible and self.body_selection_start == self.body_selection_end:
            screen.set_clip(self.body_input_rect.inflate(-10, -10))
            pygame.draw.line(screen, settings.COR_TEXTO_TITULO, self.body_cursor_rect.topleft, self.body_cursor_rect.bottomleft, 2)
            screen.set_clip(None)
            if cursor_y != -1:
                cursor_height = self.font_corpo.get_height()
                pygame.draw.line(screen, settings.COR_TEXTO_TITULO, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)