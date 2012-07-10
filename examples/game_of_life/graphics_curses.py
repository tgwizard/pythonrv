import curses

class Graphics(object):
	def __init__(self):
		self.window = curses.initscr()
		curses.noecho()
		curses.cbreak()
		self.window.nodelay(1)
		self.window.keypad(1)

	def get_size(self):
		return self.window.getmaxyx()

	def destroy(self):
		curses.nocbreak()
		self.window.keypad(0)
		self.window.nodelay(0)
		curses.echo()
		curses.endwin()

	def render(self, board):
		self.window.clear()
		self.window.border()
		#for x in range(board.width):
		#	for y in range(board.height):
		#		self.window.addch(y+1, x+1, board.cell_tile(x,y))
		self.window.addstr(0, 0, "wohooo")
		return self.window.getch() != curses.ERR

