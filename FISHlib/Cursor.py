import pygame

class Cursor:
    """
    Classe Cursor pour gérer un curseur custom.

    Attributs:
    cursor_image (pygame.Surface): Texture du curseur à afficher.
    visible (bool): Indique si le curseur est visible ou non.

    Méthodes:
    update(): Met à jour la position du curseur selon la souris.
    draw(surface): Dessine le curseur sur la surface donnée si visible.
    show(): Rend le curseur visible.
    hide(): Cache le curseur.
    """

    def __init__(self, cursor_image: pygame.Surface):
        self.cursor_image = cursor_image
        self.visible = True

    def update(self):
        self.position = pygame.mouse.get_pos()

    def draw(self, surface):
        if self.visible:
            surface.blit(self.cursor_image, self.position)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False