#!/opt/local/bin/python
from __future__ import print_function
import sys
import threading
import socket
import json
from PyQt4 import QtGui, QtCore

showHints = False 
board = []
for i in range(8):
	board.append([' '] * 8)
buttonGrid = []
app = QtGui.QApplication(sys.argv)
w = QtGui.QWidget()
chatBox = QtGui.QTextEdit()


def resetBoard():
	board[3][3] = 'X'
	board[3][4] = 'O'
	board[4][3] = 'O'
	board[4][4] = 'X'
	
resetBoard()

def getRivalTile(tile):
	if tile == 'X':
		return 'O'
	else:
		return 'X'

class clientThread(threading.Thread):

	def __init__(self, host):
		threading.Thread.__init__(self)
		#self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.client.connect( (host, 8888) )
		#self.client.setblocking(0)		
		self.client = socket.create_connection((host, 8888))
		self.buffer = ''
		self.running = True

	def run(self):
		#asyncore.loop()
		while self.running:			
			response = self.client.recv(8192)
			if response:
				print(response)
				decoded = json.loads(response)
				if decoded.get('disconnect'):
					resetBoard()
					convertBoard(board)
					w.setWindowTitle('Waiting...')
				elif decoded.get('tile'):
					self.tile = decoded['tile']
					w.setWindowTitle('You are %s' % self.tile)		
				elif decoded.get('message'):
					#chatBox.html.append('\nrival says: %s' % decoded['message'])
					chatBox.insertPlainText(QtCore.QString('\nrival says: %s' % decoded['message']))
				else:
					x = decoded['x']
					y = decoded['y']
					makeMove(board, getRivalTile(self.tile), x, y)
					convertBoard(board)
					scores = getScoreOfBoard(board)					
					w.setWindowTitle('Your turn, %s. You: %s, Opponent: %s' % (self.tile, scores[self.tile], scores[getRivalTile(self.tile)]))

	def sendMessage(self, text):
		self.client.send(json.dumps({'message' : str(text) }, sort_keys=True, indent=4))
		chatBox.insertPlainText(QtCore.QString('\you say: %s' % text))

	def sendMove(self, x, y):
		if makeMove(board, self.tile, x, y):
			convertBoard(board)			
			scores = getScoreOfBoard(board)	
			result = self.client.send(json.dumps({'x' : x, 'y' : y}, sort_keys=True, indent=4))
			#print('wyjscie %s' % result)
			w.setWindowTitle('%s has turn. You: %s, Opponent: %s' % (getRivalTile(self.tile), scores[self.tile], scores[getRivalTile(self.tile)]))
	
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

def makeMove(board, tile, xstart, ystart):
	tilesToFlip = isValidMove(board, tile, xstart, ystart)

	#print(tilesToFlip)

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

thread = clientThread('localhost')

def main():
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
	
	chatLayout = QtGui.QVBoxLayout()

	enterBox = QtGui.QLineEdit()
	sendButton = QtGui.QPushButton('Send')
	QtCore.QObject.connect(sendButton, QtCore.SIGNAL("clicked()"),
		lambda: thread.sendMessage(enterBox.text()))

	sendBoxLayout = QtGui.QHBoxLayout()
	sendBoxLayout.addWidget(enterBox)
	sendBoxLayout.addWidget(sendButton)

	chatLayout.addWidget(chatBox)
	chatLayout.addLayout(sendBoxLayout)

	mainLayout = QtGui.QVBoxLayout()
	mainLayout.addLayout(grid)
	mainLayout.addLayout(chatLayout)
	
	w.setLayout(mainLayout)

	convertBoard(board)
	#w.move(300, 150)
	w.setWindowTitle('Waiting...')
	w.show()
	thread.daemon = True
	thread.start()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
	
