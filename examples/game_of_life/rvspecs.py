from pythonrv import rv

from game import Game, CellTypes

# a generator to iterate through all board cells
def all_board_cells(board):
	for x in range(board.width):
		for y in range(board.height):
			n = board.num_live_neighbours(x,y)
			yield (x, y, n)

# this is an attempt at an runtime verification specification
# it will ensure that the rules of game of life is followed
@rv.monitor(update=Game.update)
def spec_update(event):
	board = event.fn.update.inputs[0].board
	for x, y, n in all_board_cells(board):
		if n > 3:
			event.fn.update.next(ensure_cell_state, (x,y,CellTypes.DEAD))
		elif n == 3:
			event.fn.update.next(ensure_cell_state, (x,y,CellTypes.LIVE))
		elif n == 2 and board.cell_is_live(x, y):
			event.fn.update.next(ensure_cell_state, (x,y,CellTypes.LIVE))
		else:
			event.fn.update.next(ensure_cell_state, (x,y,CellTypes.DEAD))

def ensure_cell_state(event, x, y, t):
	board = event.fn.update.inputs[0].board
	assert board.cell_is_of_type(x, y, t), \
			"Cell (%d,%d) is not of type %s as it should be" % (x, y, t)

# you may not update the game without rendering in between:
# G(update -> rendering before update2)
# how to do this in LTL?
# update -> X !update
@rv.monitor(update=Game.update, render=Game.render)
def spec_show_update(event):
	if event.fn.update.called:
		event.next_called_should_be(event.fn.render,
				"Game update called without rendering in between")


# update may not be called before render has been called once
@rv.monitor(update=Game.update, render=Game.render)
def spec_render_before_update(event):
	if event.fn.update.called:
		assert len(event.history) > 1, "Game update called without calling render first"
		event.success()
	# we can also do it like this
	if len(event.history) == 1:
		# the first event/function call
		# the following two assertions are equal
		assert event.history[0].fn.render.called, "Game update called without calling render first"
		assert event.fn.render.called, "Game update called without calling render first"
		event.success()

@rv.monitor(update=Game.update, render=Game.render)
def spec_render_before_update_always(event):
	if event.fn.update.called:
		assert len(event.history) > 1, "Game update called without calling something else first"
		assert event.prev.fn.render.called, "Render must be called before update"

@rv.monitor(update=Game.update, render=Game.render)
def spec_test(event):
	assert event.fn.update.called or event.fn.render.called, "None of event were called"
	#raise ValueError("fdsa")

#raise ValueError("asdf")
