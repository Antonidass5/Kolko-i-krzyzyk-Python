import pygame
import socket
import threading

# Inicjalizacja Pygame
pygame.init()

# Ustawienia ekranu
screen_width = 400
screen_height = 300
win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tic Tac Toe - Multiplayer")

# Kolory
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)

# Czcionka
font = pygame.font.Font(None, 36)

# Zmienna globalna dla pokoju
room_id = None
client = None
my_turn = False
board = [' ' for _ in range(9)]
run = True

# Funkcje interfejsu graficznego
def draw_text(text, pos, color=black):
    text_surface = font.render(text, True, color)
    win.blit(text_surface, pos)

def draw_menu():
    win.fill(white)
    draw_text("Stwórz nowy pokój", (100, 100))
    draw_text("Dołącz do pokoju", (100, 150))
    pygame.display.update()

def draw_board():
    win.fill(white)
    for i in range(1, 3):
        pygame.draw.line(win, black, (100 * i, 0), (100 * i, 300), 5)
        pygame.draw.line(win, black, (0, 100 * i), (300, 100 * i), 5)
    for idx, val in enumerate(board):
        if val != ' ':
            x = (idx % 3) * 100 + 50
            y = (idx // 3) * 100 + 50
            text = font.render(val, True, black)
            win.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))
    pygame.display.update()

# Funkcje sieciowe
def receive_data():
    global my_turn, board, run
    while run:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith("MOVE"):
                idx, player = message.split()[1:]
                board[int(idx)] = player
                my_turn = not my_turn
                draw_board()
        except:
            break

def send_move(idx):
    global my_turn
    if board[idx] == ' ' and my_turn:
        board[idx] = 'X'
        draw_board()
        client.send(f"MOVE {idx} X".encode('utf-8'))
        my_turn = False

# Funkcja główna
def main():
    global client, room_id, my_turn, run
    in_menu = True

    while in_menu:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 100 <= x <= 300 and 100 <= y <= 130:
                    room_id = "new_room"
                    in_menu = False
                if 100 <= x <= 300 and 150 <= y <= 180:
                    room_id = "join_room"
                    in_menu = False

    # Po wyborze pokoju
    if room_id:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 5555))

        # Wyślij informacje o pokoju do serwera
        if room_id == "new_room":
            client.send("CREATE_ROOM".encode('utf-8'))
            my_turn = True  # Pierwszy gracz
        else:
            client.send("JOIN_ROOM".encode('utf-8'))
            my_turn = False  # Drugi gracz

        thread = threading.Thread(target=receive_data)
        thread.start()

        while run:
            draw_board()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN and my_turn:
                    x, y = pygame.mouse.get_pos()
                    col = x // 100
                    row = y // 100
                    idx = row * 3 + col
                    send_move(idx)

if __name__ == "__main__":
    main()
