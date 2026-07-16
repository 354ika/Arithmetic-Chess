#!/usr/bin/env python3
import re
from os import system
# ensures ansi chars work on windows cmd line
system("")

VERSION_NUMBER = 0.4
TITLE = "Arithmetic Chess v" + str(VERSION_NUMBER)

WIDTH = 8
HEIGHT = 8
FLAG = 2**63 - 1
CELL_WIDTH = 4

GAME_OVER = 1
SUCCESS = 0
FAILURE = -1

colour_error = "\x1b[1;91m"
colour_red = "\x1b[91m"
colour_green = "\x1b[92m"
colour_highlight = "\x1b[92m\x1b[7m"
colour_yellow = "\x1b[1;93m"
colour_cyan = "\x1b[96m"
colour_reset = "\x1b[0m"
colour_dark = "\x1b[90m"

player0 = "Alice"
player1 = "Bob"

board = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

def print_board(board : list[list[int]], valid_moves : list[tuple[int, int]]) -> None:
	for y in reversed(range(len(board))):
		row = board[y]

		print(f"{y:2} |", end=" ")
		for x in range(len(board[0])):
			print(format_cell(x, y, board, valid_moves), end="")

		print()

	print(" "*8 + (" "*3).join("-" for _ in range(len(board[0]))))

	print(" "*8 + (" "*3).join(f"{x}" for x in range(len(board[0])) if x < 10) 
		+ " "*2 + (" "*2).join(f"{x}" for x in range(len(board[0])) if x >= 10))

def init_board(width : int, height : int, ic : list[tuple[int, int, int]]) -> list[list[int]] | None:
	b = create_board(width, height)
	for param in ic:
		try:
			b[param[1]][param[0]] = param[2]
		except Exception as e:
			print(f"Board initialization error: {e}, board will be empty")
			return create_board(width, height)
	return b

def create_board(width : int, height : int) -> list[list[int]]:
	return [[0 for _ in range(width)] for _ in range(height)]

def format_cell(xpos : int, ypos : int, board : list[list[int]],
				valid_moves : list[tuple[int, int]]) -> str:
	value = board[ypos][xpos]

	if ((xpos, ypos) in valid_moves and abs(value) == FLAG):
		return colour_highlight + "F".rjust(CELL_WIDTH) + colour_reset
	elif ((xpos, ypos) in valid_moves and value != 0):
		return colour_highlight + str(value).rjust(CELL_WIDTH) + colour_reset
	elif ((xpos, ypos) in valid_moves and value == 0):
		return colour_highlight + ".".rjust(CELL_WIDTH) + colour_reset
	elif value == 0:
		return colour_dark + ".".rjust(CELL_WIDTH) + colour_reset
	elif value == FLAG:
		return colour_cyan + "F".rjust(CELL_WIDTH) + colour_reset
	elif value == -FLAG:
		return colour_red + "-F".rjust(CELL_WIDTH) + colour_reset

	if value > 0:
		return colour_cyan + str(value).rjust(CELL_WIDTH) + colour_reset
	if value < 0:
		return colour_red + str(value).rjust(CELL_WIDTH) + colour_reset

def clear_screen():
	print("\x1b[2J\x1b[3J\x1b[H",end="")

def try_move(board : list[list[int]], sx : int, sy : int,
									  dx : int, dy : int, 
									  current_turn : int) -> int:
	
	if (sy < 0 or sy >= len(board) or 
		sx < 0 or sx >= len(board[0])):
		print("Source square is out of bounds.")
		return FAILURE

	x = board[sy][sx]

	if (sy + dy < 0 or sy + dy >= len(board) or 
		sx + dx < 0 or sx + dx >= len(board[0])):
		print("Destination square is out of bounds.")
		return FAILURE

	y = board[sy + dy][sx + dx]

	if x == 0:
		print("Error: Source square is empty.")
		return FAILURE
	elif current_turn * x < 0:
		print("Error: Cannot move enemy piece.")
		return FAILURE
	elif abs(x) == FLAG:
		print("Flags cannot move (Euclidean movement constraint not satisfied.)")
		return FAILURE
	elif (dx*dx + dy*dy != abs(x)):
		print("Error: Euclidean movement constraint not satisfied.")
		return FAILURE

	board[sy][sx] = 0
	if y == -FLAG * current_turn:
		# print("You win!")
		board[sy + dy][sx + dx] = x
		return GAME_OVER
	elif y == FLAG * current_turn:
		print("Losing by capturing your own flag is not allowed.")
		return FAILURE

	board[sy + dy][sx + dx] = x + y
	return SUCCESS

		


	# except Exception as e:
	# 	print(f"Error: {e}.")
	# 	return FAILURE

def is_square(param: int) -> {0, 1}:
	if param >= 0 and int(param ** (1/2)) ** 2 == param:
		return 1
	return 0

