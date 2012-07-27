from pythonrv import rv, dbc

from game import Game, CellTypes

# this is an attempt at an runtime verification specification
# it will ensure that the rules of game of life is followed
@rv.monitor(update=Game.update)
def spec_update(event):
	board = event.update.inputs()[0].board
	for x in range(board.width):
		for y in range(board.height):
			n = board.num_live_neighbours(x,y)
			if n > 3:
				event.update.next(ensure_cell_state, (x,y,CellTypes.DEAD))
			elif n == 3:
				event.update.next(ensure_cell_state, (x,y,CellTypes.LIVE))
			elif n == 2 and board.cell_is_live(x, y):
				event.update.next(ensure_cell_state, (x,y,CellTypes.LIVE))
			else:
				event.update.next(ensure_cell_state, (x,y,CellTypes.DEAD))

def ensure_cell_state(event, x, y, t):
	board = event.update.inputs()[0].board
	assert board.cell_is_of_type(x, y, t), \
			"Cell (%d,%d) is not of type %s as it should be" % (x, y, t)

# you may not update the game without rendering in between:
# G(update -> rendering before update2)
# how to do this in LTL?
# update -> X !update
@rv.monitor(update=Game.update, render=Game.render)
def spec_show_update(event):
	if event.update.called:
		event.next(event.render, "Game update called without rendering in between")


@rv.monitor(update=Game.update, render=Game.render)
def spec_test(event):
	assert event.update.called or event.render.called, "None of event were called"
	#raise ValueError("fdsa")

#raise ValueError("asdf")
