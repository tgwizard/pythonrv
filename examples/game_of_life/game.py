from time import sleep
from copy import deepcopy

class CellTypes:
	DEAD = 0
	LIVE = 1

tiles = {
		CellTypes.DEAD: ' ',
		CellTypes.LIVE: '#',
}


class Board(object):
	def __init__(self, width=10, height=10):
		"""
		Initialize the game board with dead cells.
		"""
		b = []
		for x in range(width):
			b.append([CellTypes.DEAD for y in range(height)])
		self.board = b
		self.width = width
		self.height = height

	def copy(self):
		return deepcopy(self)

	def num_live_neighbours(self, x, y):
		num = 0
		for i in range(-1, 2):
			for j in range(-1, 2):
				if self.cell_is_live(x+i,y+j):
					num += 1
		if self.cell_is_live(x,y):
			num -= 1
		return num

	def cell_is_live(self, x, y):
		return self.cell_is_of_type(x, y, CellTypes.LIVE)

	def cell_is_dead(self, x, y):
		return self.cell_is_of_type(x, y, CellTypes.DEAD)

	def cell_is_of_type(self, x, y, cell_type):
		x,y = self.coords_modulo(x,y)
		return self.board[x][y] == cell_type

	def make_dead(self, x, y):
		self.make_cell(x, y, CellTypes.DEAD)

	def make_live(self, x, y):
		self.make_cell(x, y, CellTypes.LIVE)

	def make_cell(self, x, y, cell_type):
		x,y = self.coords_modulo(x,y)
		self.board[x][y] = cell_type

	def cell_tile(self, x, y):
		return tiles[self.cell(x,y)]

	def cell(self, x, y):
		x,y = self.coords_modulo(x,y)
		return self.board[x][y]

	def coords_modulo(self, x, y):
		return (x+self.width) % self.width, (y+self.height)%self.height

	def __str__(self):
		out = []
		for y in range(self.height):
			row = ''.join([tiles[board_row[y]] for board_row in self.board])
			out.append(row)
		return '\n'.join(out)

class Game(object):
	def __init__(self, graphics, board):
		self.graphics = graphics
		self.board = board
		self.exited = False

	def update(self):
		old = self.board.copy()
		for x in range(old.width):
			for y in range(old.height):
				num = old.num_live_neighbours(x,y)
				if old.cell_is_live(x,y):
					if num < 2:
						self.board.make_dead(x,y)
					elif num >= 2 and num <= 3:
						self.board.make_live(x,y)
					else:
						self.board.make_dead(x,y)
				else:
					if num == 3:
						self.board.make_live(x,y)

	def render(self, iteration):
		self.graphics.render(self.board, iteration)

	def main_loop(self, fps=1):
		sleep_duration = 1.0 / fps
		iteration = 0
		while not self.exited:
			self.render(iteration)
			self.update()
			sleep(sleep_duration)
			iteration += 1

		self.graphics.destroy()

	def exit(self):
		print "exited"
		self.exited = True
