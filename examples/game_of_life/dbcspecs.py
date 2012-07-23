from pythonrv import rv, dbc

from game import Game, CellTypes

# this is an attempt at an design-by-contract specification
# it will ensure that the rules of game of life is followed
# it can be done through pure pre/post-condition contracts:
@dbc.after(Game.update)
@dbc.use_state(inargs = True)
def ensure_game_of_life_rules(state, outgame, outboard):
	ingame, inboard = state.inargs
	for x in range(inboard.width):
		for y in range(inboard.height):
			n = inboard.neighbours(x,y)
			# next is unfortunately a keyword...
			if n > 3:
				assert outboard.cell_is_of_type(x, y, CellTypes.DEAD)
			elif n in (2,3):
				assert outboard.cell_is_of_type(x, y, CellTypes.LIVE)
			else:
				assert outboard.cell_is_of_type(x, y, CellTypes.DEAD)

# you may not update the game without rendering in between:
# this could be done with pre-condition contracts if we could store arbitrary
# state
@dbc.after(Game.update)
@dbc.after(Game.render)
@dbc.use_state(store = True)
def ensure_show_update(state):
	if state.function == Game.update:
		# assert: either this is the first call, and val hasn't been set yet
		# or the last call was to render
		assert state.store.get('val', 'r') == 'r'
		state.store.val = 'u'
	if state.function == Game.render:
		state.store.val = 'r'
