import tkinter as tk

empty = 0
black = 1
white = 2

directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

position_weights = [
    [100, -20, 10,  7.5,  7.5, 10, -20, 100],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [10,  -2,  -1, -1, -1, -1,  -2,  10],
    [10,   -2,  -1, -1, -1, -1,  -2,  10],
    [10,   -2,  -1, -1, -1, -1,  -2,   10],
    [10,  -2,  -1, -1, -1, -1,  -2,  10],
    [-20, -50, -2, -2, -2, -2, -50, -20],
    [100, -20, 10,  7.5,  7.5, 10, -20, 100],
]

def evaluate_board(game, player):
    opponent = game.get_opponent(player)
    score = 0
    for x in range(8):
        for y in range(8):
            if game.board[x][y] == player:
                score += position_weights[x][y]
            elif game.board[x][y] == opponent:
                score -= position_weights[x][y]
    return score

class othello_game:
    def __init__(self):
        self.board = [[empty for _ in range(8)] for _ in range(8)]
        self.board[3][3], self.board[4][4] = white, white
        self.board[3][4], self.board[4][3] = black, black
        self.current_player = black

    def is_on_board(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def get_opponent(self, player):
        return black if player == white else white

    def is_valid_move(self, player, x_start, y_start):
        if not self.is_on_board(x_start, y_start) or self.board[x_start][y_start] != empty:
            return False

        opponent = self.get_opponent(player)
        for dx, dy in directions:
            x, y = x_start + dx, y_start + dy
            pieces_to_flip = []

            while self.is_on_board(x, y) and self.board[x][y] == opponent:
                pieces_to_flip.append((x, y))
                x += dx
                y += dy

            if pieces_to_flip and self.is_on_board(x, y) and self.board[x][y] == player:
                return True
        return False

    def valid_moves(self, player):
        return [(x, y) for x in range(8) for y in range(8) if self.is_valid_move(player, x, y)]

    def make_move(self, player, x_start, y_start):
        if not self.is_valid_move(player, x_start, y_start):
            return False

        self.board[x_start][y_start] = player
        opponent = self.get_opponent(player)

        for dx, dy in directions:
            x, y = x_start + dx, y_start + dy
            pieces_to_flip = []

            while self.is_on_board(x, y) and self.board[x][y] == opponent:
                pieces_to_flip.append((x, y))
                x += dx
                y += dy

            if self.is_on_board(x, y) and self.board[x][y] == player:
                for fx, fy in pieces_to_flip:
                    self.board[fx][fy] = player

        self.current_player = opponent
        return True

    def get_score(self):
        b = sum(row.count(black) for row in self.board)
        w = sum(row.count(white) for row in self.board)
        return b, w

    def is_game_over(self):
        return not self.valid_moves(black) and not self.valid_moves(white)

    def best_move(self, player, depth=5):
        def minimax(game, depth, maximizing, alpha, beta):
            if depth == 0 or game.is_game_over():
                return evaluate_board(game, player), None

            valid_moves = game.valid_moves(player if maximizing else game.get_opponent(player))
            if not valid_moves:
                return minimax(game, depth - 1, not maximizing, alpha, beta)[0], None

            best_val = float('-inf') if maximizing else float('inf')
            best_mv = None

            for move in valid_moves:
                next_game = othello_game()
                next_game.board = [row[:] for row in game.board]
                next_game.current_player = game.current_player
                next_game.make_move(player if maximizing else game.get_opponent(player), move[0], move[1])

                eval, _ = minimax(next_game, depth - 1, not maximizing, alpha, beta)

                if maximizing:
                    if eval > best_val:
                        best_val = eval
                        best_mv = move
                    alpha = max(alpha, eval)
                else:
                    if eval < best_val:
                        best_val = eval
                        best_mv = move
                    beta = min(beta, eval)

                if beta <= alpha:
                    break

            return best_val, best_mv

        _, move = minimax(self, depth, True, float('-inf'), float('inf'))
        return move

class othello_gui:
    def __init__(self, root):
        self.root = root
        self.game = othello_game()
        self.cell_size = 65
        self.canvas = tk.Canvas(root, width=8*self.cell_size, height=8*self.cell_size, bg="darkgreen")
        self.canvas.pack()
        self.status_label = tk.Label(root, text="", font=("Arial", 14))
        self.status_label.pack()
        self.canvas.bind("<Button-1>", self.click_cell)
        self.update_board()

    def click_cell(self, event):
        x = event.y // self.cell_size
        y = event.x // self.cell_size
        if self.game.current_player == black:
            if self.game.make_move(black, x, y):
                self.update_board()
                self.root.after(500, self.handle_turns)
            else:
                self.status_label.config(text="Invalid move!")
                
    def handle_turns(self):
        while not self.game.is_game_over():
            current = self.game.current_player
            valid = self.game.valid_moves(current)
            if not valid:
                self.game.current_player = self.game.get_opponent(current)
                continue

            if current == white:
                move = self.game.best_move(white)
                if move:
                    self.game.make_move(white, move[0], move[1])
                    self.update_board()
                    self.root.after(500, self.handle_turns)
                return
            else:
                self.update_board()
                return

        self.update_board()

    def update_board(self):
        self.canvas.delete("all")
        for x in range(8):
            for y in range(8):
                x1 = y * self.cell_size
                y1 = x * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="darkgreen")

                piece = self.game.board[x][y]
                if piece != empty:
                    color = "black" if piece == black else "white"
                    margin = 8
                    self.canvas.create_oval(x1 + margin, y1 + margin, x2 - margin, y2 - margin, fill=color)
        if self.game.is_game_over():
            b, w = self.game.get_score()
            winner = "Black" if b > w else "White" if w > b else "Tie"
            self.status_label.config(text=f"Winner is: {winner} | Black: {b} White: {w}")
        else:
            player = "Black" if self.game.current_player == black else "White"
            self.status_label.config(text=f"Turn: {player}")

root = tk.Tk()
root.title("Othello")
gui = othello_gui(root)
root.mainloop()
