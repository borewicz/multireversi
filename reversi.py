#!/opt/local/bin/python
from __future__ import print_function
import sys
import random
#import time
import asyncore
import socket
import json
from PyQt4 import QtGui, QtCore

showHints = False 
board = []
for i in range(8):
	board.append([' '] * 8)
board[3][3] = 'X'
board[3][4] = 'O'
board[4][3] = 'O'
board[4][4] = 'X'
buttonGrid = []
playerTile = 'X'
computerTile = 'O'
app = QtGui.QApplication(sys.argv)
w = QtGui.QWidget()

class asyncClient(asyncore.dispatcher):

	def __init__(self, host):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect( (host, 8888) )
		#self.buffer = 'GET %s HTTP/1.0\r\n\r\n' % path
		#self.buffer = json.dumps({'x' : 1, 'y' : 1}, sort_keys=True, indent=4)
		self.buffer = ''

	def handle_connect(self):
		pass

	def handle_close(self):
		self.close()

	def handle_read(self):
		response = self.recv(8192)
		decoded = json.loads(response)
		x = decoded['x']
		y = decoded['y']
		#board[x][y] = computerTile
		makeMove(board, computerTile, x, y)
		for y in range(8):
			print('%s|' % (y+1), end='')
			for x in range(8):
				print(board[x][y], end='')
			print('|')
		convertBoard(board)

	def writable(self):
		return (len(self.buffer) > 0)

	#def handle_write(self):
		#sent = self.send(self.buffer)
		##to anuluje dalsze wysylanie w loopie
		#self.buffer = self.buffer[sent:] 

	def sendMove(self, x, y):
		self.board = board
		self.buffer = json.dumps({'x' : x, 'y' : y}, sort_keys=True, indent=4)
		sent = self.send(self.buffer)
		#to anuluje dalsze wysylanie w loopie
		self.buffer = self.buffer[sent:] 

class clientThread(QtCore.QThread):

	client = asyncClient('localhost')

	def run(self):
		asyncore.loop()

	def sendMove(self, x, y):
		makeMove(board, playerTile, x, y)		
		self.client.sendMove(x, y)

def __init__():
	super(Reversi, self).__init__()

def convertBoard(board):
	for x in range(8):
		for y in range(8):
			try:
				buttonGrid[x][y].setText(board[x][y])
			except:
				pass	

def isValidMove(board, tile, xstart, ystart):
	# Returns False if the player's move on space xstart, ystart is invalid.
	# If it is a valid move, returns a list of spaces that would become the player's if they made a move here.
	if board[xstart][ystart] != ' ' or not isOnBoard(xstart, ystart):
		return False

	board[xstart][ystart] = tile # temporarily set the tile on the board.

	if tile == 'X':
		otherTile = 'O'
	else:
		otherTile = 'X'

	tilesToFlip = []
	for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
		x, y = xstart, ystart
		x += xdirection # first step in the direction
		y += ydirection # first step in the direction
		if isOnBoard(x, y) and board[x][y] == otherTile:
			# There is a piece belonging to the other player next to our piece.
			x += xdirection
			y += ydirection
			if not isOnBoard(x, y):
				continue
			while board[x][y] == otherTile:
				x += xdirection
				y += ydirection
				if not isOnBoard(x, y): # break out of while loop, then continue in for loop
					break
			if not isOnBoard(x, y):
				continue
			if board[x][y] == tile:
				# There are pieces to flip over. Go in the reverse direction until we reach the original space, noting all the tiles along the way.
				while True:
					x -= xdirection
					y -= ydirection
					if x == xstart and y == ystart:
						break
					tilesToFlip.append([x, y])

	board[xstart][ystart] = ' ' # restore the empty space
	if len(tilesToFlip) == 0: # If no tiles were flipped, this is not a valid move.
		return False
	return tilesToFlip


def isOnBoard(x, y):
	# Returns True if the coordinates are located on the board.
	return x >= 0 and x <= 7 and y >= 0 and y <=7

