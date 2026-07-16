from arithmetic_chess import *
from tkinter import *

class BoardDisplay:
    TILE_W = 8
    TILE_H = 3
    
    # TO-DO, use game logic to determine what each tile actually contains
    
    def __init__(self):
        self.board_tiles = []
        self.selected_tile = (-1, -1)  
    
    def set_selected_tile(xpos, ypos):
        self.selected_tile = (xpos, ypos)    
        
    def coord_to_tile(xpos : int, ypos : int, board : list[list[int]], valid_moves : list[tuple[int, int]], root, palette):
        pass
        
    def alternate_tile_bg_colours(x, y, palette):
        return palette.tile1 if (x % 2 == 0 and y % 2 == 0) or (not x % 2 == 0 and not y % 2 == 0) else palette.tile2
        
    def set_test_board_tiles(self, root, palette):
        for x in range(WIDTH):
            for y in range(HEIGHT):
                new_tile = Button(root, text = f"{x}, {y}", 
                                               width = BoardDisplay.TILE_W, 
                                               height = BoardDisplay.TILE_H,
                                               activebackground = palette.tile_clicked,
                                               background = BoardDisplay.alternate_tile_bg_colours(x, y, palette),
                                               border = 2,
                                               highlightthickness = 0
                                               )
                new_tile.grid(row = x, column = y)
                self.board_tiles.append(new_tile)    
                
    def clear_tiles(self):
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
            
LIGHT = Palette(
    text = "black", 
    background = "ivory2",
    tile1 = "white",
    tile2 = "gray67",
    player1 = "cyan",
    player2 = "red",
    highlight = "green",
    tile_clicked = "magenta",
    error = "red3"
    )

palette = LIGHT
root = Tk()
board_display = BoardDisplay()

if __name__ == "__main__":
    root.configure(bg = palette.background)
    root.title(TITLE)
    root.geometry("750x500")
    
    board_display.set_test_board_tiles(root, palette)
    # board_display.clear_tiles()
    
    root.mainloop()
    