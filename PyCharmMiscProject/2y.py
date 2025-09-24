import pygame
import sys
import os
import random

pygame.init()

# ==================== CONFIGURAÇÕES BÁSICAS ====================
# Configura o jogo para tela cheia
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Pixel Hopper 3000")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
YELLOW = (255, 220, 80)
ORANGE = (255, 150, 40)
HIGHLIGHT_BG = (255, 255, 150)
HIGHLIGHT_BORDER = (150, 150, 0)
BUTTON_TEXT_COLOR = (40, 40, 40)
TEXT_BETA_COLOR = (200, 200, 200)
BLACK = (0, 0, 0)
CURSOR_COLOR = (255, 255, 255)

# ===================== FONTES ====================
try:
    font_file_path = 'assets/fonts/Minecraftia-Regular.ttf'
    FONT_BIG = pygame.font.Font(font_file_path, int(HEIGHT * 0.1))
    FONT_SMALL = pygame.font.Font(font_file_path, int(HEIGHT * 0.05))
    FONT_TINY = pygame.font.Font(font_file_path, int(HEIGHT * 0.025))
    FONT_MED_INTRO = pygame.font.Font(font_file_path, int(HEIGHT * 0.03))

except FileNotFoundError:
    print("Aviso: Arquivo de fonte não encontrado. Usando fonte padrão do sistema.")
    FONT_BIG = pygame.font.SysFont("Arial", 64, bold=True)
    FONT_SMALL = pygame.font.SysFont("Arial", 28, bold=True)
    FONT_TINY = pygame.font.SysFont("Arial", 14)
    FONT_MED_INTRO = pygame.font.SysFont("Arial", 14)

# Mensagem completa para a introdução
intro_message = (
    "Olá, bravo aventureiro!\n"
    "Você decidiu enfrentar este mundo sozinho, e isso já mostra sua coragem.\n\n"
    "O desafio que o espera é intenso: 10 fases cheias de plataformas, "
    "inimigos astutos e segredos escondidos.\n\n"
    "Progresso Salvo: não se preocupe, cada passo da sua jornada é registrado. "
    "Se precisar fazer uma pausa, poderá continuar exatamente de onde parou.\n\n"
    "Suas Vidas: você começa com 5 vidas, mas o mapa guarda bônus e mistérios "
    "que podem aumentar suas chances. Explore cada canto; a curiosidade pode "
    "trazer recompensas inesperadas!\n\n"
    "Dicas para o Herói:\n\n"
    "– Observe o cenário: algumas plataformas escondem atalhos.\n\n"
    "– Preste atenção nos inimigos com poderes especiais; aprender seus padrões "
    "é a chave para vencê-los.\n\n"
    "– Colete moedas e itens brilhantes: eles podem lhe dar energia extra.\n\n"
    "Quando sentir que está pronto para a aventura, pressione Enter e embarque "
    "nesta missão épica.\n\n"
    "Boa sorte e divirta-se no Pixel Hopper 3000!"
)


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
]


# ==================== FUNÇÕES AUXILIARES ====================
def draw_background():
    screen.blit(BACKGROUND_IMAGE, (0, 0))


def draw_text_with_outline(text, font, x, y, main_color, outline_color):
    base = font.render(text, True, outline_color)
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        screen.blit(base, (x + dx, y + dy))
    screen.blit(font.render(text, True, main_color), (x, y))