def getValidMoves(board, tile):
	# Returns a list of [x,y] lists of valid moves for the given player on the given board.
	validMoves = []

	for x in range(8):
		for y in range(8):
			if isValidMove(board, tile, x, y) != False:
				validMoves.append([x, y])
	return validMoves


def getScoreOfBoard(board):
	# Determine the score by counting the tiles. Returns a dictionary with keys 'X' and 'O'.
	xscore = 0
	oscore = 0
	for x in range(8):
		for y in range(8):
			if board[x][y] == 'X':
				xscore += 1
			if board[x][y] == 'O':
				oscore += 1
	return {'X':xscore, 'O':oscore}

def enterPlayerTile():
	# the first element in the tuple is the player's tile, the second is the computer's tile.
	#if tile == 'X':
		return ['X', 'O']
	#else:
		#return ['O', 'X']

def makeMove(board, tile, xstart, ystart):
	tilesToFlip = isValidMove(board, tile, xstart, ystart)

	if tilesToFlip == False:
		return False

	#print 'true'
	board[xstart][ystart] = tile
	for x, y in tilesToFlip:
		board[x][y] = tile

	return True

def isOnCorner(x, y):
	# Returns True if the position is in one of the four corners.
	return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)	

def showPoints(board, tile):
	scores = getScoreOfBoard(board)
	if tile == 'X':
		computerTile = 'O'
	else:
		computerTile = 'X'

	w.setWindowTitle('You: %s, Computer: %s' % (scores[tile], scores[computerTile]))

thread = clientThread()

def main():
	#initUI()
	#w = QtGui.QWidget()
	#w.resize(250, 300)
	#w.move(300, 300)
	#w.setWindowTitle('HEHE')
	#w.show()
	#reversi = Reversi()
	playerTile, computerTile = enterPlayerTile()
	
	grid = QtGui.QGridLayout()
	for i in range (0, 8):
		new = []
		for j in range (0, 8):
			button = QtGui.QToolButton()
			button.setMinimumWidth(40)
			button.setMaximumWidth(40)
			QtCore.QObject.connect(button, QtCore.SIGNAL("clicked()"), 
				lambda i=i, j=j: thread.sendMove(i, j))
			new.append(button)
			grid.addWidget(new[j], i, j)
		buttonGrid.append(new)
	
	#computerButton = QtGui.QPushButton('Computer Move')
	horizontialLayout = QtGui.QHBoxLayout()
	resetButton = QtGui.QPushButton('Reset Board')
	#horizontialLayout.addWidget(computerButton)	
	horizontialLayout.addWidget(resetButton)
	QtCore.QObject.connect(resetButton, QtCore.SIGNAL("clicked()"), 
		lambda: resetBoard(board))
	#QtCore.QObject.connect(computerButton, QtCore.SIGNAL("clicked()"),
		#lambda: makeComputerMove(board, computerTile))
	
	horizontialBoxLayout = QtGui.QHBoxLayout()
	verticalBoxLayout = QtGui.QVBoxLayout()
	chatBox = QtGui.QTextEdit()
	enterBox = QtGui.QLineEdit()
	chatLayout = QtGui.QVBoxLayout()
	sendButton = QtGui.QPushButton('Send')
	cancelButton = QtGui.QPushButton('Cancel')

	verticalBoxLayout.addWidget(sendButton)
	verticalBoxLayout.addWidget(cancelButton)

	chatLayout.addWidget(chatBox)
	chatLayout.addWidget(enterBox)

	horizontialBoxLayout.addLayout(chatLayout)
	horizontialBoxLayout.addLayout(verticalBoxLayout)

	mainLayout = QtGui.QVBoxLayout()

	mainLayout.addLayout(grid)
	mainLayout.addLayout(horizontialLayout)
	mainLayout.addLayout(horizontialBoxLayout)
	
	w.setLayout(mainLayout)

	convertBoard(board)
	w.move(300, 150)
	w.setWindowTitle('REVERSI')
	w.show()
	#client = asyncClient('localhost')
	#asyncore.loop()
	#thread = clientThread()
	thread.start()
	sys.exit(app.exec_())
	

if __name__ == '__main__':
	main()
	
