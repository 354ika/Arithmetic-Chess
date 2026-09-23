import arithmetic_chess as ArithChessLogic
from os import system
from tkinter import *
from tkinter import filedialog
try:
    from pygame import mixer
except:
    print("Required library pygame not found, installing pygame-ce")
    system("pip install pygame-ce")
    from pygame import mixer

class GameBoard:

    def __init__(self):
        self.board_tiles = []
        self.valid_moves = []
        self.board = []
        self.source_tile = None
        self.dest_tile = None
        self.current_turn = 1
        self.enable_move = False

    '''
    Creates the menu bar for the GUI
    Contains:
    - Load option - to load a configuration file
    - Save option - to save the current board state to a configuration file
    '''
    def create_menu_bar(self, root): 
        menu_bar = Menu(root) 
        file_menu = Menu(menu_bar, tearoff=0) 
        file_menu.add_command( label="Load", command=self.load_configuration_file ) 
        file_menu.add_command( label="Save", command=self.save_configuration_file ) 
        menu_bar.add_cascade( label="File", menu=file_menu ) 
        root.config(menu=menu_bar)

    def init_board(self, ic = ArithChessLogic.ic4[2]):
        reset_board_sfx.play()
        self.deselect_tiles
        self.destroy_tiles()
        self.board = ArithChessLogic.init_board(ArithChessLogic.WIDTH, ArithChessLogic.HEIGHT, ic)
        for x in range(ArithChessLogic.WIDTH):
            for y in range(ArithChessLogic.HEIGHT):
                new_tile = Tile(x, y)
                new_tile.format()
                self.board_tiles.append(new_tile)
        self.current_turn = 1    
        self.enable_move = True
        self.update_turn_label(False)        

    def load_configuration_file(self): 
        filename = filedialog.askopenfilename( 
            title="Load Configuration", 
            filetypes=[ 
                ("Configuration files", "*.txt"), 
                ("All files", "*.*") 
            ] 
        ) 
        if not filename: 
            return 
        try: 
            board = ArithChessLogic.load_configuration(filename) 
            game_board.board = board 
            # Recreate the tiles in case the loaded board has 
            # different dimensions 
            game_board.destroy_tiles() 
            for x in range(len(board)): 
                for y in range(len(board[0])): 
                    new_tile = Tile(x, y) 
                    new_tile.format() 
                    game_board.board_tiles.append(new_tile) 
            game_board.current_turn = 1 
            game_board.enable_move = True 
            game_board.deselect_tiles() 
            game_board.update_turn_label(False) 
        except Exception as e: 
            print(f"Error loading configuration: {e}")

    def save_configuration_file(self): 
        filename = filedialog.asksaveasfilename( 
            title="Save Configuration", 
            defaultextension=".txt", 
            filetypes=[ 
                ("Configuration files", "*.txt"), 
                ("All files", "*.*") 
            ] 
        ) 
        if not filename: 
            return 
        ArithChessLogic.save_configuration(filename, game_board.board)

    def load_board_state(self, board : list[list[int]], valid_moves : list[tuple[int, int]]):
        self.board = board
        self.valid_moves = valid_moves
        for tile in self.board_tiles:
            tile.format()
          
    def deselect_tiles(self):
        self.valid_moves = []
        self.source_tile = None
        self.dest_tile = None
        for t in self.board_tiles:
            t.selected = False
            t.format()
                
    def destroy_tiles(self):
        for tile in self.board_tiles:
            tile.destroy()     
        self.board_tiles = []    
     
    def try_move(self, start_tile, dest_tile):
        if not self.enable_move:
            self.deselect_tiles()
            return
        sx = start_tile.coords[X]
        sy = start_tile.coords[Y]
        tx = dest_tile.coords[X] 
        ty = dest_tile.coords[Y]
        #print(f"Trying: {sy}, {sx} -> {ty}, {tx}")
        move_status = ArithChessLogic.try_move(self.board, sy, sx, ty - sy, tx - sx, self.current_turn)
        if move_status.state == ArithChessLogic.SUCCESS:
            self.load_board_state(self.board, ())
            self.current_turn *= -1
            self.update_turn_label(game_over = False)
            piece_captured_sfx.play() if move_status == ArithChessLogic.PIECE_CAPTURED else piece_placed_sfx.play()
        elif move_status.state == ArithChessLogic.GAME_OVER:
            self.on_game_over()
        elif move_status.state == ArithChessLogic.FAILURE:
            update_label(move_error_label, move_error_text, move_status.message, palette.error)
            invalid_move_sfx.play()
        self.deselect_tiles()
        self.check_if_valid_moves_possible()
      
    def on_game_over(self):
        self.deselect_tiles()
        self.load_board_state(self.board, ())
        self.update_turn_label(game_over = True)
        game_over_sfx.play()
        self.enable_move = False
    
    def update_turn_label(self, game_over):
        if self.current_turn == 1:
            update_label(player_action_label, 
                        player_action_text, 
                        "Player 1 Wins" if game_over else "Your turn, Player 1", 
                        palette.player1)
        else:
            update_label(player_action_label, 
                        player_action_text, 
                        "Player 2 Wins" if game_over else "Your turn, Player 2", 
                        palette.player2)
        update_label(move_error_label, move_error_text, "", palette.error)
        
    def highlight_valid_moves(self, tile):
        try:
            value = abs(int(tile['text']))
        except:
            return
        moves = ArithChessLogic.all_valid_moves((ArithChessLogic.WIDTH, ArithChessLogic.HEIGHT), tile.coords, value)
        #print(f"Moves number: {len(moves)}")
        self.load_board_state(self.board, moves)
     
    def get_all_player_tiles(self):
        p_tiles = []
        for tile in self.board_tiles:
            if not check_int(tile['text']):
                continue
            value = int(tile['text'])
            if (self.current_turn <= -1 and value <= -1):
                p_tiles.append(tile)
                continue
            elif (self.current_turn >= 1 and value >= 1):
                p_tiles.append(tile)
                continue
        return p_tiles
       
    def check_if_valid_moves_possible(self):
        tile_values = self.get_all_player_tiles()
        valid_move_found = False
        for tile in tile_values:
            value = abs(int(tile['text']))
            moves = ArithChessLogic.all_valid_moves((ArithChessLogic.WIDTH, ArithChessLogic.HEIGHT), tile.coords, value)
            print(len(moves))
            if(len(moves) > 1):
                valid_move_found = True
                break
        if(not valid_move_found):
            self.current_turn = -self.current_turn
            self.on_game_over()
            
