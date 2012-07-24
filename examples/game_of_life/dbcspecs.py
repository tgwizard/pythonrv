from pythonrv import dbc

from game import Game, CellTypes

# this is an attempt at an design-by-contract specification
# it will ensure that the rules of game of life is followed
# it can be done through pure pre/post-condition contracts:
@dbc.after(Game.update)
@dbc.use_state(inargs = True)
def ensure_game_of_life_rules(state):
	ingame, = state.inargs
	inboard = ingame.board
	outgame, = state.outargs
	outboard = outgame.board
	for x in range(inboard.width):
		for y in range(inboard.height):
			n = inboard.num_live_neighbours(x,y)
			if n > 3:
				assert outboard.cell_is_of_type(x, y, CellTypes.DEAD), \
					"Too many neighbours (%d), (%d,%d) should be dead" % (n, x, y)
			elif n == 3:
				assert outboard.cell_is_of_type(x, y, CellTypes.LIVE), \
					"Right number of neighbours (%d), (%d,%d) should be live" % (n, x, y)
			elif n == 2 and inboard.cell_is_of_type(x, y, CellTypes.LIVE):
				assert outboard.cell_is_of_type(x, y, CellTypes.LIVE), \
					"Right number of neighbours (%d), (%d,%d) should still be live" % (n, x, y)
			else:
				assert outboard.cell_is_of_type(x, y, CellTypes.DEAD), \
					"Too few neighbours (%d), (%d,%d) should be dead" % (n, x, y)

# you may not update the game without rendering in between:
# this could be done with pre-condition contracts if we could store arbitrary
# state
@dbc.after(Game.update)
@dbc.after(Game.render)
@dbc.use_state(local_store = True)
def ensure_show_update(state):
	if state.function_name == 'update':
		# assert: either this is the first call, and val hasn't been set yet
		# or the last call was to render
		assert state.local_store.get('val', 'r') == 'r', \
				"Game update called without rendering in between"
		state.local_store['val'] = 'u'
	if state.function_name == 'render':
		state.local_store['val'] = 'r'
