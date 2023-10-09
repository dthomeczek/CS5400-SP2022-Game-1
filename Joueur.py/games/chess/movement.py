# Used for the rank, file, and colors of the pieces for board structure
CHESS_RANK = ["a", "b", "c", "d", "e", "f", "g", "h"]
CHESS_FILE = ["1", "2", "3", "4", "5", "6", "7", "8"]
WHITE_CHESS_PIECES = ["P", "R", "N", "B", "Q", "K"]
BLACK_CHESS_PIECES = ["p", "r", "n", "b", "q", "k"]

# Builds a board based on the fen string provided
def parse_board(board_list):
    # Set board to make white the lower part of the board
    board_list.reverse()
    temp = []
    new_board = []
    for row in board_list:
        for index in row:
            if (index.isnumeric()):
                for i in range(int(index)):
                    temp.append(".")
            else:
                temp.append(index)
        new_board.append(temp)
        temp = []
    return new_board

# UCI format to grid coordinates
def uci_to_coords(uci_str):

    # Cuts out any promotion or attacks from moves to correlate to 4
    # character UCI easier
    move = clean(uci_str)
    rank_origin = move[0]
    file_origin = move[1]
    rank_end = move[2]
    file_end = move[3]
    row_origin = -1
    col_origin = -1
    row_end = -1
    col_end = -1
    for i in range(8):
        if (CHESS_RANK[i] == rank_origin):
            row_origin = i
        if (CHESS_FILE[i] == file_origin):
            col_origin = i
        if (CHESS_RANK[i] == rank_end):
            row_end = i
        if (CHESS_FILE[i] == file_end):
            col_end = i
    return (col_origin, row_origin, col_end, row_end)

# Reverts from coordinates to UCI form
def coords_to_uci(row, col):
    return (CHESS_RANK[col] + CHESS_FILE[row])

# Cleans up the UCI string to a simple 4 character form
# To do: Make it properly output when a Pawn is promoted with the UCI output
# Example: a7a8b, a7a8n, a7a8b, a7a8q would all be options
def clean(uci_str):
    move = uci_str
    if (len(uci_str) > 4):
        if ("x" in uci_str):
            move = move.replace("x", '')
        else:
            move = move[:-1]
    return move

# Gets all moves the Pawns can make
# To do: Get Pawns to capably promote to other pieces than just a Queen
def get_pawn_moves(chess_board, my_pieces, enemy_pieces, row, col):

    # Lists to each contain possible moves for a Pawn, whether it be 
    # first move forward 2, attacking forward left, forward right, or 
    # simply moving forward once, and stopping if blocked directly
    valid_tiles = []
    stay_column = []
    move_range = 2
    forward_moves = []
    diagonal = []
    right_forward = []
    left_forward = []
    if (my_pieces[0].isupper()):
        # First move Pawn can move forward 2 tiles
        if (row == 1):
            move_range = 3

        # Update list for range of movement
        for i in range(move_range):
            stay_column.append(col)

        # Move White Pawn forward
        if (row + 1 < 8):
            forward_moves = [zip(range(row + 1, row + move_range), stay_column)]
            # Check forward to the right
            if (col + 1 < 8):
                right_forward = [zip(range(row + 1, row + 2), range(col + 1, col + 2))]
            # Check forward to the left
            if (col - 1 > -1):
                left_forward = [zip(range(row + 1, row + 2), range(col - 1, col - 2, -1)),]
                
            # Add to diagonal options
            diagonal = right_forward + left_forward
    else:
        # First move Pawn can move forward 2 tiles
        if (row == 6):
            move_range = 3

        # Update list for range of movement
        for i in range(move_range):
            stay_column.append(col)

        # Move Black Pawn forward
        if (row - 1 > -1):
            forward_moves = [zip(range(row - 1, row - move_range, - 1), stay_column)]

            # Check forward to the right
            if (col + 1 < 8):
                right_forward = [zip(range(row - 1, row - 2, - 1), range(col + 1, col + 2))]
            # Check forward to the left
            if (col - 1 > -1):
                left_forward = [zip(range(row - 1, row - 2, - 1), range(col - 1, col - 2, -1)),]
                
            # Add to diagonal options
            diagonal = right_forward + left_forward

    # Build list of forward moves
    for direction in forward_moves:
        for pair in direction:
            # Stop if Pawn runs into own piece in front of it
            if (chess_board[pair[0]][pair[1]] in my_pieces or chess_board[pair[0]][pair[1]] in enemy_pieces):
                break

            valid_tiles.append(coords_to_uci(row, col) + coords_to_uci(pair[0], pair[1]))
    
    # Build list of diagonal moves
    for direction in diagonal:
        for pair in direction:
            # Stop if Pawn runs into an enemy piece in front of it
            if (chess_board[pair[0]][pair[1]] in enemy_pieces):
                valid_tiles.append(coords_to_uci(row, col) + coords_to_uci(pair[0], pair[1]))

    return valid_tiles