class Palette:
    def __init__(self, text, background, tile1, tile2, player1, player2, highlight, selected, error, panel_back, option_button):
            self.text = text
            self.background = background
            self.tile1 = tile1
            self.tile2 = tile2
            self.player1 = player1
            self.player2 = player2
            self.highlight = highlight
            self.selected = selected
            self.error = error
            self.panel_back = panel_back
            self.option_button = option_button

class Tile(Button):
    TILE_SIZE = 56
    
    def __init__(self, x, y, text = "empty"):
        super().__init__(master = board_frame, text = text,
                        image = pixel,
                        activebackground = palette.selected,
                        background = Tile.determine_tile_bg_colour(x, y),
                        border = 3,
                        font = body_font,
                        compound = 'c',
                        width = Tile.TILE_SIZE,
                        height = Tile.TILE_SIZE,
                        command = self.on_click
                        )
        self.coords = (x, y)
        self.grid(row = x, column = y)
        self.selected = False
        
    def determine_tile_bg_colour(x, y):
        return palette.tile1 if (x % 2 == 0 and y % 2 == 0) or (not x % 2 == 0 and not y % 2 == 0) else palette.tile2
        
    def update_background_colour(self):
        if self.selected:
            colour = palette.selected
        elif self.coords in game_board.valid_moves:
            colour = palette.highlight
        else:
            colour = Tile.determine_tile_bg_colour(self.coords[X], self.coords[Y])
        self.configure(background = colour)
    
    def on_click(self):
        if game_board.source_tile == self:
            game_board.deselect_tiles()
        elif game_board.source_tile == None:
            game_board.source_tile = self
            self.selected = not self.selected
            game_board.highlight_valid_moves(game_board.source_tile)
        elif game_board.dest_tile == None:
            game_board.dest_tile = self
            self.selected = not self.selected
            game_board.try_move(game_board.source_tile, game_board.dest_tile)
        else:
            game_board.deselect_tiles()
        
    def format(self):
        value = game_board.board[self.coords[X]][self.coords[Y]]
        if(game_board.enable_move):
            self.update_background_colour()
        tile_text = ""
        text_colour = palette.text
        
        if(value == ArithChessLogic.FLAG):
            tile_text = "F"
        elif(value == -ArithChessLogic.FLAG):
            tile_text = "-F"
        elif(value != 0):
            tile_text = str(value)
            
        if(value > 0):
            text_colour = palette.player1
        if(value < 0):
            text_colour = palette.player2
            
        self.configure(
            fg = text_colour,
            text = tile_text
        )   
  
class OptionButton(Button):
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 30
    
    def __init__(self, x, text, command):
        super().__init__(master = option_buttons, text = text,
                        image = pixel,
                        activebackground = palette.selected,
                        background = palette.option_button,
                        border = 1,
                        font = body_font,
                        compound = 'c',
                        width = OptionButton.BUTTON_WIDTH,
                        height = OptionButton.BUTTON_HEIGHT,
                        padx = 8,
                        command = command
                        )
        self.grid(row = 0, column = x, padx = 16)

  
