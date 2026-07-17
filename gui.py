from arithmetic_chess import *
from tkinter import *

class BoardDisplay:
    # TO-DO, use game logic to determine what each tile actually contains
    
    def __init__(self):
        self.board_tiles = []
        
    def get_tile_at_coord(self, x, y):
        tile_idx = x + (y * WIDTH)
        tile = self.board_tiles[tile_idx]
        # print("coord:" + str(tile.coords))
        return tile
        
    def get_selected_tiles(self, max_selectex = None):
        selected_tiles = []
        for t in self.board_tiles:
            if t.selected:
                selected_tiles.append(t)
        if(max_selectex is not None and len(selected_tiles) > max_selectex):
            self.deselect_all_tiles()
            return []
        else:
            return selected_tiles
                
    def load_board_state(self, board : list[list[int]], valid_moves : list[tuple[int, int]]):
        self.destroy_tiles()
        for x in range(WIDTH):
            for y in range(HEIGHT):
                new_tile = Tile(x, y)
                print(new_tile.coords)
                new_tile.format(board, valid_moves)
                self.board_tiles.append(new_tile)
          
    def deselect_all_tiles(self):
        for t in self.board_tiles:
            t.selected = False
            t.format()
                
    def destroy_tiles(self):
        for tile in self.board_tiles:
            tile.destroy()
            
class Palette:
    def __init__(self, text, background, tile1, tile2, player1, player2, highlight, tile_clicked, error):
            self.text = text
            self.background = background
            self.tile1 = tile1
            self.tile2 = tile2
            self.player1 = player1
            self.player2 = player2
            self.highlight = highlight
            self.tile_clicked = tile_clicked
            self.error = error

class Tile(Button):
    TILE_SIZE = 56
    
    def __init__(self, x, y, text = "empty"):
        super().__init__(master = board_frame, text = text,
                        image = pixel,
                        activebackground = palette.tile_clicked,
                        background = Tile.determine_tile_bg_colour(x, y),
                        border = 2,
                        font = body_font,
                        compound = 'c',
                        width = int(Tile.TILE_SIZE * 1.05),
                        height = Tile.TILE_SIZE
                        )
        self.coords = (x, y)
        self.grid(row = x, column = y)
        self.selected = False
        self.configure(command = self.on_click)
        
    def determine_tile_bg_colour(x, y):
        return palette.tile1 if (x % 2 == 0 and y % 2 == 0) or (not x % 2 == 0 and not y % 2 == 0) else palette.tile2
        
    def update_background_colour(self):
        self.configure(background = palette.tile_clicked if self.selected else Tile.determine_tile_bg_colour(self.coords[X], self.coords[Y]))
    
    def on_click(self):
        self.selected = not self.selected
        self.update_background_colour()
        
    def format(self, board, valid_moves):
        value = board[self.coords[X]][self.coords[Y]]
        
        ### defaults
        back_colour = Tile.determine_tile_bg_colour(self.coords[X], self.coords[Y])
        # tile_text = f"{self.coords[X]}, {self.coords[Y]}"
        tile_text = ""
        text_colour = palette.text
        
        if(self.coords in valid_moves):
            back_colour = palette.highlight
        
        if(value == FLAG):
            tile_text = "F"
        elif(value == -FLAG):
            tile_text = "-F"
        elif(value != 0):
            tile_text = str(value)
            
        if(value > 0):
            text_colour = palette.player1
        if(value < 0):
            text_colour = palette.player2
            
        if(self.selected):
            back_colour = palette.tile_clicked
            
        self.configure(
            bg = back_colour,
            fg = text_colour,
            text = tile_text
        )
            
LIGHT = Palette(
    text = "black", 
    background = "ivory2",
    tile1 = "white",
    tile2 = "gray67",
    player1 = "blue",
    player2 = "red",
    highlight = "green",
    tile_clicked = "magenta",
    error = "red3"
    )

X = 0
Y = 1
palette = LIGHT
root = Tk()
tile_px = 16
WIN_WIDTH = 1080
WIN_HEIGHT = 720
PADDING = 8
heading_font = ("Cascadia Code", 16)
body_font = ("Cascadia Code", 11)
pixel = PhotoImage(width = 1, height = 1)

board_display = BoardDisplay()

board_frame = Frame(root, bg = palette.tile1, width = WIN_WIDTH / 3, height = WIN_WIDTH / 3, bd = 3)
debug_buttons = Frame(root, bg = palette.tile1, width = WIN_WIDTH / 3, height = WIN_HEIGHT / 6, bd = 3)
print_selected_tiles = Button(debug_buttons, width = 3, bg = palette.highlight, command = lambda : print(str(len(board_display.get_selected_tiles(2)))))
print_selected_tiles.grid(row = 0, column = 0)

def set_title_label():
    title_label = Label(root, text = TITLE, font = heading_font, background = palette.background) 
    title_label.pack(pady = PADDING)
    

if __name__ == "__main__":
    root.configure(bg = palette.background)
    root.title(TITLE)
    root.resizable(width=False, height=False)
    root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
    
    set_title_label()
    
    test_board = init_board(WIDTH, HEIGHT, icB[2])
    print(str(test_board))
    board_display.load_board_state(test_board, [])
    board_frame.pack()
    debug_buttons.pack()
    
    root.mainloop()
    