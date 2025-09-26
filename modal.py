# Arquivo: modal.py (CORRIGIDO)
import pygame
import settings
import pyperclip

class EditModal:
    def __init__(self, task_to_edit):
        self.task = task_to_edit
        self.font_titulo = pygame.font.Font(None, settings.TAMANHO_FONTE_TITULO)
        self.font_menu = pygame.font.Font(None, settings.TAMANHO_FONTE_MENU)
        self.edited_title = task_to_edit.title
        self.edited_body = task_to_edit.body
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
        self.title_input_rect = pygame.Rect(
            self.modal_rect.left + settings.MODAL_INPUT_PADDING,
            self.modal_rect.top + 50,
            self.modal_rect.width - (settings.MODAL_INPUT_PADDING * 2),
            40
        )
        self.selection_start = 0
        self.selection_end = 0
        self.is_selecting = False


    def _get_char_index_from_pos(self, pos):
        rel_x = pos[0] - (self.title_input_rect.x + settings.MODAL_INPUT_PADDING)
        current_width = 0
        for i, char in enumerate(self.edited_title):
            char_width = self.font_titulo.size(char)[0]
            if rel_x < current_width + char_width / 2:
                return i
            current_width += char_width
        return len(self.edited_title)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button_rect.collidepoint(event.pos):
                return 'close'
            
            if self.title_input_rect.collidepoint(event.pos):
                self.active_field = 'title'
                cursor_pos = self._get_char_index_from_pos(event.pos)
                self.selection_start = self.selection_end = cursor_pos
                self.is_selecting = True # Começa o processo de seleção
            else:
                self.active_field = None
                self.selection_start = self.selection_end = 0
                self.is_selecting = False

        if event.type == pygame.MOUSEMOTION:
            # Se o mouse estiver se movendo com o botão pressionado, atualiza a seleção
            if self.active_field == 'title' and self.is_selecting:
                cursor_pos = self._get_char_index_from_pos(event.pos)
                self.selection_end = cursor_pos

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Finaliza o processo de seleção
            self.is_selecting = False

        if event.type == pygame.KEYDOWN:
            if self.active_field == 'title':
                # Combinação de teclas (Ctrl + algo)
                if event.mod & pygame.KMOD_CTRL:
                    if event.key == pygame.K_a: # Ctrl+A
                        self.selection_start = 0
                        self.selection_end = len(self.edited_title)
                    
                    # ### NOVO: Lógica Ctrl+C (Copiar) ###
                    elif event.key == pygame.K_c:
                        if self.selection_start != self.selection_end:
                            start = min(self.selection_start, self.selection_end)
                            end = max(self.selection_start, self.selection_end)
                            pyperclip.copy(self.edited_title[start:end])

                    # ### NOVO: Lógica Ctrl+V (Colar) ###
                    elif event.key == pygame.K_v:
                        start = min(self.selection_start, self.selection_end)
                        end = max(self.selection_start, self.selection_end)
                        self.edited_title = self.edited_title[:start] + pyperclip.paste() + self.edited_title[end:]
                        self.selection_start = self.selection_end = start + len(pyperclip.paste())

                # Teclas normais (sem Ctrl)
                elif event.key == pygame.K_BACKSPACE:
                    if self.selection_start != self.selection_end:
                        start, end = min(self.selection_start, self.selection_end), max(self.selection_start, self.selection_end)
                        self.edited_title = self.edited_title[:start] + self.edited_title[end:]
                        self.selection_start = self.selection_end = start
                    elif self.selection_end > 0:
                        pos = self.selection_end
                        self.edited_title = self.edited_title[:pos-1] + self.edited_title[pos:]
                        self.selection_start = self.selection_end = pos - 1
                elif event.key == pygame.K_RETURN:
                    self.active_field = None
                    self.selection_start = self.selection_end = 0
                else:
                    start, end = min(self.selection_start, self.selection_end), max(self.selection_start, self.selection_end)
                    self.edited_title = self.edited_title[:start] + event.unicode + self.edited_title[end:]
                    self.selection_start = self.selection_end = start + len(event.unicode)
        
        return None
    def update(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_cursor_toggle > settings.CURSOR_BLINK_RATE:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = time_now

    def draw(self, screen):
        overlay = pygame.Surface((settings.LARGURA_TELA, settings.ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, settings.COR_FUNDO, self.modal_rect)
        pygame.draw.rect(screen, settings.COR_BORDA_RETANGULO, self.modal_rect, 2)
        mouse_pos = pygame.mouse.get_pos()
        is_hovering_close = self.close_button_rect.collidepoint(mouse_pos)
        text_color_x = settings.MODAL_CLOSE_X_COLOR_NORMAL
        if is_hovering_close:
            pygame.draw.rect(screen, settings.MODAL_CLOSE_BG_COLOR_HOVER, self.close_button_rect)
            text_color_x = settings.MODAL_CLOSE_X_COLOR_HOVER
        close_text = self.font_titulo.render("X", True, text_color_x)
        close_text_rect = close_text.get_rect(center=self.close_button_rect.center)
        screen.blit(close_text, close_text_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.concluido_button_rect)
        concluido_text = self.font_menu.render("Concluído", True, (0, 0, 0))
        concluido_text_rect = concluido_text.get_rect(center=self.concluido_button_rect.center)
        screen.blit(concluido_text, concluido_text_rect)
        pygame.draw.rect(screen, settings.MODAL_INPUT_BG_COLOR, self.title_input_rect)
        border_color = settings.MODAL_INPUT_BORDER_ACTIVE if self.active_field == 'title' else settings.MODAL_INPUT_BORDER_INACTIVE
        pygame.draw.rect(screen, border_color, self.title_input_rect, 2)
        text_x = self.title_input_rect.x + settings.MODAL_INPUT_PADDING
        text_y = self.title_input_rect.y + settings.MODAL_INPUT_PADDING
        start_index, end_index = min(self.selection_start, self.selection_end), max(self.selection_start, self.selection_end)
        text_before = self.edited_title[:start_index]
        text_selected = self.edited_title[start_index:end_index]
        text_after = self.edited_title[end_index:]
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
        if self.active_field == 'title' and self.cursor_visible and self.selection_start == self.selection_end:
            cursor_pos_x = text_x + self.font_titulo.size(self.edited_title[:self.selection_end])[0]
            cursor_height = self.font_titulo.get_height()
            pygame.draw.line(screen, settings.COR_TEXTO_TITULO, (cursor_pos_x, text_y), (cursor_pos_x, text_y + cursor_height), 2)