# Gets all moves for the Knights
def get_knight_moves(chess_board, enemy_pieces, row, col):
    directions = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
    valid_tiles = []
    for (x, y) in directions:
        x_new = row + x
        y_new = col + y
        if (-1 < x_new < 8 and -1 < y_new < 8):
            if (chess_board[x_new][y_new] == "." or chess_board[x_new][y_new] in enemy_pieces):
                valid_tiles.append(coords_to_uci(row, col) + coords_to_uci(x_new, y_new))

    return valid_tiles

# Gets diagonal directions (used for Bishop, King, and Queen)
def get_bishop_moves(chess_board, my_pieces, enemy_pieces, king, row, col):

    # Diagonal direction lists
    n_e = []
    n_w = []
    s_e = []
    s_w = []

    # Keeps track of valid movement tiles and diagonals
    valid_tiles = []
    diagonal = []

    # Determines diagonal movement based on if the piece being moved is or isn't a King
    if (king):
        row_edge_up = row + 2
        row_edge_down = row - 2
        col_edge_right = col + 2
        col_edge_left = col - 2
    else:
        row_edge_up = 8
        row_edge_down = -1
        col_edge_right = 8
        col_edge_left = -1
    
    # Generating diagonal movement
    if (row + 1 < 8):

        if (col + 1 < 8):
            n_e = [zip(range(row + 1, row_edge_up), range(col + 1, col_edge_right))]
        if (col - 1 > -1):
            n_w = [zip(range(row + 1, row_edge_up), range(col - 1, col_edge_left, -1))]    
    if (row - 1 > -1):
        if (col + 1 < 8):
            s_e = [zip(range(row - 1, row_edge_down, - 1), range(col + 1, col_edge_right))]
        if (col - 1 > -1):
            s_w = [zip(range(row - 1, row_edge_down, - 1), range(col - 1, col_edge_left, -1))]
    
    # Assigns diagonal directions
    diagonal = n_e + n_w + s_w + s_e

    for direction in diagonal:
        for pair in direction:
            # Stop if it runs into own piece
            if (chess_board[pair[0]][pair[1]] in my_pieces):
                break

            valid_tiles.append(coords_to_uci(row, col) + coords_to_uci(pair[0], pair[1]))

            # Stop if it runs into enemy piece
            if (chess_board[pair[0]][pair[1]] in enemy_pieces):
                break
    return valid_tiles

# Gets cardinal directions (Used for Rook, King, Queen, and Pawn)
def get_rook_moves(chess_board, my_pieces, enemy_pieces, king, row, col):
    
    # Determines cardinal movement based on if the piece being moved is or isn't a King
    if (king):
        row_edge_up = row + 2
        row_edge_down = row - 2
        col_edge_left = col -2
        col_edge_right = col + 2
    else:
        row_edge_up = 8
        row_edge_down = -1
        col_edge_left = -1
        col_edge_right = 8

    # Cardinal directions lists
    valid_tiles = []
    right_move = []
    left_move = []
    up_move = []
    down_move = []

    # Checks all spaces in a straight line each cardinal direction of the King
    for i in range(col + 1, 8):
        right_move.append(row)

    for i in range(col - 1, -1, -1):
        left_move.append(row)

    for i in range(row + 1, 8):
        up_move.append(col)

    for i in range(row - 1, -1, -1):
        down_move.append(col)

    directions = [  
                    zip(right_move, range(col + 1, col_edge_right)),
                    zip(left_move, range(col -1, col_edge_left, -1)),
                    zip(range(row + 1, row_edge_up), up_move),
                    zip(range(row - 1, row_edge_down, -1), down_move)
                ]

    for direction in directions:
        for pair in direction:
            # Stop if it runs into own piece 
            if (chess_board[pair[0]][pair[1]] in my_pieces):
                break

            valid_tiles.append(coords_to_uci(row, col) + coords_to_uci(pair[0], pair[1]))

            # Stop if it runs into enemy piece
            if (chess_board[pair[0]][pair[1]] in enemy_pieces):
                break

    return valid_tiles

