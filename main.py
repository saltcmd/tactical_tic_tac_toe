import math
import json

# Initialize the Ultimate Tic Tac Toe Board
def create_board():
    # A 3x3 grid of 3x3 boards
    return [[[[' ' for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]

def print_board(board, last_move=None):
    """
    Prints the Ultimate Tic Tac Toe board with the most recent move highlighted in green.

    Parameters:
        board: The 3x3 grid of 3x3 boards.
        last_move: Tuple of (big_row, big_col, small_row, small_col) indicating the last move.
    """

    print("\nUltimate Tic Tac Toe Board:\n")
    for big_row in range(3):
        for small_row in range(3):
            row = []
            for big_col in range(3):
                for small_col in range(3):
                    # Highlight the last move in green
                    if last_move == (big_row, big_col, small_row, small_col):
                        row.append(f"\033[92m{board[big_row][big_col][small_row][small_col]}\033[0m")
                    else:
                        row.append(board[big_row][big_col][small_row][small_col])
                row.append('|')  # Add separator for small boards
            print(' '.join(row[:-1]))  # Print the row without the trailing separator
        print('-' * 22 if big_row != 2 else '')   # Separator for big boards
    print("\n")

# Winning and Game Status Functions
def check_winner(board, player):
    # Check if a specific 3x3 board has a winner
    for row in board:
        if all(cell == player for cell in row):
            return True
    for col in range(3):
        if all(row[col] == player for row in board):
            return True
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2 - i] == player for i in range(3)):
        return True
    return False

def check_ultimate_winner(big_board, player):
    # Check if the larger board has a winner
    return check_winner(big_board, player)

def check_small_board_full(board):
    # Check if a specific 3x3 board is full
    return all(cell != ' ' for row in board for cell in row)

def check_big_board_full(big_board):
    # Check if the entire game is full
    return all(check_small_board_full(board) for row in big_board for board in row)

# Evaluate the board for heuristic scoring
def evaluate_board(big_board):
    score = 0
    # Evaluate each small board
    for big_row in range(3):
        for big_col in range(3):
            score += evaluate_small_board(big_board[big_row][big_col], 'O')  # Player (O)
            score -= evaluate_small_board(big_board[big_row][big_col], 'X')  # Opponent (X)
    return score

def evaluate_small_board(board, player):
    # Unfinished boards contribute to the score based on the number of player's pieces
    player_count = sum(row.count(player) for row in board)
    return player_count


# Minimax Algorithm with Alpha-Beta Pruning
def minimax(big_board, active_row, active_col, is_maximizing, depth, alpha, beta, max_depth=5):
    # Depth-limiting for better performance
    if depth >= max_depth:
        return evaluate_board(big_board)

    # Check terminal states for the maximizing/minimizing player
    if check_ultimate_winner(big_board, 'X'):  # Opponent wins
        return -10 + depth
    if check_ultimate_winner(big_board, 'O'):  # Player wins
        return 10 - depth
    if check_big_board_full(big_board):  # Tie
        return 0

    active_board = big_board[active_row][active_col]
    if is_maximizing:  # Maximizing player ('O')
        best_score = -math.inf
        for row in range(3):
            for col in range(3):
                if active_board[row][col] == ' ':
                    active_board[row][col] = 'O'

                    # Immediate winning check
                    if check_winner(active_board, 'O'):
                        active_board[row][col] = ' '  # Undo
                        return 10 - depth  # Immediate win

                    # Recursive call
                    score = minimax(big_board, row, col, False, depth + 1, alpha, beta, max_depth)
                    active_board[row][col] = ' '  # Undo the move
                    best_score = max(best_score, score)
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        break  # Prune
        return best_score
    else:  # Minimizing player ('X')
        best_score = math.inf
        for row in range(3):
            for col in range(3):
                if active_board[row][col] == ' ':
                    active_board[row][col] = 'X'

                    # Immediate winning check
                    if check_winner(active_board, 'X'):
                        active_board[row][col] = ' '  # Undo
                        return -10 + depth  # Immediate loss

                    # Recursive call
                    score = minimax(big_board, row, col, True, depth + 1, alpha, beta, max_depth)
                    active_board[row][col] = ' '  # Undo the move
                    best_score = min(best_score, score)
                    beta = min(beta, score)
                    if beta <= alpha:
                        break  # Prune
        return best_score
def danger_likelihood_for_move(big_board, move):
    """
    Calculate the likelihood that a move will lead to an opponent win.

    Parameters:
        big_board: The current state of the 3x3 grid of 3x3 boards.
        move: Tuple (small_row, small_col) representing the player's move.
    Returns:
        danger_percentage: A float in the range 0-100, representing how likely
        this move is to allow the opponent to win on their next turn.
    """
    # Determine which board the opponent will be sent to
    next_row, next_col = move
    directed_board = big_board[next_row][next_col]

    # Check if the directed board is already won or full
    if check_small_board_full(directed_board) or check_winner(directed_board, 'O') or check_winner(directed_board, 'X'):
        return 0  # No danger if the game can't continue there

    # Simulate all possible moves the opponent could make on the directed board
    opponent_winning_moves = 0
    total_possible_moves = 0
    for row in range(3):
        for col in range(3):
            if directed_board[row][col] == ' ':
                total_possible_moves += 1
                # Simulate the opponent's move
                directed_board[row][col] = 'X'
                if check_winner(directed_board, 'X'):  # Check if opponent wins
                    opponent_winning_moves += 1
                directed_board[row][col] = ' '  # Undo the simulated move

    # Calculate the likelihood of danger as a percentage
    if total_possible_moves == 0:
        return 0  # No danger if no more moves are possible
    danger_percentage = (opponent_winning_moves / total_possible_moves) * 100
    return danger_percentage
def best_move_with_details(big_board, active_row, active_col):
    """
    Determine the best move for the player ('O'), incorporating both strategic scoring and
    opponent win likelihood penalties.

    Parameters:
        big_board: The 3x3 grid of 3x3 boards.
        active_row: The row index of the current active small board.
        active_col: The column index of the current active small board.
    Returns:
        move: The best move as a tuple (small_row, small_col).
        scores: Raw Minimax scores for each potential move.
        normalized_scores: Pseudo-probability distribution of scores.
        dangers: Opponent win likelihood for each potential move.
    """
    active_board = big_board[active_row][active_col]
    scores = {}  # For raw Minimax scores
    dangers = {}  # For danger likelihood
    adjusted_scores = {}  # For Minimax scores adjusted by danger likelihood
    best_score = -math.inf
    move = None

    for row in range(3):
        for col in range(3):
            if active_board[row][col] == ' ':
                # Simulate the player's move
                active_board[row][col] = 'O'

                # Check if this move wins the small board outright
                if check_winner(active_board, 'O'):
                    active_board[row][col] = ' '  # Undo the move
                    return (row, col), {(row, col): float('inf')}, {(row, col): 100}, {(row, col): 0}

                # Undo the move
                active_board[row][col] = ' '

                # Calculate the opponent win likelihood if the player makes this move
                danger_percentage = danger_likelihood_for_move(big_board, (row, col))
                dangers[(row, col)] = danger_percentage

                # Evaluate the move using Minimax
                score = minimax(big_board, row, col, False, 0, -math.inf, math.inf, max_depth=3)
                scores[(row, col)] = score

                # Adjust the score by penalizing based on opponent win likelihood
                adjusted_score = score - (danger_percentage / 100) * 10  # Subtract a penalty
                adjusted_scores[(row, col)] = adjusted_score

                if adjusted_score > best_score:
                    best_score = adjusted_score
                    move = (row, col)  # Track the best move

    # Normalize the adjusted scores into a pseudo-probability distribution
    min_score = min(adjusted_scores.values()) if adjusted_scores else 0
    max_score = max(adjusted_scores.values()) if adjusted_scores else 1
    if max_score != min_score:
        normalized_scores = {key: (score - min_score) / (max_score - min_score) * 100 for key, score in adjusted_scores.items()}
    else:
        normalized_scores = {key: 100 / len(adjusted_scores) for key in adjusted_scores} if adjusted_scores else {}

    return move, scores, normalized_scores, dangers

def save_game(big_board, active_row, active_col, last_move, filename="saved_game.json"):
    """
    Saves the current game state to a file.
    Parameters:
        big_board: The current state of the 3x3 grid of 3x3 boards.
        active_row: The row index of the active small board.
        active_col: The column index of the active small board.
        last_move: The last move made in the game (or None if no move has been made).
        filename: The name of the file to save the game state (default is "saved_game.json").
    """
    game_state = {
        "big_board": big_board,  # Saving the entire board
        "active_row": active_row,
        "active_col": active_col,
        "last_move": last_move,
    }
    with open(filename, "w") as file:
        json.dump(game_state, file)
    print(f"Game saved successfully to {filename}!")

def load_game(filename="saved_game.json"):
    """
    Loads a previously saved game state from a file.
    Parameters:
        filename: The name of the file to load the game state (default is "saved_game.json").
    Returns:
        A tuple (big_board, active_row, active_col, last_move) representing the restored game state.
    """
    try:
        with open(filename, "r") as file:
            game_state = json.load(file)
        print(f"Game loaded successfully from {filename}!")
        return (
            game_state["big_board"],
            game_state["active_row"],
            game_state["active_col"],
            game_state["last_move"],
        )
    except FileNotFoundError:
        print(f"No saved game found with the name {filename}. Starting a new game.")
        return create_board(), 0, 0, None  # Return a new game state if file not found
    except json.JSONDecodeError:
        print(f"Error reading the saved game. Starting a new game.")
        return create_board(), 0, 0, None  # Handle corrupted/invalid save file

# Main Function for Input and Gameplay updated to utilize details
def play_ultimate_tic_tac_toe():
    print("Do you want to load a previous game? (yes/no):")
    if input().strip().lower() == "yes":
        big_board, active_row, active_col, last_move = load_game()
    else:
        big_board = create_board()
        active_row, active_col = 0, 0  # Start in the top-left small board
        last_move = None  # To track the last move

    while True:
        # Player's move
        print_board(big_board, last_move)
        print(f"Your move must be in the small board at ({active_row}, {active_col}).")

        # Allow the user to pick a different small board if the designated one is full
        if check_small_board_full(big_board[active_row][active_col]):
            print(f"The designated small board at ({active_row}, {active_col}) is full.")
            while True:
                print("Please select a new small board as 'big_row big_col':")
                try:
                    new_row, new_col = map(int, input().strip().split())
                    if (
                        0 <= new_row < 3
                        and 0 <= new_col < 3
                        and not check_small_board_full(big_board[new_row][new_col])
                    ):
                        active_row, active_col = new_row, new_col
                        print(f"Active small board changed to ({active_row}, {active_col}).")
                        break
                    else:
                        print("Invalid choice. Either out of bounds or the selected small board is full.")
                except ValueError:
                    print("Invalid input. Use 'big_row big_col' format (e.g., '1 2').")

        while True:
            print("Enter your move as 'row col', type 'save' to save the game, or type 'help' for a suggestion:")
            your_input = input().strip()
            # When the player asks for "help"
            if your_input.lower() == "help":
                suggestion, raw_scores, normalized_scores, dangers = best_move_with_details(big_board, active_row, active_col)

                if suggestion is None:
                    print("No completely safe moves are available. Here is the risk evaluation for each move:\n")
                    for move, danger in dangers.items():
                        print(f"Move {move}: Opponent win likelihood: {danger:.2f}%")
                else:
                    print(f"The best move is: \033[92m{suggestion}\033[0m")
                    print("Move evaluation (Minimax scores with penalties):")
                    for move, score in raw_scores.items():
                        print(f" Move {move}: Raw Score {score:.2f} | Winning Likelihood: {normalized_scores[move]:.2f}% | Opponent Win Likelihood: {dangers[move]:.2f}%")
                continue
            if your_input.lower() == "save":
                save_game(big_board, active_row, active_col, last_move)
                continue  # Keep playing after saving
            try:
                your_row, your_col = map(int, your_input.split())
                if (
                    0 <= your_row < 3
                    and 0 <= your_col < 3
                    and big_board[active_row][active_col][your_row][your_col] == ' '
                ):
                    big_board[active_row][active_col][your_row][your_col] = 'O'
                    last_move = (active_row, active_col, your_row, your_col)  # Update the last move
                    active_row, active_col = your_row, your_col
                    break
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Invalid input. Please use row col format (e.g., '1 2').")

        # Check for game end conditions
        if check_ultimate_winner(big_board, 'O'):
            print_board(big_board, last_move)
            print("You win!")
            break
        if check_big_board_full(big_board):
            print_board(big_board, last_move)
            print("It's a draw!")
            break

        # Opponent's move
        print_board(big_board, last_move)
        print(f"Opponent's move is in the small board at ({active_row}, {active_col}).")

        # Allow the opponent to pick a new small board if the designated one is full
        if check_small_board_full(big_board[active_row][active_col]):
            print(f"The designated small board at ({active_row}, {active_col}) is full.")
            while True:
                print("Opponent, please select a new small board as 'big_row big_col':")
                try:
                    new_row, new_col = map(int, input().strip().split())
                    if (
                        0 <= new_row < 3
                        and 0 <= new_col < 3
                        and not check_small_board_full(big_board[new_row][new_col])
                    ):
                        active_row, active_col = new_row, new_col
                        print(f"Opponent's active small board changed to ({active_row}, {active_col}).")
                        break
                    else:
                        print("Invalid choice. Either out of bounds or the selected small board is full.")
                except ValueError:
                    print("Invalid input. Use 'big_row big_col' format (e.g., '1 2').")

        while True:
            print("Enter opponent's move as 'row col':")
            opp_input = input().strip()
            try:
                opp_row, opp_col = map(int, opp_input.split())
                if (
                    0 <= opp_row < 3
                    and 0 <= opp_col < 3
                    and big_board[active_row][active_col][opp_row][opp_col] == ' '
                ):
                    big_board[active_row][active_col][opp_row][opp_col] = 'X'
                    last_move = (active_row, active_col, opp_row, opp_col)  # Update the last move
                    active_row, active_col = opp_row, opp_col
                    break
                else:
                    print("Invalid move. Try again.")
            except ValueError:
                print("Invalid input. Please use row col format (e.g., '1 2').")

        # Check for game end conditions
        if check_ultimate_winner(big_board, 'X'):
            print_board(big_board, last_move)
            print("Opponent wins!")
            break
        if check_big_board_full(big_board):
            print_board(big_board, last_move)
            print("It's a draw!")
            break
# Run the game
play_ultimate_tic_tac_toe()
