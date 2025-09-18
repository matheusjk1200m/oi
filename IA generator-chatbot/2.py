import pygame
import sys
import os
import random

pygame.init()

WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Hopper 3000")

# ===================== CORES =====================
WHITE = (255, 255, 255)
YELLOW = (255, 220, 80)
ORANGE = (255, 150, 40)
HIGHLIGHT_BG = (255, 255, 150)
HIGHLIGHT_BORDER = (150, 150, 0)
BUTTON_TEXT_COLOR = (40, 40, 40)
TEXT_BETA_COLOR = (200, 200, 200)

# ===================== FONTES ====================
try:
    font_path = pygame.font.match_font('pressstart2p', bold=True)
    if font_path:
        FONT_BIG = pygame.font.Font(font_path, 64)
        FONT_SMALL = pygame.font.Font(font_path, 28)
        FONT_TINY = pygame.font.Font(font_path, 14)
    else:
        FONT_BIG = pygame.font.SysFont("Arial", 64, bold=True)
        FONT_SMALL = pygame.font.SysFont("Arial", 28, bold=True)
        FONT_TINY = pygame.font.SysFont("Arial", 14)
except FileNotFoundError:
    FONT_BIG = pygame.font.SysFont("Arial", 64, bold=True)
    FONT_SMALL = pygame.font.SysFont("Arial", 28, bold=True)
    FONT_TINY = pygame.font.SysFont("Arial", 14)


# ===================== SPRITES E IMAGENS ====================
class SpriteSheet:
    def __init__(self, filename):
        if os.path.exists(filename):
            self.sprite_sheet = pygame.image.load(filename).convert_alpha()
        else:
            surf = pygame.Surface((16, 16), pygame.SRCALPHA)
            surf.fill((255, 0, 0))
            self.sprite_sheet = surf

    def get_image(self, x, y, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return pygame.transform.scale(image, (width * scale, height * scale))


try:
    BACKGROUND_IMAGE = pygame.image.load('assets/montanha.png').convert()
    BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT))
    # Carregue os sprites aqui (exemplo)
    # mario_sheet = SpriteSheet('assets/mario.png')
    # blocks_sheet = SpriteSheet('assets/blocks.png')
    # ...
except pygame.error as e:
    print(f"Erro ao carregar imagem de fundo: {e}")
    print("Verifique se o arquivo 'montanha.png' está na pasta 'assets' e o nome está correto.")
    sys.exit()


# ===================== OBJETOS ====================
class Block(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))


class Character(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.gravity = 0.5

    def update(self):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y


# ===================== DADOS DAS FASES ====================
# A lista de dicionários com as posições dos objetos para cada fase
LEVEL_DATA = [
    {  # Fase 1
        'blocks': [(100, 300), (200, 300), (300, 300)],
        'enemies': [(150, 250), (450, 250)],
        'player_start': (50, 400),
    },
    {  # Fase 2
        'blocks': [(100, 200), (400, 300), (600, 250)],
        'enemies': [(250, 150), (700, 200)],
        'player_start': (50, 400),
    },
    # ... adicione mais 8 dicionários para completar as 10 fases
]


# ===================== FUNÇÃO DE FUNDO ====================
def draw_background():
    screen.blit(BACKGROUND_IMAGE, (0, 0))


# ===================== GAME LOOP ====================
def game_loop():
    current_level = 0
    all_sprites = pygame.sprite.Group()

    # Função para carregar a fase atual
    def load_level(level_index):
        nonlocal all_sprites
        all_sprites.empty()  # Remove todos os sprites da fase anterior

        level_data = LEVEL_DATA[level_index]

        # Cria os blocos
        # Exemplo: for pos in level_data['blocks']:
        #              block = Block(blocks_sheet.get_image(...), pos[0], pos[1])
        #              all_sprites.add(block)

        # Cria o jogador
        # Exemplo: player = Character(mario_sheet.get_image(...), level_data['player_start'][0], level_data['player_start'][1])
        # all_sprites.add(player)

        # Cria os inimigos
        # Exemplo: for pos in level_data['enemies']:
        #              enemy = Character(enemies_sheet.get_image(...), pos[0], pos[1])
        #              all_sprites.add(enemy)

    # Inicia a primeira fase
    load_level(current_level)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_background()
        all_sprites.update()
        all_sprites.draw(screen)

        beta_text = FONT_TINY.render("Mb game (beta_test)", True, TEXT_BETA_COLOR)
        screen.blit(beta_text, (5, HEIGHT - 20))

        pygame.display.flip()
        clock.tick(60)


# ===================== TELA INICIAL ====================
def draw_text_with_outline(text, font, x, y, main_color, outline_color):
    base = font.render(text, True, outline_color)
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        screen.blit(base, (x + dx, y + dy))
    screen.blit(font.render(text, True, main_color), (x, y))


def title_screen():
    options = ["1 PLAYER", "2 PLAYERS"]
    selected = 0
    clock = pygame.time.Clock()

    button_rects = []
    for i, text in enumerate(options):
        rect_x = WIDTH // 2 - 120
        rect_y = 260 + i * 70
        rect = pygame.Rect(rect_x, rect_y, 240, 50)
        button_rects.append(rect)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for i, rect in enumerate(button_rects):
            if rect.collidepoint(mouse_pos):
                selected = i

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rects[selected].collidepoint(mouse_pos):
                    return

        draw_background()

        draw_text_with_outline("PIXEL HOPPER 3000", FONT_BIG,
                               WIDTH // 2 - FONT_BIG.render("PIXEL HOPPER 3000", True, (0, 0, 0)).get_width() // 2, 70,
                               ORANGE, (0, 0, 0))

        time_ms = pygame.time.get_ticks()
        blink = (time_ms // 300) % 2

        for i, text in enumerate(options):
            is_sel = (i == selected)
            rect = button_rects[i]

            if is_sel:
                pygame.draw.rect(screen, HIGHLIGHT_BG, rect, 0, 10)
                if blink:
                    pygame.draw.rect(screen, HIGHLIGHT_BORDER, rect, 4, 10)

            text_surf = FONT_SMALL.render(text, True, BUTTON_TEXT_COLOR)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

        beta_text = FONT_TINY.render("Mb game (beta_test)", True, TEXT_BETA_COLOR)
        screen.blit(beta_text, (5, HEIGHT - 20))

        pygame.display.flip()
        clock.tick(60)


# ===================== MAIN ====================
def main():
    title_screen()
    game_loop()


if __name__ == "__main__":
    main()