# Gets all moves the Queen(s) can make
def get_queen_moves(chess_board, my_pieces, enemy_pieces, row, col):

    # Checks every direction the Queen(s) could theoretically move
    cardinal_moves = get_rook_moves(chess_board, my_pieces, enemy_pieces, False, row, col)
    diagonal_moves = get_bishop_moves(chess_board, my_pieces, enemy_pieces, False, row, col)
    valid_moves = cardinal_moves + diagonal_moves
    return valid_moves

# Get all moves the King can make
def get_king_moves(chess_board, my_pieces, enemy_pieces, row, col):

    # Checks every direction the King could theoretically move
    diagonal = get_bishop_moves(chess_board, my_pieces, enemy_pieces, True, row, col)
    cardinal = get_rook_moves(chess_board, my_pieces, enemy_pieces, True, row, col)
    prelim_moves = diagonal + cardinal

    return prelim_moves

# Checks if the King is in check from an enemy Knight
def check_knight(chess_board, enemy_pieces, king_row, king_col):

    # Checks all possible directions a Knight could attack from
    directions = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2)]
    for (x, y) in directions:
        x_new = king_row + x
        y_new = king_col + y
        if (-1 < x_new < 8 and -1 < y_new < 8):
            if (chess_board[x_new][y_new] == enemy_pieces[2]):
                return True
    return False

# Checks if the King is in check from a cardinal direction
def check_cardinal(chess_board, my_pieces, enemy_pieces, row, col):
    right_move = []
    left_move = []
    up_move = []
    down_move = []

    # Checks all spaces in a straight line each cardinal direction of the King
    for i in range(col + 1, 8):
        right_move.append(row)

    for i in range(col - 1, -1, -1):
        left_move.append(row)

    for i in range(row + 1, 8):
        up_move.append(col)

    for i in range(row - 1, -1, -1):
        down_move.append(col)

    directions = [  
                    zip(right_move, range(col + 1, 8)),
                    zip(left_move, range(col -1, -1, -1)),
                    zip(range(row + 1, 8), up_move),
                    zip(range(row - 1, -1, -1), down_move)
                ]

    for direction in directions:
        for pair in direction:
            # Stop if King runs into own piece in front of it
            if (chess_board[pair[0]][pair[1]] in my_pieces):
                break

            # Stop if King runs into an enemy piece in front of it
            if (chess_board[pair[0]][pair[1]] in enemy_pieces):
                if (chess_board[pair[0]][pair[1]] == enemy_pieces[1] or chess_board[pair[0]][pair[1]] == enemy_pieces[4]):
                    return True
                break

    return False

# Checks if the King is in check from a diagonal direction
def check_diagonal(chess_board, my_pieces, enemy_pieces, row, col):
    king_directions = [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)]
    if my_pieces[0].islower():
        side = -1
    else:
        side = 1
    
    # Determines the attacking directions of the Pawns of the enemy
    pawn_directions = [(1 * side,-1),(1 * side,1)]
    directions = [
                    zip(range(row + 1, 8), range(col + 1, 8)),
                    zip(range(row + 1, 8), range(col - 1, -1, -1)),
                    zip(range(row - 1, -1, -1), range(col + 1, 8)),
                    zip(range(row - 1, -1, -1), range(col - 1, -1, -1)),
                ]

    # Accounts for Pawn diagonals
    for (x, y) in pawn_directions:
        new_row = row + x
        new_col = col + y
        if (-1 < new_row < 8 and -1 < new_col < 8):
            if (chess_board[new_row][new_col] == enemy_pieces[0]):
                return True

    # Accounts for if there is an enemy King
    for (x, y) in king_directions:
        new_row = row + x
        new_col = col + y
        if (-1 < new_row < 8 and -1 < new_col < 8):
            if (chess_board[new_row][new_col] == enemy_pieces[5]):
                return True
    

    for direction in directions:
        for pair in direction:
            # Stop if King runs into own piece in front of it
            if (chess_board[pair[0]][pair[1]] in my_pieces):
                break

            # Stop if King runs into enemy piece in front of it
            if (chess_board[pair[0]][pair[1]] in enemy_pieces):
                if (chess_board[pair[0]][pair[1]] == enemy_pieces[3] or chess_board[pair[0]][pair[1]] == enemy_pieces[4]):
                    return True
                break

    return False

