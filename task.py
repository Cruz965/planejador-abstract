# Arquivo: task.py (CORRIGIDO)
import pygame
import settings
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
    def from_dict(data, size, parent=None): # <--- MUDANÇA AQUI: adicionado o parâmetro 'size'
        """Cria um nó (e todos os seus filhos) a partir de um dicionário."""
        node = TaskNode(
            title=data['title'],
            body=data['body'],
            parent=parent,
            pos=data['pos'],
            size=size # <--- MUDANÇA AQUI: usando o 'size' do parâmetro
        )
        for child_data in data['children']:
            # <--- MUDANÇA AQUI: passando 'size' na chamada recursiva
            child_node = TaskNode.from_dict(child_data, size, parent=node)
            node.add_child(child_node)
        return node