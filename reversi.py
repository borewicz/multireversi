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
startWindow = QtGui.QWidget()
#chatBox = QtGui.QTextEdit()
nick = 'unknown'

def resetBoard():
	for i in range(8):
		for j in range(8):
			board[i][j] = ' '
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

	def __init__(self, host, nick):
		threading.Thread.__init__(self)
		self._stop = threading.Event()		
		#self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.client.connect( (host, 8888) )
		#self.client.setblocking(0)		
		self.client = socket.create_connection((host, 8888))
		self.buffer = ''
		self.nick = nick
		#self.rival = 'unknown'
		self.running = True
		self.chatBox = QtGui.QTextEdit()		
		self.window = self.createWindow()
		startWindow.hide()
		self.window.show()

	def createWindow(self):
		#convertBoard(board)
		w = QtGui.QWidget()	
		grid = QtGui.QGridLayout()
		for i in range (0, 8):
			new = []
			for j in range (0, 8):
				button = QtGui.QToolButton()
				button.setMinimumWidth(40)
				button.setMaximumWidth(40)
				QtCore.QObject.connect(button, QtCore.SIGNAL("clicked()"), 
					lambda i=i, j=j: self.sendMove(i, j))
				new.append(button)
				grid.addWidget(new[j], i, j)
			buttonGrid.append(new)
		
		chatLayout = QtGui.QVBoxLayout()

		enterBox = QtGui.QLineEdit()
		sendButton = QtGui.QPushButton('Send')
		QtCore.QObject.connect(sendButton, QtCore.SIGNAL("clicked()"),
			lambda: self.sendMessage(enterBox.text()))

		sendBoxLayout = QtGui.QHBoxLayout()
		sendBoxLayout.addWidget(enterBox)
		sendBoxLayout.addWidget(sendButton)

		chatLayout.addWidget(self.chatBox)
		chatLayout.addLayout(sendBoxLayout)

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addLayout(grid)
		mainLayout.addLayout(chatLayout)
		
		convertBoard(board)
		
		w.setWindowTitle('Waiting...')	
		w.setLayout(mainLayout)
		return w

	def run(self):
		#asyncore.loop()
		#self.client.send(json.dumps({'nick' : str(self.nick) }, sort_keys=True, indent=4))		
		while self.running:			
			response = self.client.recv(1024)
			if response:
				print(response)
				decoded = json.loads(response)
				if decoded.get('disconnect'):
					resetBoard()
					convertBoard(board)
					#.setWindowTitle('Waiting...')
					#w.hide()
					startWindow.show()
					self._stop.set()					
				elif decoded.get('tile'):
					self.tile = decoded['tile']
					self.window.setWindowTitle('You are %s' % self.tile)		
				elif decoded.get('message'):
					#chatBox.html.append('\nrival says: %s' % decoded['message'])
					self.chatBox.insertPlainText(QtCore.QString('%s: %s\n' % (decoded['nick'], decoded['message'])))
				#elif decoded.get('nick'):
					#self.rival = decoded['nick']
				else:
					x = decoded['x']
					y = decoded['y']
					makeMove(board, getRivalTile(self.tile), x, y)
					convertBoard(board)
					scores = getScoreOfBoard(board)					
					self.window.setWindowTitle('Your turn, %s. You: %s, Opponent: %s' % (self.tile, scores[self.tile], scores[getRivalTile(self.tile)]))
			else:
				self.sock.close()
				self.running = False
				self._stop.set()
				del self
				return

	def sendMessage(self, text):
		self.client.send(json.dumps({'message' : str(text), 'nick' : self.nick }, sort_keys=True, indent=4))
		self.chatBox.insertPlainText(QtCore.QString('%s: %s\n' % (self.nick, text)))

	def sendMove(self, x, y):
		if makeMove(board, self.tile, x, y):
			convertBoard(board)			
			scores = getScoreOfBoard(board)	
			result = self.client.sendall(json.dumps({'x' : x, 'y' : y}, sort_keys=True, indent=4))
			self.window.setWindowTitle('%s has turn. You: %s, Opponent: %s' % (getRivalTile(self.tile), scores[self.tile], scores[getRivalTile(self.tile)]))
	
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
	if board[xstart][ystart] != ' ' or not isOnBoard(xstart, ystart):
		return False

	board[xstart][ystart] = tile 

	if tile == 'X':
		otherTile = 'O'
	else:
		otherTile = 'X'

	tilesToFlip = []
	for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
		x, y = xstart, ystart
		x += xdirection
		y += ydirection 
		if isOnBoard(x, y) and board[x][y] == otherTile:
			x += xdirection
			y += ydirection
			if not isOnBoard(x, y):
				continue
			while board[x][y] == otherTile:
				x += xdirection
				y += ydirection
				if not isOnBoard(x, y): 
					break
			if not isOnBoard(x, y):
				continue
			if board[x][y] == tile:
				while True:
					x -= xdirection
					y -= ydirection
					if x == xstart and y == ystart:
						break
					tilesToFlip.append([x, y])

	board[xstart][ystart] = ' ' 
	if len(tilesToFlip) == 0: 
		return False
	return tilesToFlip


def isOnBoard(x, y):
	return x >= 0 and x <= 7 and y >= 0 and y <=7

def getValidMoves(board, tile):
	validMoves = []

	for x in range(8):
		for y in range(8):
			if isValidMove(board, tile, x, y) != False:
				validMoves.append([x, y])
	return validMoves


def getScoreOfBoard(board):
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

	if tilesToFlip == False:
		return False

	board[xstart][ystart] = tile
	for x, y in tilesToFlip:
		board[x][y] = tile

	return True

def isOnCorner(x, y):
	return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)	

def createThread(nick):
	thread = clientThread('localhost', nick)
	thread.daemon = True
	thread.start()

def showSplash():
	nickLabel = QtGui.QLabel('Nickname:')
	nickBox = QtGui.QLineEdit()
	connectButton = QtGui.QPushButton('Connect')
	QtCore.QObject.connect(connectButton, QtCore.SIGNAL("clicked()"), 
				lambda: createThread(str(nickBox.text())))
	dialogLayout = QtGui.QHBoxLayout()
	dialogLayout.addWidget(nickLabel)
	dialogLayout.addWidget(nickBox)
	
	mainDialogLayout = QtGui.QVBoxLayout()
	mainDialogLayout.addLayout(dialogLayout)
	mainDialogLayout.addWidget(connectButton)

	startWindow.setLayout(mainDialogLayout)

def main():
	showSplash()
	startWindow.show()		
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
	
