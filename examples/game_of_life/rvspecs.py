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
# G(update -> rendering before update2)
# how to do this in LTL?
class ShowUpdatesSpec(rv.Spec):

	@rv.monitors(update=Game.update, render=Game.render)
	@rv.spec
	def spec_show_update(self, monitors):
		if monitors.update.called:
			monitors.next(monitors.render)

# this could be done with pre-condition contracts if we could store arbitrary
# state
@dbc.after(Game.update)
@dbc.after(Game.render)
@dbc.use_staet(store = True)
def ensure_show_update(state):
	if state.function == Game.update:
		# assert: either this is the first call, and val hasn't been set yet
		# or the last call was to render
		assert state.store.get('val', 'r') == 'r'
		state.store.val = 'u'
	if state.function == Game.render:
		state.store.val = 'r'

