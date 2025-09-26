# Arquivo: modal.py (ATUALIZADO)
import pygame
import settings

class EditModal:
    def __init__(self, task_to_edit):
        """Inicializa a janela modal com a tarefa a ser editada."""
        self.task = task_to_edit
        self.font_titulo = pygame.font.Font(None, settings.TAMANHO_FONTE_TITULO)
        self.font_menu = pygame.font.Font(None, settings.TAMANHO_FONTE_MENU)

        self.edited_title = task_to_edit.title
        self.edited_body = task_to_edit.body

        # Define as dimensões e posição da janela
        modal_width = settings.LARGURA_TELA * settings.MODAL_WIDTH_REL
        modal_height = settings.ALTURA_TELA * settings.MODAL_HEIGHT_REL
        self.modal_rect = pygame.Rect(0, 0, modal_width, modal_height)
        self.modal_rect.center = (settings.LARGURA_TELA / 2, settings.ALTURA_TELA / 2)

        # Define o botão de fechar 'X' usando constantes
        self.close_button_rect = pygame.Rect(
            self.modal_rect.right - settings.MODAL_CLOSE_BUTTON_SIZE - settings.MODAL_CLOSE_BUTTON_MARGIN,
            self.modal_rect.top + settings.MODAL_CLOSE_BUTTON_MARGIN,
            settings.MODAL_CLOSE_BUTTON_SIZE,
            settings.MODAL_CLOSE_BUTTON_SIZE
        )
        
        # Define o botão "Concluído" usando constantes
        self.concluido_button_rect = pygame.Rect(0, 0, settings.MODAL_DONE_BUTTON_WIDTH, settings.MODAL_DONE_BUTTON_HEIGHT)
        self.concluido_button_rect.bottomright = (
            self.modal_rect.right - settings.MODAL_DONE_BUTTON_MARGIN,
            self.modal_rect.bottom - settings.MODAL_DONE_BUTTON_MARGIN
        )

    def handle_event(self, event):
        """Processa um único evento. Retorna 'close' se a janela deve ser fechada."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button_rect.collidepoint(event.pos):
                return 'close'
        return None

    def draw(self, screen):
        """Desenha a janela modal e seus componentes na tela fornecida."""
        overlay = pygame.Surface((settings.LARGURA_TELA, settings.ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, settings.COR_FUNDO, self.modal_rect)
        pygame.draw.rect(screen, settings.COR_BORDA_RETANGULO, self.modal_rect, 2)

        # ### ALTERADO: Lógica de desenho do botão 'X'
        mouse_pos = pygame.mouse.get_pos()
        is_hovering_close = self.close_button_rect.collidepoint(mouse_pos)
        
        text_color = settings.MODAL_CLOSE_X_COLOR_NORMAL
        if is_hovering_close:
            pygame.draw.rect(screen, settings.MODAL_CLOSE_BG_COLOR_HOVER, self.close_button_rect)
            text_color = settings.MODAL_CLOSE_X_COLOR_HOVER
        
        close_text = self.font_titulo.render("X", True, text_color)
        close_text_rect = close_text.get_rect(center=self.close_button_rect.center)
        screen.blit(close_text, close_text_rect)

        # Botão "Concluído"
        pygame.draw.rect(screen, (200, 200, 200), self.concluido_button_rect)
        concluido_text = self.font_menu.render("Concluído", True, (0, 0, 0))
        concluido_text_rect = concluido_text.get_rect(center=self.concluido_button_rect.center)
        screen.blit(concluido_text, concluido_text_rect)