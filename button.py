import pygame

class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_clicked(self, pos):
        if self.rect.collidepoint(pos):
            self.clicked = True
        else:
            self.clicked = False
          
        return self.clicked