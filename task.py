# Ficheiro: task.py
import pygame
import settings

class TaskNode:
    def __init__(self, title, body, parent=None, pos=(10, 10), size=(200, 100)):
        self.title = title
        self.body = body
        self.parent = parent
        self.children = []
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.is_expanded = False
        self.status = 'normal' 

    # ### NOVO: Método para alterar o status em cascata ###
    def set_status(self, new_status):
        """Define o status para este nó e para todos os seus descendentes."""
        self.status = new_status
        for child in self.children:
            child.set_status(new_status) # A magia da recursão acontece aqui

    def add_child(self, child_node):
        self.children.append(child_node)

    def to_dict(self):
        """Converte este nó e todos os seus filhos em um dicionário."""
        return {
            'title': self.title,
            'body': self.body,
            'pos': (self.rect.x, self.rect.y),
            'is_expanded': self.is_expanded,
            'status': self.status,
            'children': [child.to_dict() for child in self.children]
        }

    @staticmethod
    def from_dict(data, parent=None):
        """Cria um nó (e todos os seus filhos) a partir de um dicionário."""
        node = TaskNode(
            title=data['title'],
            body=data['body'],
            parent=parent,
            pos=data['pos'],
            size=settings.TAMANHO_RETANGULO
        )
        node.is_expanded = data.get('is_expanded', False)
        node.status = data.get('status', 'normal')
        
        for child_data in data.get('children', []):
            child_node = TaskNode.from_dict(child_data, parent=node)
            node.add_child(child_node)
        return node
    def get_path(self):
        """Retorna o caminho único para este nó a partir da raiz."""
        path = []
        current = self
        # Sobe na árvore, adicionando os títulos ao início do caminho
        while current and current.parent:
            path.insert(0, current.title)
            current = current.parent
        return " > ".join(path)