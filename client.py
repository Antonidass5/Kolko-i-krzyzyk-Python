import pygame
import socket
import threading

# Inicjalizacja Pygame
pygame.init()

# Ustawienia ekranu
screen_width = 360
screen_height = 400
win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tic Tac Toe - Multiplayer")

# Kolory
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Czcionka
font = pygame.font.Font(None, 36)

# Zmienna globalna dla pokoju
room_id = None
client = None
my_turn = False
board = [' ' for _ in range(9)]
run = True
is_player_one = True
startgame = False

# Funkcje interfejsu graficznego
def draw_text(text, pos, color=black):
    text_surface = font.render(text, True, color)
    win.blit(text_surface, pos)


def draw_menu():
    win.fill(white)
    draw_text("Stwórz nowy pokój", (75, 150))
    draw_text("Dołącz do pokoju", (75, 200))
    pygame.display.update()


def draw_board():
    win.fill(white)
    for i in range(1, 3):
        pygame.draw.line(win, black, (120 * i, 0 + 40), (120 * i, 360 + 40), 5)
        pygame.draw.line(win, black, (0, 120 * i + 40), (360, 120 * i + 40), 5)
    for idx, val in enumerate(board):
        if val != ' ':
            x = (idx % 3) * 120 + 50
            y = (idx // 3) * 120 + 50 + 40
            text = font.render(val, True, black)
            win.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))
    draw_information(check_is_win())
    pygame.display.update()


def draw_information(result):
    if result == " ":
        sign = "O"
        if not is_player_one:
            sign = "X"
        if my_turn:
            draw_text(f"Twój ruch ({sign})", (0, 0), green)
        else:
            draw_text(f"Ruch przeciwnika ({sign})", (0, 0), red)
        return
    if (result == "O" and is_player_one) or (result == "X" and not is_player_one):
        draw_text("Wygrałeś", (120, 0), green)
    if (result == "O" and not is_player_one) or (result == "X" and is_player_one):
        draw_text("Przegrałeś", (120, 0), red)
    if result == "D":
        draw_text("Remis", (120, 0), blue)


# Funkcje sieciowe
def receive_data():
    global my_turn, board, run, startgame
    while run:
        try:

            message = client.recv(1024).decode('utf-8')
            if message.startswith("START_GAME") and is_player_one:
                startgame = True
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
        if is_player_one:
            board[idx] = "O"
        else:
            board[idx] = "X"
        draw_board()
        client.send(f"MOVE {idx} {board[idx]}".encode('utf-8'))
        my_turn = False


def check_is_win():
    for i in range(3):
        if board[i] == board[i + 1] and board[i + 1] == board[i + 2]:
            return board[i]
    for i in range(3):
        if board[i] == board[i + 3] and board[i + 3] == board[i + 6]:
            return board[i]
    if (board[0] == board[4] and board[4] == board[8]) or (board[2] == board[4] and board[4] == board[6]):
        return board[4]
    for field in board:
        if field == " ":
            return " "
    return "D"


# Funkcja główna
def main():
    global client, room_id, my_turn, run, is_player_one
    in_menu = True
    while in_menu:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 75 <= x <= 300 and 150 <= y <= 180:
                    room_id = "new_room"
                    in_menu = False
                if 75 <= x <= 300 and 200 <= y <= 230:
                    room_id = "join_room"
                    in_menu = False
                    is_player_one = False

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
            if startgame or not is_player_one:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
                    if event.type == pygame.MOUSEBUTTONDOWN and my_turn and check_is_win() == " " and pygame. mouse. get_focused():
                        x, y = pygame.mouse.get_pos()
                        col = x // 120
                        row = (y - 40) // 120
                        idx = row * 3 + col
                        send_move(idx)


if __name__ == "__main__":
    main()
