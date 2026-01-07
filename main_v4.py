# chess_game_fantasy.py
import pygame
import sys

# --- Game constants ---
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 10, 10
SQUARE_SIZE = WIDTH // COLS

# Colors
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
MOVE_HIGHLIGHT = (0, 255, 0, 100)
CAPTURE_HIGHLIGHT = (255, 0, 0, 100)
BEUROCRATE_HIGHLIGHT = (0, 0, 255, 100)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("10x10 Fantasy Chess")
font = pygame.font.SysFont("arial", 24)

# Piece kind mapping (single-letter codes used internally)
# Existing: K Q R B N P C
# New: J = Jester, S = Squire, L = Paladin, V = Prince, W = Princess
NEW_KINDS = ['J', 'S', 'L', 'V', 'W']

# --- Piece Class ---
class Piece:
    def __init__(self, color, kind):
        self.color = color  # 'w' or 'b'
        self.kind = kind    # single char
        self.image = None

    def __repr__(self):
        return f"{self.color}{self.kind}"

# --- Board Class ---
class Board:
    def __init__(self):
        self.pieces = {}
        # track moved for castling (original kings & rooks)
        self.has_moved = {'wK': False, 'bK': False,
                          'wR_left': False, 'wR_right': False,
                          'bR_left': False, 'bR_right': False}
        self.last_pawn_double_move = None  # for en passant as (row,col)
        self.game_over = False
        self.winner = None
        # track last moved piece kind (for Jester). Updated by Game when moves happen.
        self.last_moved_kind = None
        self.piece_images = {}
        self.flipped = False  # Track if board is flipped
        self.load_images()
        self.init_board()

    def load_images(self):
        # expected filenames: assets/pieces/<color><kind>.png, e.g. wK.png, bJ.png
        kinds = ['K','Q','R','B','N','P','C','J','S','L','V','W']
        colors = ['w','b']
        for color in colors:
            for kind in kinds:
                key = color + kind
                try:
                    img = pygame.image.load(f"assets/pieces/{key}.png").convert_alpha()
                    # Use smoothscale for better quality when resizing
                    img = pygame.transform.smoothscale(img, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
                    self.piece_images[key] = img
                except Exception:
                    self.piece_images[key] = None  # fallback to letter rendering

    def init_board(self):
        self.pieces.clear()
        self.last_pawn_double_move = None
        self.game_over = False
        self.winner = None
        self.last_moved_kind = None
        # Final decided back-rank layout (left to right columns 0..9):
        # R N B J K Q C B N R
        def back_rank(color, row):
            prefix = 'w' if color == 'white' else 'b'
            layout = ['R','N','B','J','K','Q','C','B','N','R']  # Jester at col3, Bureaucrat at col6
            for col, k in enumerate(layout):
                self.pieces[(row, col)] = Piece(prefix, k)

        back_rank('black', 0)
        # row 1 black pawns -> replace specific pawn types as described
        for col in range(COLS):
            # front row mapping for black at row=1 (mirrors white)
            # Squire in front of knights (cols 1 and 8)
            # Paladin in front of bishops (cols 2 and 7? but bishop cols are 2 and 7 here)
            # Prince in front of king (king at col4)
            # Princess in front of queen (queen at col5)
            # Squire -> 'S', Paladin -> 'L', Prince -> 'V', Princess -> 'W'
            if col in (1, 8):
                self.pieces[(1, col)] = Piece('b', 'S')  # Squire
            elif col in (2, 7):
                self.pieces[(1, col)] = Piece('b', 'L')  # Paladin
            elif col == 4:
                self.pieces[(1, col)] = Piece('b', 'V')  # Prince
            elif col == 5:
                self.pieces[(1, col)] = Piece('b', 'W')  # Princess
            else:
                self.pieces[(1, col)] = Piece('b', 'P')

        back_rank('white', 9)
        # row 8 white pawns: mirror (white pawns at row 8)
        for col in range(COLS):
            if col in (1, 8):
                self.pieces[(8, col)] = Piece('w', 'S')  # Squire
            elif col in (2, 7):
                self.pieces[(8, col)] = Piece('w', 'L')  # Paladin
            elif col == 4:
                self.pieces[(8, col)] = Piece('w', 'V')  # Prince
            elif col == 5:
                self.pieces[(8, col)] = Piece('w', 'W')  # Princess
            else:
                self.pieces[(8, col)] = Piece('w', 'P')

    # --- Drawing ---
    def draw_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                color = LIGHT if (r + c) % 2 == 0 else DARK
                # Calculate display position based on flip
                if self.flipped:
                    display_r = ROWS - 1 - r
                    display_c = COLS - 1 - c
                else:
                    display_r = r
                    display_c = c
                pygame.draw.rect(screen, color, (display_c * SQUARE_SIZE, display_r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for (r, c), piece in self.pieces.items():
            key = piece.color + piece.kind
            img = self.piece_images.get(key)
            # Calculate display position based on flip
            if self.flipped:
                display_r = ROWS - 1 - r
                display_c = COLS - 1 - c
            else:
                display_r = r
                display_c = c
            
            if img:
                screen.blit(img, (display_c * SQUARE_SIZE + 5, display_r * SQUARE_SIZE + 5))
            else:
                # fallback: draw letter tile
                surf = pygame.Surface((SQUARE_SIZE - 10, SQUARE_SIZE - 10))
                surf.fill((220,220,220))
                small = pygame.font.SysFont("arial", 20)
                text = small.render(piece.kind, True, (0,0,0))
                surf.blit(text, (5,5))
                screen.blit(surf, (display_c * SQUARE_SIZE + 5, display_r * SQUARE_SIZE + 5))

    def draw(self):
        self.draw_board()
        self.draw_pieces()

    def draw_highlights(self, selected, valid_moves):
        piece_kind = self.pieces[selected].kind
        for move in valid_moves:
            r, c = move
            # Calculate display position based on flip
            if self.flipped:
                display_r = ROWS - 1 - r
                display_c = COLS - 1 - c
            else:
                display_r = r
                display_c = c
            
            overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            if piece_kind == 'C':
                overlay.fill(BEUROCRATE_HIGHLIGHT)
            elif move in self.pieces and self.pieces[move].color != self.pieces[selected].color:
                overlay.fill(CAPTURE_HIGHLIGHT)
            else:
                overlay.fill(MOVE_HIGHLIGHT)
            screen.blit(overlay, (display_c * SQUARE_SIZE, display_r * SQUARE_SIZE))

    def get_square_under_mouse(self):
        x, y = pygame.mouse.get_pos()
        c = x // SQUARE_SIZE
        r = y // SQUARE_SIZE
        # Convert display position to logical position based on flip
        if self.flipped:
            r = ROWS - 1 - r
            c = COLS - 1 - c
        return r, c

    # --- Game Logic helpers ---
    def is_in_check(self, color):
        # find king position (king could be original K or if replaced, check piece with kind 'K' only)
        king_pos = next((pos for pos, p in self.pieces.items() if p.color == color and p.kind == 'K'), None)
        if not king_pos:
            # No king found - this means game should be over or prince hasn't transformed yet
            return True
        
        # Check if BOTH King and Prince exist - only then can King be captured without check mattering
        # If Prince was killed first, normal check rules apply
        has_prince = any(p for p in self.pieces.values() if p.color == color and p.kind == 'V')
        has_king = True  # We already found king above
        
        # Only ignore check if BOTH King and Prince are alive
        if has_prince and has_king:
            return False
        
        # Normal check detection - any enemy move that can reach king
        for pos, p in list(self.pieces.items()):
            if p.color != color:
                enemy_moves = self.valid_moves(p, pos, ignore_check=True)
                if king_pos in enemy_moves:
                    return True
        return False

    def has_legal_moves(self, color):
        # iterate over a snapshot list to avoid dict mutation during simulation
        for pos, p in list(self.pieces.items()):
            if p.color != color:
                continue
            moves = self.valid_moves(p, pos)
            for m in moves:
                saved = self.pieces.get(m)
                # simulate
                self.pieces[m] = p
                del self.pieces[pos]
                in_check = self.is_in_check(color)
                # undo
                self.pieces[pos] = p
                if saved:
                    self.pieces[m] = saved
                else:
                    self.pieces.pop(m, None)
                if not in_check:
                    return True
        return False

    # Helper: generate moves for a given kind without recursion risk (used by Jester)
    def moves_for_kind(self, kind, color, start, ignore_check=True):
        fake = Piece(color, kind)
        return self.valid_moves(fake, start, ignore_check=ignore_check)

    # --- Movement rules ---
    def valid_moves(self, piece, start, ignore_check=False):
        """
        Return list of destination tuples. If ignore_check==False, filter out moves that leave own king in check.
        """
        r, c = start
        color, kind = piece.color, piece.kind
        moves = []
        inside = lambda x, y: 0 <= x < ROWS and 0 <= y < COLS

        # Pawn (normal): forward 1 (or 2 from start), captures diag, en passant tracked via last_pawn_double_move
        if kind == 'P':
            direction = -1 if color == 'w' else 1
            start_row = 8 if color == 'w' else 1
            nr = r + direction
            # forward 1
            if inside(nr, c) and (nr, c) not in self.pieces:
                moves.append((nr, c))
                # forward 2 from start
                two_r = r + 2*direction
                if r == start_row and inside(two_r, c) and (two_r, c) not in self.pieces:
                    moves.append((two_r, c))
            # captures (and en passant)
            for dc in (-1, 1):
                nc = c + dc
                if inside(nr, nc):
                    if (nr, nc) in self.pieces and self.pieces[(nr, nc)].color != color:
                        moves.append((nr, nc))
                    # en passant: if pawn that moved two squares is adjacent on same row
                    if self.last_pawn_double_move:
                        lr, lc = self.last_pawn_double_move
                        # last double move landed at lr,lc; en passant capture landing square is (nr,nc)
                        # condition: lr == r and lc == nc (opponent pawn moved to adjacent column)
                        if lr == r and lc == nc:
                            # landing square is nr,nc
                            moves.append((nr, nc))

        # Rook
        elif kind == 'R':
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc
                while inside(nr, nc):
                    if (nr, nc) in self.pieces:
                        if self.pieces[(nr, nc)].color != color:
                            moves.append((nr, nc))
                        break
                    moves.append((nr, nc))
                    nr += dr; nc += dc

        # Bishop
        elif kind == 'B':
            for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                nr, nc = r + dr, c + dc
                while inside(nr, nc):
                    if (nr, nc) in self.pieces:
                        if self.pieces[(nr, nc)].color != color:
                            moves.append((nr, nc))
                        break
                    moves.append((nr, nc))
                    nr += dr; nc += dc

        # Knight
        elif kind == 'N':
            for dr, dc in [(-2,-1),(-2,1),(2,-1),(2,1),(-1,-2),(-1,2),(1,-2),(1,2)]:
                nr, nc = r + dr, c + dc
                if inside(nr, nc) and ((nr, nc) not in self.pieces or self.pieces[(nr, nc)].color != color):
                    moves.append((nr, nc))

        # Queen
        elif kind == 'Q':
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                nr, nc = r + dr, c + dc
                while inside(nr, nc):
                    if (nr, nc) in self.pieces:
                        if self.pieces[(nr, nc)].color != color:
                            moves.append((nr, nc))
                        break
                    moves.append((nr, nc))
                    nr += dr; nc += dc

        # Bureaucrat (C): can move to ANY empty square of same color parity; cannot capture
        elif kind == 'C':
            start_color = (r + c) % 2
            for row in range(ROWS):
                for col in range(COLS):
                    if (row + col) % 2 == start_color and (row, col) not in self.pieces:
                        moves.append((row, col))

        # Jester (J): moves like the opponent's last moved piece kind (if available).
        # It can capture normally. If there's no last kind, it moves like a king as fallback.
        elif kind == 'J':
            last_kind = self.last_moved_kind
            if last_kind:
                # Use moves_for_kind but avoid infinite recursion: pass ignore_check=True to not re-filter
                # Create a fake piece of that kind with jester's color, but call a helper that won't call J->J recursively:
                # We call moves_for_kind which internally calls valid_moves(fake,...) - could loop if last_kind == 'J'
                # To avoid cycles: if last_kind == 'J', fallback to King moves
                if last_kind == 'J':
                    last_kind = 'K'
                # generate moves as if a piece of kind last_kind were at Jester's position
                temp_moves = []
                # implement movement for last_kind without invoking J again by calling valid_moves with ignore_check=True
                temp_piece = Piece(piece.color, last_kind)
                temp_moves = self.valid_moves(temp_piece, start, ignore_check=True)
                # only include moves that either capture enemy or land on empty
                for mv in temp_moves:
                    if mv not in self.pieces or self.pieces[mv].color != piece.color:
                        moves.append(mv)
            else:
                # fallback: king-like moves
                for dr in (-1,0,1):
                    for dc in (-1,0,1):
                        if dr==0 and dc==0: continue
                        nr,nc = r+dr, c+dc
                        if 0<=nr<ROWS and 0<=nc<COLS and ((nr,nc) not in self.pieces or self.pieces[(nr,nc)].color!=piece.color):
                            moves.append((nr,nc))

        # Squire (S): moves 2 squares orthogonally (up/down/left/right), *jumps* over the intermediate square (like a knight)
        elif kind == 'S':
            for dr, dc in [(-2,0),(2,0),(0,-2),(0,2)]:
                nr, nc = r+dr, c+dc
                if inside(nr,nc) and ((nr,nc) not in self.pieces or self.pieces[(nr,nc)].color != color):
                    moves.append((nr,nc))

        # Paladin (L): moves 2 squares diagonally, jumps over the intermediate square
        elif kind == 'L':
            for dr,dc in [(-2,-2),(-2,2),(2,-2),(2,2)]:
                nr,nc = r+dr, c+dc
                if inside(nr,nc) and ((nr,nc) not in self.pieces or self.pieces[(nr,nc)].color != color):
                    moves.append((nr,nc))

        # Prince (V): can move up to 2 squares in any direction (no jumping) and capture
        # Moves like a king but with range 2 - only orthogonal and diagonal directions
        elif kind == 'V':
            # Eight directions: orthogonal and diagonal
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                # Try 1 square and 2 squares in each direction
                for distance in (1, 2):
                    nr, nc = r + dr*distance, c + dc*distance
                    if not inside(nr, nc):
                        break  # Can't go further in this direction
                    # Check if path is blocked (for distance 2, check intermediate square)
                    if distance == 2:
                        mid_r, mid_c = r + dr, c + dc
                        if (mid_r, mid_c) in self.pieces:
                            break  # Path blocked, can't move 2 squares
                    # Check destination
                    if (nr, nc) in self.pieces:
                        if self.pieces[(nr, nc)].color != color:
                            moves.append((nr, nc))  # Can capture
                        break  # Can't go further
                    else:
                        moves.append((nr, nc))  # Empty square

        # Princess (W): can move up to 3 squares in any direction (queen-like but capped to 3), path must be clear
        elif kind == 'W':
            for dr,dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                for step in (1,2,3):
                    nr, nc = r + dr*step, c + dc*step
                    if not inside(nr,nc): break
                    if (nr,nc) in self.pieces:
                        if self.pieces[(nr,nc)].color != color:
                            moves.append((nr,nc))
                        break
                    moves.append((nr,nc))

        # King (K)
        elif kind == 'K':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==0 and dc==0: continue
                    nr, nc = r+dr, c+dc
                    if inside(nr,nc) and ((nr,nc) not in self.pieces or self.pieces[(nr,nc)].color != color):
                        moves.append((nr,nc))
            # castling (special 10x10 positions); only if original king still exists and hasn't moved
            row = 9 if color == 'w' else 0
            left_between = [(row,i) for i in range(1,4)]
            right_between = [(row,i) for i in range(5,9)]
            if color == 'w':
                if not self.has_moved['wK'] and not self.has_moved['wR_left'] and all(pos not in self.pieces for pos in left_between):
                    moves.append((row,1))
                if not self.has_moved['wK'] and not self.has_moved['wR_right'] and all(pos not in self.pieces for pos in right_between):
                    moves.append((row,7))
            else:
                if not self.has_moved['bK'] and not self.has_moved['bR_left'] and all(pos not in self.pieces for pos in left_between):
                    moves.append((row,1))
                if not self.has_moved['bK'] and not self.has_moved['bR_right'] and all(pos not in self.pieces for pos in right_between):
                    moves.append((row,7))

        # --- Filter moves that would leave king in check (unless ignore_check True) ---
        if not ignore_check:
            safe_moves = []
            # take snapshot to restore after simulating each move
            pieces_snapshot = self.pieces.copy()
            for m in moves:
                # simulate move
                taken = self.pieces.get(m)
                self.pieces[m] = piece
                # special case: if capturing en passant, remove the captured pawn behind the landing square
                removed_en_passant = None
                if piece.kind == 'P' and self.last_pawn_double_move:
                    lr, lc = self.last_pawn_double_move
                    # an en passant capture lands on nr,nc == m and removes pawn at (r, nc)
                    # detect and remove if appropriate
                    if (m[0] == lr + (-1 if piece.color == 'w' else 1)) and (m[1] == lc) and (r == lr):
                        # the captured pawn sits at lr,lc; ensure we only remove opponent pawn at that square
                        if (lr, lc) in self.pieces and self.pieces[(lr, lc)].color != piece.color:
                            removed_en_passant = (lr, lc)
                            del self.pieces[(lr, lc)]
                # remove source
                if start in self.pieces:
                    del self.pieces[start]
                # check
                in_check = self.is_in_check(color)
                # restore from snapshot
                self.pieces = pieces_snapshot.copy()
                if not in_check:
                    safe_moves.append(m)
            return safe_moves

        return moves

    # Utility to promote a piece object (change its kind)
    def promote_piece_at(self, pos, new_kind):
        if pos in self.pieces:
            p = self.pieces[pos]
            p.kind = new_kind

# --- Game Class ---
class Game:
    def __init__(self):
        self.board = Board()
        self.selected = None
        self.valid_moves = []
        self.turn = 'w'
        # Track last moved kind per player globally for Jester usage: board.last_moved_kind records last move regardless of side
        # We'll set board.last_moved_kind = moved_piece.kind after each successful move in handle_move
        self.running = True

    def choose_promotion(self, color):
        """Let player choose promotion piece: Q, R, B, N, C, J, S, L, V, W"""
        options = ['Q','R','B','N','C','J','S','L','V','W']
        images = []
        for kind in options:
            key = color + kind
            img = self.board.piece_images.get(key)
            if img:
                images.append(img)
            else:
                surf = pygame.Surface((SQUARE_SIZE - 10, SQUARE_SIZE - 10))
                surf.fill((200,200,200))
                big = pygame.font.SysFont("arial", 28)
                t = big.render(kind, True, (0,0,0))
                surf.blit(t, (8,8))
                images.append(surf)

        running = True
        selected_kind = None
        while running:
            self.board.draw()
            # draw the promotion options centered
            label = font.render("Choose promotion:", True, (255,255,255))
            screen.blit(label, (WIDTH//2 - 150, HEIGHT//4))
            for i, img in enumerate(images):
                rect = pygame.Rect(WIDTH//2 - 240 + i*90, HEIGHT//2 - 40, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(screen, (100,100,100), rect, 2)
                screen.blit(img, (rect.x+5, rect.y+5))
            pygame.display.flip()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    for i, kind in enumerate(options):
                        rect = pygame.Rect(WIDTH//2 - 240 + i*90, HEIGHT//2 - 40, SQUARE_SIZE, SQUARE_SIZE)
                        if rect.collidepoint(mx,my):
                            selected_kind = kind
                            running = False
                            break
        return selected_kind

    def handle_castling(self, piece, start, end):
        row = 9 if piece.color == 'w' else 0
        if end == (row,1):
            # queenside castling: king -> col=1, rook from col=0 -> col=2
            rook = self.board.pieces.pop((row,0), None)
            if rook:
                self.board.pieces[(row,2)] = rook
            if piece.color == 'w':
                self.board.has_moved['wR_left'] = True
            else:
                self.board.has_moved['bR_left'] = True
        elif end == (row,7):
            # kingside castling: king -> col=7, rook from col=9 -> col=6
            rook = self.board.pieces.pop((row,9), None)
            if rook:
                self.board.pieces[(row,6)] = rook
            if piece.color == 'w':
                self.board.has_moved['wR_right'] = True
            else:
                self.board.has_moved['bR_right'] = True

    def update_rook_movement(self, piece, start):
        if piece.color == 'w':
            if start == (9,0): self.board.has_moved['wR_left'] = True
            elif start == (9,9): self.board.has_moved['wR_right'] = True
        else:
            if start == (0,0): self.board.has_moved['bR_left'] = True
            elif start == (0,9): self.board.has_moved['bR_right'] = True

    def handle_move(self, start, dest):
        """
        Perform move; assumes dest is valid among valid_moves.
        Handles castling, en passant, promotions, prince->king substitution after king capture.
        """
        piece = self.board.pieces.pop(start)
        color = piece.color
        captured = None

        # Castling (if moving King)
        if piece.kind == 'K':
            if color == 'w':
                self.board.has_moved['wK'] = True
            else:
                self.board.has_moved['bK'] = True
            # handle rook reposition inside Board
            self.handle_castling(piece, start, dest)

        # track rook move
        if piece.kind == 'R':
            self.update_rook_movement(piece, start)

        # En passant capture removal
        if piece.kind == 'P':
            # detect en passant capture pattern
            if self.board.last_pawn_double_move:
                lr, lc = self.board.last_pawn_double_move
                # if capturing en passant, destination should be (lr + direction, lc)
                # direction relative to capturing pawn:
                dir_move = -1 if piece.color == 'w' else 1
                expected_capture_from = (lr, lc)
                # en passant capture occurs when destination column equals lc and destination row equals lr + dir_move
                if dest[1] == lc and dest[0] == lr + dir_move and start[0] == lr:
                    # remove the captured pawn at lr,lc
                    if (lr, lc) in self.board.pieces and self.board.pieces[(lr,lc)].color != piece.color:
                        del self.board.pieces[(lr,lc)]
                        captured = (lr,lc)

        # Normal capture
        if dest in self.board.pieces:
            captured = dest
            captured_piece = self.board.pieces[dest]
            # if capturing a king, we may need to transform the prince/princess if exists
            if captured_piece.kind == 'K':
                # remove captured king by assigning captured variable; replacement will be handled after placing our piece
                pass
            # remove captured piece (we'll overwrite below)
            del self.board.pieces[dest]

        # Place moving piece
        self.board.pieces[dest] = piece

        # Pawn double-move tracking for en passant
        if piece.kind == 'P' and abs(dest[0] - start[0]) == 2:
            self.board.last_pawn_double_move = dest
        else:
            self.board.last_pawn_double_move = None

        # Pawn promotion
        if piece.kind == 'P' and (dest[0] == 0 or dest[0] == 9):
            # ask player to choose
            new_kind = self.choose_promotion(piece.color)
            if new_kind:
                piece.kind = new_kind

        # Squire promotion: if reaches back row, becomes Knight
        if piece.kind == 'S' and (dest[0] == 0 or dest[0] == 9):
            piece.kind = 'N'

        # Paladin promotion: if reaches back row, becomes Bishop
        if piece.kind == 'L' and (dest[0] == 0 or dest[0] == 9):
            piece.kind = 'B'

        # If we captured opponent's King: check for Prince -> King substitution
        # Captured info might be the dest square earlier or removed by en passant logic; check if a King of opposite color exists still.
        # Actually we removed captured king above (if dest had king, it was deleted). Now see if the owner (opponent) has a Prince.
        opponent = 'b' if color == 'w' else 'w'
        # if opponent has no King but has a Prince -> transform Prince->King and Princess->Queen
        opp_has_king = any(p for p in self.board.pieces.values() if p.color == opponent and p.kind == 'K')
        opp_has_prince_pos = next((pos for pos,p in self.board.pieces.items() if p.color == opponent and p.kind == 'V'), None)
        opp_has_princess_pos = next((pos for pos,p in self.board.pieces.items() if p.color == opponent and p.kind == 'W'), None)
        if not opp_has_king and opp_has_prince_pos:
            # Prince becomes King (no castling allowed)
            prince_pos = opp_has_prince_pos
            self.board.pieces[prince_pos].kind = 'K'
            # Princess becomes Queen (if present)
            if opp_has_princess_pos:
                self.board.pieces[opp_has_princess_pos].kind = 'Q'
            # disable castling for that side
            if opponent == 'w':
                self.board.has_moved['wK'] = True
                self.board.has_moved['wR_left'] = True
                self.board.has_moved['wR_right'] = True
            else:
                self.board.has_moved['bK'] = True
                self.board.has_moved['bR_left'] = True
                self.board.has_moved['bR_right'] = True

        # Update board.last_moved_kind for Jester
        self.board.last_moved_kind = piece.kind

    def handle_click(self):
        pos = self.board.get_square_under_mouse()
        # if a piece currently selected
        if self.selected:
            if pos in self.valid_moves:
                # perform move
                start = self.selected
                self.handle_move(start, pos)
                # Flip board after move
                self.board.flipped = not self.board.flipped
                # switch turn
                self.turn = 'b' if self.turn == 'w' else 'w'
            # reset selection in any case
            self.selected = None
            self.valid_moves = []
        # selecting a piece
        elif pos in self.board.pieces and self.board.pieces[pos].color == self.turn:
            self.selected = pos
            self.valid_moves = self.board.valid_moves(self.board.pieces[pos], pos)

    def run(self):
        clock = pygame.time.Clock()
        while True:
            screen.fill((0,0,0))
            self.board.draw()
            if self.selected:
                self.board.draw_highlights(self.selected, self.valid_moves)
            if self.board.game_over:
                text = font.render(f"Game Over! {self.board.winner}", True, (255,0,0))
                screen.blit(text, (WIDTH//2 - 150, HEIGHT//2))
            pygame.display.flip()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and not self.board.game_over:
                    self.handle_click()

            # Game over detection
            if not self.board.game_over:
                if self.board.is_in_check(self.turn) and not self.board.has_legal_moves(self.turn):
                    self.board.game_over = True
                    self.board.winner = ('Checkmate! White wins' if self.turn == 'b' else 'Checkmate! Black wins')
                elif not self.board.is_in_check(self.turn) and not self.board.has_legal_moves(self.turn):
                    self.board.game_over = True
                    self.board.winner = 'Stalemate! Draw'

            clock.tick(30)

# --- Run ---
if __name__ == "__main__":
    Game().run()