def all_valid_displacements(param: int) -> list[tuple[int, int]]:
	l = list()

	for x in range(-int(param ** (1/2)), int(param ** (1/2)) + 1):
		if is_square(param - x**2):
			l.append((x, -int((param - x**2) ** (1/2))))
			if (param != x**2):
				l.append((x, int((param - x**2) ** (1/2))))
	return l

def all_valid_moves(bsize: tuple[int, int], pos: tuple[int, int], param: int) -> list[tuple[int, int]]:
	bparam = bsize[0] ** 2 + bsize[1] ** 2
	if param > bparam:
		return []

	moves = all_valid_displacements(param)


	l = list()

	for move in moves:
		if (0 <= move[0] + pos[0] and move[0] + pos[0] < bsize[0] and 
			0 <= move[1] + pos[1] and move[1] + pos[1] < bsize[1]):
			l.append((move[0] + pos[0], move[1] + pos[1]))

	return l

def extract_move(arg: str) -> tuple[int, int, int]:
	# Arguments may be presented in the following forms:
	#	1.	Two numbers, separated by any number of spaces
	#	2.	Two numbers, separated by a comma, and any number of spaces


	parts = [s for s in re.split(r"[\(,;\) ]+", arg) if s]
	if len(parts) != 2:
		clear_screen()
		print(colour_error + "Error: Invalid input format.\n\n" + colour_reset)
		return (0, 0, FAILURE)

	try:
		x, y = map(int, parts)
	except ValueError:
		clear_screen()
		print(colour_error + "Error: Input must be integers.\n\n" + colour_reset)
		return (0, 0, FAILURE)
	
	return (x, y, SUCCESS)

icA = (8, 8, [
	(0, 0, FLAG),
	(1, 1, 4),
	(6, 6, -4),
	(7, 7, -FLAG),
])

icB = (8, 8, [
	(0, 0, FLAG),
	(1, 0, 5),
	(2, 0, 2),
	(1, 1, 4),
	(2, 1, 1),

	(5, 6, -1),
	(6, 6, -4),
	(5, 7, -2),
	(6, 7, -5),
	(7, 7, -FLAG)
])

icC = (8, 8, [
	(0, 0, 4),
	(1, 0, 5),
	(2, 0, 8),
	(3, 0, 2),
	(4, 0, FLAG),
	(5, 0, 8),
	(6, 0, 5),
	(7, 0, 4),
	(0, 1, 1),
	(1, 1, 1),
	(2, 1, 1),
	(3, 1, 1),
	(4, 1, 1),
	(5, 1, 1),
	(6, 1, 1),
	(7, 1, 1),

	(0, 6, -1),
	(1, 6, -1),
	(2, 6, -1),
	(3, 6, -1),
	(4, 6, -1),
	(5, 6, -1),
	(6, 6, -1),
	(7, 6, -1),
	(0, 7, -4),
	(1, 7, -5),
	(2, 7, -8),
	(3, 7, -2),
	(4, 7, -FLAG),
	(5, 7, -8),
	(6, 7, -5),
	(7, 7, -4)
])

icD = (8, 8, [
	(0, 0, FLAG),
	(1, 0, 5),
	(2, 0, 2),
	(0, 1, 5),
	(1, 1, 4),
	(2, 1, 1),
	(0, 2, 2),
	(1, 2, 1),
	(2, 2, 1),

	(5, 5, -1),
	(6, 5, -1),
	(7, 5, -2),
	(5, 6, -1),
	(6, 6, -4),
	(7, 6, -5),
	(5, 7, -2),
	(6, 7, -5),
	(7, 7, -FLAG)
])

lookup = [icA, icB, icC, icD]

