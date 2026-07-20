import arithmetic_chess as ArithChessLogic
from tkinter import *

class GameBoard:
    # TO-DO, use game logic to determine what each tile actually contains

    def __init__(self):
        self.board_tiles = []
        self.valid_moves = []
        self.board = []
        
    def get_tile_at_coord(self, x, y):
        tile_idx = x + (y * ArithChessLogic.WIDTH)
        tile = self.board_tiles[tile_idx]
        # print("coord:" + str(tile.coords))
        return tile
        
    def handle_selected_tiles(self):
        selected_tiles = []
        for t in self.board_tiles:
            if t.selected:
                selected_tiles.append(t)
        number_of_selected_tiles = len(selected_tiles)
        print(f"Number of selected tiles: {number_of_selected_tiles}")
        if(number_of_selected_tiles == 1):
            self.highlight_valid_moves(selected_tiles[0])
            return
        elif(number_of_selected_tiles > 1):
            self.try_move(selected_tiles[0], selected_tiles[1])
        self.deselect_all_tiles()
                
    def init_board(self):
        self.board = ArithChessLogic.init_board(ArithChessLogic.WIDTH, ArithChessLogic.HEIGHT, ArithChessLogic.icB[2])
        for x in range(ArithChessLogic.WIDTH):
            for y in range(ArithChessLogic.HEIGHT):
                new_tile = Tile(x, y)
                new_tile.format()
                self.board_tiles.append(new_tile)            
                
    def load_board_state(self, board : list[list[int]], valid_moves : list[tuple[int, int]]):
        self.board = board
        self.valid_moves = valid_moves
        for tile in self.board_tiles:
            tile.format()
          
    def deselect_all_tiles(self):
        self.valid_moves = []
        for t in self.board_tiles:
            t.selected = False
            t.format()
                
    def destroy_tiles(self):
        for tile in self.board_tiles:
            tile.destroy()
     
    def try_move(self, start_tile, dest_tile):
        sx = start_tile.coords[X]
        sy = start_tile.coords[Y]
        tx = dest_tile.coords[X] 
        ty = dest_tile.coords[Y]
        print(f"Trying: {sy}, {sx} -> {ty}, {tx}")
        success = ArithChessLogic.try_move(self.board, sy, sx, ty - sy, tx - sx, 1)
        if success == ArithChessLogic.SUCCESS:
            self.load_board_state(self.board, ())
            ArithChessLogic.print_board(self.board, [])
        print(f"Move success: {success}")
        
    def highlight_valid_moves(self, tile):
        try:
            value = abs(int(tile['text']))
        except:
            return
        moves = ArithChessLogic.all_valid_moves((ArithChessLogic.WIDTH, ArithChessLogic.HEIGHT), tile.coords, value)
        print(f"Moves number: {len(moves)}")
        self.load_board_state(self.board, moves)
            
class Palette:
    def __init__(self, text, background, tile1, tile2, player1, player2, highlight, selected, error):
            self.text = text
            self.background = background
            self.tile1 = tile1
            self.tile2 = tile2
            self.player1 = player1
            self.player2 = player2
            self.highlight = highlight
            self.selected = selected
            self.error = error

class Tile(Button):
    TILE_SIZE = 56
    
    def __init__(self, x, y, text = "empty"):
        super().__init__(master = board_frame, text = text,
                        image = pixel,
                        activebackground = palette.selected,
                        background = Tile.determine_tile_bg_colour(x, y),
                        border = 2,
                        font = body_font,
                        compound = 'c',
                        width = int(Tile.TILE_SIZE * 1.05),
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
        self.selected = not self.selected
        self.update_background_colour()
        game_board.handle_selected_tiles()
        
    def format(self):
        value = game_board.board[self.coords[X]][self.coords[Y]]
        
        ### defaults
        self.update_background_colour()
        # tile_text = f"{self.coords[X]}, {self.coords[Y]}"
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
  
def set_title_label():
    title_label = Label(root, text = ArithChessLogic.TITLE, font = heading_font, background = palette.background, foreground = palette.text) 
    title_label.grid(row = 0, column = 0, sticky = "n", pady = PADDING)
    
def update_player_action_label(text, colour):
    player_action_text.set(text)
    player_action_label.configure(foreground = colour) 
    
def set_info_popup():
    RULES = ("- Player 1 controls positive numbers\n" +
        "- Player 2 controls positive numbers\n" +
        "- Capture the opponent's F piece\n" +
        "- A piece can move sqrt(n) spaces\n" +
        "- When two pieces collide, their values sum"
        )
    rules_title = Label(info_frame, text = "Rules", foreground = palette.text, background = palette.tile1, font = heading_font)
    rules_text = Label(info_frame, text = RULES, 
                    foreground = palette.text, 
                    background = palette.tile1, 
                    font = body_font,
                    justify = "left"
                    )
    CREDITS = ("Game Logic/Design: Hong Fulin\n" + 
            "GUI: June Wilson"
            )
    credits_title = Label(info_frame, text = "Credits", foreground = palette.text, background = palette.tile1, font = heading_font)
    credits_text = Label(info_frame, text = CREDITS, 
                        foreground = palette.text, 
                        background = palette.tile1, 
                        font = body_font,
                        justify = "left"
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
    print("r was pressed, " + str(show_info))
                       
LIGHT = Palette(
    text = "black", 
    background = "ivory2",
    tile1 = "white",
    tile2 = "gray67",
    player1 = "blue",
    player2 = "red",
    highlight = "green2",
    selected = "magenta",
    error = "red3"
    )

X = 0
Y = 1
palette = LIGHT
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
player_action_text = StringVar(root, "placeholder")
player_action_label = Label(root, textvariable = player_action_text, font = body_font, background = palette.background)

info_frame = Frame(root, bd = 3, background = palette.tile1)
show_info = True

if __name__ == "__main__":
    root.configure(bg = palette.background)
    root.title(ArithChessLogic.TITLE)
    root.resizable(width=False, height=False)
    root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
    root.bind('r', toggle_show_info)
    root.bind('R', toggle_show_info)
    set_title_label()
    game_board.init_board()
    board_frame.grid(row = 1, column = 0, padx = WIN_WIDTH / 4)
    player_action_label.grid(row = 2, column = 0)
    set_info_popup()
    toggle_show_info(None)
    root.mainloop()
    