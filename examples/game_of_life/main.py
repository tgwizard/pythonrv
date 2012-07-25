#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

#import dbcspecs
import rvspecs

import game
import graphics_term as graphics

def main():
	if len(sys.argv) == 2:
		board = read_file(sys.argv[1])
	else:
		board = game.Board(4, 4)
		board.make_live(1,1)
		board.make_live(1,2)
		board.make_live(1,3)
	gol = game.Game(graphics.Graphics(), board)
	return gol.main_loop(fps=10)

def read_file(filename):
	f = open(filename, 'r')
	width = int(f.readline())
	height = int(f.readline())
	board = game.Board(width, height)

	y = 0
	while True:
		line = f.readline()
		if line == '':
			break
		x = 0
		for c in line[:-1]:
			if c == game.tiles[game.CellTypes.LIVE]:
				board.make_live(x,y)
			x += 1
		y += 1

	f.close()
	return board

if __name__ == '__main__':
	main()
