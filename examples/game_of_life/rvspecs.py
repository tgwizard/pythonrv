from pythonrv import rv, dbc

from game import Game, CellTypes

# this is an attempt at an runtime verification specification
# it will ensure that the rules of game of life is followed
class GameSpec(rv.Spec):
	@rv.monitors(update=Game.update)
	@rv.spec
	def spec_update(self, monitors):
		game, board = monitors.update.inputs()

		for x in range(board.width):
			for y in range(board.height):
				n = board.neighbours(x,y)
				# next is unfortunately a keyword...
				if n > 3:
					monitors.update.next(self.ensure_cell_state, (x,y,CellTypes.DEAD)
				elif n in (2,3):
					monitors.update.next(self.ensure_cell_state, (x,y,CellTypes.LIVE)
				else:
					monitors.update.next(self.ensure_cell_state, (x,y,CellTypes.DEAD)

	def ensure_cell_state(self, x, y, t):
		assert board.cell_is_of_type(x, y, t)

# you may not update the game without rendering in between:
# G(update -> rendering before update2)
# how to do this in LTL?
class ShowUpdatesSpec(rv.Spec):
	@rv.monitors(update=Game.update, render=Game.render)
	@rv.spec
	def spec_show_update(self, monitors):
		if monitors.update.called:
			monitors.next(monitors.render)