def main():
	debug = 1
	clear_screen()
	print(TITLE + "\n")
	print("\n")

	print("Rules: ")
	print(f"1. {colour_cyan}Player 1{colour_reset} controls the {colour_cyan}positive numbers (cyan).{colour_reset}")
	print(f"   {colour_red}Player 2{colour_reset} controls the {colour_red}negative numbers (red).{colour_reset}")
	print(f"2. The objective of the game is to capture your opponent's flag (the F piece).")
	print(f"3. A piece with absolute value n can move to a square exactly distance sqrt(n) away.")
	print(f"   This distance is Euclidean distance, and basically means dx^2 + dy^2 = abs(n).")
	print(f"4. Whenever two pieces with values a and b land on the same square, they add together.")
	print(f"   A piece with value a + b is formed.")

	print("\n")
	print(f"{colour_cyan}Player 1{colour_reset}, please enter your name (Defaults to Alice): ", )
	s = input()

	if s:
		player0 = s
		print(f"Hello, {colour_cyan}{s}{colour_reset}!")
	else:
		player0 = "Alice"


	print(f"{colour_red}Player 2{colour_reset}, please enter your name (Defaults to Bob): ")
	s = input()

	if s:
		player1 = s
		print(f"Hi, {colour_red}{s}{colour_reset}!")
	else:
		player1 = "Bob"

	print(f"When you're ready.\n<Press Enter key to continue...>")

	s = input()


	clear_screen()
	print(TITLE + "\n\n")
	# Load initial conditions by hand here
	board = init_board(8, 8, icB[2])
	if debug and s:
		try:
			boardid = int(s)
			if (0 <= boardid and boardid <= 3):
				board = init_board(*lookup[boardid])
			else:
				board = init_board(*icB)
		except ValueError:
			board = init_board(*icB)

	boardy = len(board)
	boardx = len(board[0])
	current_sign = 1



	while True:

		player_0_can_move = 0
		player_1_can_move = 0

		for y in range(len(board)):
			for x in range(len(board[0])):
				if board[y][x] == 0:
					continue
				elif board[y][x] > 0 and all_valid_moves((boardx, boardy), (x, y), board[y][x]) != []:
					player_0_can_move = 1
				elif board[y][x] < 0 and all_valid_moves((boardx, boardy), (x, y), -board[y][x]) != []:
					player_1_can_move = 1

		if player_0_can_move == 0 and player_1_can_move == 0:
			print(colour_yellow + "Neither player can move, the game is drawn!\n\n" + colour_reset)
			print_board(board)
			break

		if player_0_can_move == 0 and current_sign == 1:
			print(colour_yellow + player0 + "cannot move!\n\n" + colour_reset)
			current_sign *= -1
			continue

		if player_1_can_move == 0 and current_sign == -1:
			print(colour_yellow + player1 + "cannot move!\n\n" + colour_reset)
			current_sign *= -1
			continue
				

		print_board(board, [])
		if current_sign == 1:
			print(f"\n\n{colour_cyan}{player0}{colour_reset}, it's your turn!")
		else:
			print(f"\n\n{colour_red}{player1}{colour_reset}, it's your turn!")	

		# Select piece
		move = input("Select piece at location: ")
		sx, sy, status = extract_move(move)
		if status == FAILURE:
			continue

		if (sy < 0 or sy >= len(board) or 
			sx < 0 or sx >= len(board[0])):
			clear_screen()
			print(colour_error + "Source square is out of bounds.\n\n" + colour_reset)
			continue

		if board[sy][sx] == 0:
			clear_screen()
			print(colour_error + "Error: Source square is empty.\n\n" + colour_reset)
			continue

		if board[sy][sx] * current_sign < 0:
			clear_screen()
			print(colour_error + "Error: Cannot move enemy piece.\n\n" + colour_reset)
			continue

		x = board[sy][sx]
		clear_screen()
		print(TITLE + "\n\n")
		print_board(board, all_valid_moves((boardx, boardy), (sx, sy), abs(x)))

		str1 = ""
		if current_sign == 1:
			str1 = colour_cyan + str(x) + colour_reset
		else:
			str1 = colour_red + str(x) + colour_reset

		print(f"Piece selected: {str1} on {(sx, sy)}",end=" ")
		if all_valid_moves((boardx, boardy), (sx, sy), abs(x)) != []:
			print(colour_green + "Valid moves: ",end="")
			print(all_valid_moves((boardx, boardy), (sx, sy), abs(x)),end="")
			print(colour_reset)
		else:
			print(colour_highlight + "Warning: This piece cannot move!" + colour_reset)

		move = input("Move piece to location: ")
		tx, ty, status = extract_move(move)
		if status == FAILURE:
			continue

		if (ty < 0 or ty >= len(board) or 
			tx < 0 or tx >= len(board[0])):
			clear_screen()
			print(colour_error + "Error: Destination square is out of bounds.\n\n" + colour_reset)
			continue

		if ((ty - sy) * (ty - sy) + (tx - sx) * (tx - sx)) != abs(x):
			clear_screen()
			print(colour_error + f"Error: Euclidean movement constraint is not satisfied. \n (({tx - sx})^2 + ({ty - sy})^2 = {(tx - sx)**2 + (ty - sy)**2}, not {abs(x)})\n" + colour_reset)
			continue

		y = board[ty][tx]

		if y == FLAG * current_sign:
			clear_screen()
			print(colour_error + "Error: Capturing your own flag is not allowed.\n\n" + colour_reset)
			continue


		#print(f"sx: {sx}, sy: {sy}, dx: {dx}, dy: {dy}")
		result = try_move(board, sx, sy, tx-sx, ty-sy, current_sign)

		if result == GAME_OVER:
			print_board(board, [])
			if current_sign == 1:
				print(f"{colour_cyan}{player0}{colour_reset} wins!")
			else:
				print(f"{colour_red}{player1}{colour_reset} wins!")
			s = input("Another game?")
			c = str(s[0]) if s else 0 

			if (c in "+1TtYy"): 
				...
			elif (c in "Rr"):
				main()
				break
			elif (c in "Dd"):
				debug = 1
				main()
				break
			else:
				break
			
		elif result == FAILURE:
			continue



		clear_screen()
		print(TITLE + "\n\n")


		current_sign *= -1




if __name__ == "__main__":
	main()