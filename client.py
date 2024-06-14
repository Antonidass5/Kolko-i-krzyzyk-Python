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
purple = (128, 0, 128)

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
        pygame.draw.line(win, black, (120 * i, 40), (120 * i, 400), 5)
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
    if not startgame:
        draw_text(f"Oczekiwanie na przeciwnika", (0, 0), purple)
        return
    if result == " ":
        sign = "O" if is_player_one else "X"
        if my_turn:
            draw_text(f"Twój ruch ({sign})", (0, 0), green)
        else:
            draw_text(f"Ruch przeciwnika ({sign})", (0, 0), red)
        return
    if (result == "O" and is_player_one) or (result == "X" and not is_player_one):
        draw_text("Wygrałeś", (120, 0), green)
    elif (result == "O" and not is_player_one) or (result == "X" and is_player_one):
        draw_text("Przegrałeś", (120, 0), red)
    else:
        draw_text("Remis", (120, 0), blue)

    draw_text("Powrót do menu", (110, 370), blue)


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
        board[idx] = "O" if is_player_one else "X"
        draw_board()
        client.send(f"MOVE {idx} {board[idx]}".encode('utf-8'))
        my_turn = False


def check_is_win():
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # poziome
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # pionowe
        [0, 4, 8], [2, 4, 6]  # ukośne
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] != ' ':
            return board[condition[0]]
    if ' ' not in board:
        return "D"
    return " "


def reset_game():
    global board, my_turn, startgame, is_player_one
    board = [' ' for _ in range(9)]
    my_turn = False
    startgame = False
    is_player_one = True


# Funkcja główna
def main():
    while True:
        global client, room_id, my_turn, run, is_player_one, startgame
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

        if room_id:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('127.0.0.1', 5555))

            if room_id == "new_room":
                client.send("CREATE_ROOM".encode('utf-8'))
                my_turn = True
            else:
                client.send("JOIN_ROOM".encode('utf-8'))
                my_turn = False
                startgame = True

            thread = threading.Thread(target=receive_data)
            thread.start()

            while run:
                draw_board()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        pygame.quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        if check_is_win() != " " and 110 <= x <= 250 and 370 <= y <= 400:
                            reset_game()
                            return main()  # Restart the game
                        if my_turn and check_is_win() == " " and pygame.mouse.get_focused() and startgame:
                            col = x // 120
                            row = (y - 40) // 120
                            if 0 <= col < 3 and 0 <= row < 3:
                                idx = row * 3 + col
                                send_move(idx)


if __name__ == "__main__":
    main()