def show_intro_message(screen, clock, message, font):
    fade = pygame.Surface(screen.get_size())
    fade.fill((0, 0, 0))

    for alpha in range(0, 255, 5):
        fade.set_alpha(alpha)
        draw_background()
        screen.blit(fade, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    pygame.time.delay(1000)

    start_time = pygame.time.get_ticks()
    text_speed = 40  # Aumentado para 40 para uma escrita mais lenta

    margin_x = int(WIDTH * 0.05)
    margin_y = int(HEIGHT * 0.1)
    text_area_width = WIDTH - 2 * margin_x
    line_height = font.get_height() + 8

    message_lines = message.split('\n')

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        screen.fill(BLACK)

        current_time = pygame.time.get_ticks()
        time_elapsed = current_time - start_time
        num_chars_to_show = int(time_elapsed / text_speed)

        y_offset = margin_y
        total_chars_drawn = 0
        last_line_width = 0

        message_complete = False

        for line in message_lines:
            words = line.split(' ')
            wrapped_line = ''
            for word in words:
                test_line = wrapped_line + ' ' + word if wrapped_line else word
                if font.size(test_line)[0] <= text_area_width:
                    wrapped_line = test_line
                else:
                    chars_to_draw_in_line = min(len(wrapped_line), num_chars_to_show - total_chars_drawn)
                    typed_part = wrapped_line[:chars_to_draw_in_line]
                    img = font.render(typed_part, True, WHITE)
                    screen.blit(img, (margin_x, y_offset))
                    total_chars_drawn += chars_to_draw_in_line
                    if num_chars_to_show <= total_chars_drawn:
                        last_line_width = font.size(typed_part)[0]
                        message_complete = False
                        break

                    y_offset += line_height
                    wrapped_line = word

            if not message_complete:
                chars_to_draw_in_line = min(len(wrapped_line), num_chars_to_show - total_chars_drawn)
                typed_part = wrapped_line[:chars_to_draw_in_line]
                img = font.render(typed_part, True, WHITE)
                screen.blit(img, (margin_x, y_offset))
                total_chars_drawn += chars_to_draw_in_line
                last_line_width = font.size(typed_part)[0]
                y_offset += line_height
                if num_chars_to_show <= total_chars_drawn:
                    message_complete = False
                    break
        else:
            message_complete = True

        # Desenha o cursor DURANTE a digitação
        if not message_complete:
            blink_on = (current_time // 300) % 2
            if blink_on:
                cursor_pos_x = margin_x + last_line_width
                cursor_pos_y = y_offset - line_height
                cursor_rect = pygame.Rect(cursor_pos_x, cursor_pos_y, 4, font.get_height())
                pygame.draw.rect(screen, CURSOR_COLOR, cursor_rect)

        # Desenha o prompt com cursor piscando APÓS a digitação
        if message_complete:
            prompt_text = "Pressione ENTER para continuar"
            prompt_surf = FONT_TINY.render(prompt_text, True, WHITE)
            prompt_rect = prompt_surf.get_rect(center=(WIDTH // 2, HEIGHT - int(HEIGHT * 0.05)))

            blink_on = (current_time // 300) % 2
            if blink_on:
                prompt_text_with_cursor = prompt_text + "_"
                prompt_surf = FONT_TINY.render(prompt_text_with_cursor, True, WHITE)
                prompt_rect = prompt_surf.get_rect(center=(WIDTH // 2, HEIGHT - int(HEIGHT * 0.05)))

            screen.blit(prompt_surf, prompt_rect)

        pygame.display.flip()
        clock.tick(60)


# ===================== GAME LOOP ====================
def game_loop():
    current_level = 0
    all_sprites = pygame.sprite.Group()

    def load_level(level_index):
        nonlocal all_sprites
        all_sprites.empty()

        if level_index >= len(LEVEL_DATA):
            print("Fim do jogo!")
            return False

        level_data = LEVEL_DATA[level_index]
        print(f"Carregando Fase {level_index + 1}...")

        return True

    if not load_level(current_level):
        return

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        draw_background()
        all_sprites.update()
        all_sprites.draw(screen)

        beta_text = FONT_TINY.render("Mb game (beta_test)", True, TEXT_BETA_COLOR)
        screen.blit(beta_text, (5, HEIGHT - int(HEIGHT * 0.04)))

        pygame.display.flip()
        clock.tick(60)


# ===================== TELA INICIAL ====================
def title_screen():
    options = ["1 PLAYER", "2 PLAYERS"]
    selected = 0

    button_width = int(WIDTH * 0.3)
    button_height = int(HEIGHT * 0.1)
    button_margin = int(HEIGHT * 0.05)

    button_rects = []
    for i, text in enumerate(options):
        rect_x = WIDTH // 2 - button_width // 2
        rect_y = HEIGHT // 2 + (i - 0.5) * (button_height + button_margin)
        rect = pygame.Rect(rect_x, rect_y, button_width, button_height)
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
                    if selected == 0:
                        show_intro_message(screen, clock, intro_message, FONT_MED_INTRO)
                        game_loop()
                    elif selected == 1:
                        pass
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rects[selected].collidepoint(mouse_pos):
                    if selected == 0:
                        show_intro_message(screen, clock, intro_message, FONT_MED_INTRO)
                        game_loop()
                    elif selected == 1:
                        pass
                    return

        draw_background()

        title_text = "PIXEL HOPPER 3000"
        title_surf = FONT_BIG.render(title_text, True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - int(HEIGHT * 0.2)))
        draw_text_with_outline(title_text, FONT_BIG, title_rect.x, title_rect.y, ORANGE, (0, 0, 0))

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
        screen.blit(beta_text, (5, HEIGHT - int(HEIGHT * 0.04)))

        pygame.display.flip()
        clock.tick(60)


# ===================== MAIN ====================
def main():
    title_screen()


if __name__ == "__main__":
    main()