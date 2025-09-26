# Arquivo: task.py (VERSÃO CORRETA)
import pygame
import settings # Importa nosso novo arquivo de configurações

class TaskNode:
    def __init__(self, title, body, parent=None, pos=(10, 10), size=(200, 100)):
        self.title = title
        self.body = body
        self.parent = parent
        self.children = []
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.is_completed = False

    def add_child(self, child_node):
        self.children.append(child_node)

    def to_dict(self):
        return {
            'title': self.title,
            'body': self.body,
            'pos': (self.rect.x, self.rect.y),
            'children': [child.to_dict() for child in self.children]
        }

    @staticmethod
    def from_dict(data, parent=None): # <-- Assinatura correta, sem 'size'
        node = TaskNode(
            title=data['title'],
            body=data['body'],
            parent=parent,
            pos=data['pos'],
            size=settings.TAMANHO_RETANGULO # <-- Usa o valor direto de settings
        )
        for child_data in data['children']:
            child_node = TaskNode.from_dict(child_data, parent=node)
            node.add_child(child_node)
        return node