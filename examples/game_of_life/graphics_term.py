import os

class Graphics(object):
	def destroy(self):
		pass

	def render(self, board, iteration):
		os.system('clear')
		maxx = board.width+2
		maxy = board.height+2
		for y in range(maxy):
			for x in range(maxx):
				print self.get_char(board, x, y, maxx, maxy),
			print ""
		print "Iteration: %d" % iteration

	def get_char(self, board, x, y, maxx, maxy):
		bd = self._get_border_char(x, y, maxx, maxy)
		if bd != '':
			return bd
		return board.cell_tile(x-1, y-1)

	def _get_border_char(self, x, y, maxx, maxy):
		vertical = (x == 0 or x == maxx-1)
		horizontal = (y == 0 or y == maxy-1)
		if vertical and horizontal:
			return '+'
		if vertical:
			return '|'
		if horizontal:
			return '-'
		return ''

