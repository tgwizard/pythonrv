from pythonrv import rv, dbc

from game import Game, CellTypes

# this is an attempt at an runtime verification specification
# it will ensure that the rules of game of life is followed
@rv.monitors(update=Game.update)
def spec_update(monitors):
	board = monitors.update.inputs()[0].board
	for x in range(board.width):
		for y in range(board.height):
			n = board.num_live_neighbours(x,y)
			# next is unfortunately a keyword...
			if n > 3:
				monitors.update.next(ensure_cell_state, (x,y,CellTypes.DEAD))
			elif n == 3:
				monitors.update.next(ensure_cell_state, (x,y,CellTypes.LIVE))
			elif n == 2 and board.cell_is_live(x, y):
				monitors.update.next(ensure_cell_state, (x,y,CellTypes.LIVE))
			else:
				monitors.update.next(ensure_cell_state, (x,y,CellTypes.DEAD))

def ensure_cell_state(monitors, x, y, t):
	board = monitors.update.inputs()[0].board
	assert board.cell_is_of_type(x, y, t), \
			"Cell (%d,%d) is not of type %s as it should be" % (x, y, t)

# you may not update the game without rendering in between:
# G(update -> rendering before update2)
# how to do this in LTL?
@rv.monitors(update=Game.update, render=Game.render)
def spec_show_update(monitors):
	if monitors.update.called:
		monitors.next(monitors.render, "Game update called without rendering in between")


@rv.monitors(update=Game.update, render=Game.render)
def spec_test(monitors):
	assert monitors.update.called or monitors.render.called, "None of monitors were called"
	#raise ValueError("fdsa")

#raise ValueError("asdf")