def set_title_label():
    title_label = Label(root, text = ArithChessLogic.TITLE, font = heading_font, background = palette.background, foreground = palette.text) 
    title_label.grid(row = 0, column = 0, sticky = "n", pady = PADDING)
    
def update_label(label, textvar, text, colour):
    textvar.set(text)
    label.configure(foreground = colour) 
    
def set_info_popup():
    RULES = ("- Player 1 controls positive numbers\n" +
        "- Player 2 controls positive numbers\n" +
        "- Capture the opponent's F piece\n" +
        "- Or force them not be able to move\n"
        "- A piece can move sqrt(n) spaces\n" +
        "- When two pieces collide, their values sum"
        )
    rules_title = Label(info_frame, text = "Rules", foreground = palette.text, background = palette.panel_back, font = heading_font)
    rules_text = Label(info_frame, text = RULES, 
                    foreground = palette.text, 
                    background = palette.panel_back, 
                    font = body_font,
                    justify = "left",
                    pady = PADDING / 2
                    )
    CREDITS = ("Game Logic/Design: Hong Fulin\n" + 
            "GUI: June Wilson\n\n" +
            "Press R to view the rules at any time."
            )
    credits_title = Label(info_frame, text = "Credits", foreground = palette.text, background = palette.panel_back, font = heading_font)
    credits_text = Label(info_frame, text = CREDITS, 
                        foreground = palette.text, 
                        background = palette.panel_back, 
                        font = body_font,
                        justify = "left",
                        pady = PADDING / 2
                        )

    rules_title.pack()
    rules_text.pack(padx = PADDING)
    credits_title.pack()
    credits_text.pack(padx = PADDING)

def set_info_popup_visibility(show):
    info_frame.grid(row = 1, column = 0, pady = PADDING * 2) if show else info_frame.grid_forget()

def toggle_show_info(event):
    global show_info
    show_info = not show_info
    set_info_popup_visibility(show_info)
    #print("r was pressed, " + str(show_info))
                       
def check_int(s):
    try:
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()
    except:
        return False

mixer.init()
piece_captured_sfx = mixer.Sound(r"assets/sfx/piece_captured.wav")
piece_placed_sfx = mixer.Sound(r"assets/sfx/piece_placed.wav")
invalid_move_sfx = mixer.Sound(r"assets/sfx/invalid_move.wav")
reset_board_sfx = mixer.Sound(r"assets/sfx/reset_board.wav")
game_over_sfx = mixer.Sound(r"assets/sfx/game_over.wav")

palette = Palette(
    text = "black", 
    background = "ivory2",
    tile1 = "white",
    tile2 = "gray67",
    player1 = "blue",
    player2 = "red",
    highlight = "green2",
    selected = "magenta",
    error = "red3",
    panel_back = "white",
    option_button = "lightsteelblue3"
    )

X = 0
Y = 1
root = Tk()
tile_px = 16
WIN_WIDTH = 1080
WIN_HEIGHT = 720
PADDING = 16
heading_font = ("Cascadia Code", 16)
body_font = ("Cascadia Code", 11)
pixel = PhotoImage(width = 1, height = 1)

game_board = GameBoard()
board_frame = Frame(root, bg = palette.tile1, bd = 3)
player_action_text = StringVar(root, "Your turn, Player 1")
player_action_label = Label(root, textvariable = player_action_text, font = body_font, background = palette.background, foreground = palette.player1)
move_error_text = StringVar(root, "")
move_error_label = Label(root, textvariable = move_error_text, font = body_font, background = palette.background, foreground = palette.error)

info_frame = Frame(root, bd = 3, background = palette.panel_back)
show_info = True

option_buttons = Frame(root, bd = 3, background = palette.background)
show_rules_button = OptionButton(0, "Show Rules", command = lambda: toggle_show_info(None))
reset_board_button = OptionButton(1, "Reset Board",  command = game_board.init_board)

if __name__ == "__main__":
    
    root.configure(bg = palette.background)
    root.title(ArithChessLogic.TITLE)
    root.resizable(width=False, height=False)
    root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
    root.bind('r', toggle_show_info)
    root.bind('R', toggle_show_info)
    set_title_label()


    game_board.init_board()
    game_board.create_menu_bar(root)

    board_frame.grid(row = 1, column = 0, padx = WIN_WIDTH / 4)
    player_action_label.grid(row = 2, column = 0)
    move_error_label.grid(row = 3, column = 0)
    option_buttons.grid(row = 4, column = 0)

    set_info_popup()
    set_info_popup_visibility(True)

    game_board.load_configuration_file()
    
    root.mainloop()
    