# Check to see if the King is currently in check
def king_check(chess_board, my_pieces, enemy_pieces, row, col):

    # Views all directions and then returns true if the King is in check, false if it isn't
    knight_positions = check_knight(chess_board, enemy_pieces, row, col)
    cardinal_sight = check_cardinal(chess_board, my_pieces, enemy_pieces, row, col)
    diagonal_sight = check_diagonal(chess_board, my_pieces, enemy_pieces, row, col)

    if (knight_positions or cardinal_sight or diagonal_sight):
        return True
    else:
        return False

# Find valid actions
# To do: Make En Passant and Castling actions
def actions(color, chess_board):
    valid_moves = []
    king_row = -1
    king_col = -1

    # Assigns a set of pieces with the color of the player
    if (color == "white"):
        my_pieces = WHITE_CHESS_PIECES
        enemy_pieces = BLACK_CHESS_PIECES
    else:
        my_pieces = BLACK_CHESS_PIECES
        enemy_pieces = WHITE_CHESS_PIECES

    for i in range(8):
        for j in range(8):
            # Get all moves for Pawns
            if (chess_board[i][j] == my_pieces[0]):
                valid_pawn = []
                valid_pawn = get_pawn_moves(chess_board, my_pieces, enemy_pieces, i, j)
                if (len(valid_pawn) > 0):
                    valid_moves.append(valid_pawn)

            # Get all moves for Knights
            if (chess_board[i][j] == my_pieces[2]):
                valid_knight = []
                valid_knight = get_knight_moves(chess_board, enemy_pieces, i, j)
                if (len(valid_knight) > 0):
                    valid_moves.append(valid_knight)

            # Get all moves for Bishops
            if (chess_board[i][j] == my_pieces[3]):
                valid_bishop = []
                valid_bishop = get_bishop_moves(chess_board, my_pieces, enemy_pieces, False ,i, j)
                if (len(valid_bishop) > 0):
                    valid_moves.append(valid_bishop)

            # Get all moves for Rooks
            if (chess_board[i][j] == my_pieces[1]):
                valid_rook = []
                valid_rook = get_rook_moves(chess_board, my_pieces, enemy_pieces, False, i, j)
                if (len(valid_rook) > 0):
                    valid_moves.append(valid_rook)

            # Get all moves for Queen
            if (chess_board[i][j] == my_pieces[4]):
                valid_queen = []
                valid_queen = get_queen_moves(chess_board, my_pieces, enemy_pieces, i, j)
                if (len(valid_queen) > 0):
                    valid_moves.append(valid_queen)
     
            # Get all moves for King  
            if (chess_board[i][j] == my_pieces[5]):
                king_row = i
                king_col = j
                valid_king = []
                valid_king = get_king_moves(chess_board, my_pieces, enemy_pieces, i, j)
                if (len(valid_king) > 0):
                    valid_moves.append(valid_king)

    # Compiles a list of all "possible" moves, not necessarily all valid
    moves_list = [j for val in valid_moves for j in val]
    valid_moves = []

    # Test valid moves to see if King is placed in check
    in_check = king_check(chess_board, my_pieces, enemy_pieces, king_row, king_col)
    for move in moves_list:
        if check_valid(chess_board, move, my_pieces, enemy_pieces, king_row, king_col):
            valid_moves.append(move)

    return valid_moves

# Check move for validity, return true of os valid, false if it puts king in check or is outright invalid
def check_valid(chess_board, move, my_pieces, enemy_pieces, king_row, king_col):
    new_board  = [[j for j in chess_board[i]] for i in range(len(chess_board))] 
    move_coords = uci_to_coords(move)

    # Gets the coords for the tile a piece would be moving from
    last_tile = (move_coords[0], move_coords[1])
    piece_moving = new_board[last_tile[0]][last_tile[1]]

    new_board[last_tile[0]][last_tile[1]] = "."

    # Gets the coords for the tile a piece would be moving to
    new_tile = (move_coords[2], move_coords[3])
    new_board[new_tile[0]][new_tile[1]] = piece_moving

    # Conditional to prevent King from moving into check
    if (piece_moving == my_pieces[5]):
        is_in_check = king_check(new_board, my_pieces, enemy_pieces, new_tile[0], new_tile[1])
    else:
        is_in_check = king_check(new_board, my_pieces, enemy_pieces, king_row, king_col)

    # Returns true if the move is valid and false if it isn't
    if is_in_check:
        return False
    else:
        return True

# Print function to show chess board for visualization
# Purely used for testing without the visualizer
def print_chess(chess_board):
    count = 9
    for i in range(len(chess_board) - 1, -1, -1):
        count -= 1
        print(count, chess_board[i])
    print(" ", CHESS_RANK)