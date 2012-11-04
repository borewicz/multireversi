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

def returnName(tile):
	if tile == 'X':
		return 'White'
	else:
		return 'Black'


class clientThread(threading.Thread):

	def __init__(self, host, nick):
		threading.Thread.__init__(self)
		self._stop = threading.Event()		
		#self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.client.connect( (host, 8888) )
		#self.client.setblocking(0)		
		self.client = socket.create_connection((host, 8888))
		self.buffer = ''
		if nick != '':
			self.nick = nick
		else:
			self.nick = 'anon'
		#self.rival = 'unknown'
		self.running = True
		self.chatBox = QtGui.QTextEdit()		
		self.chatBox.setReadOnly(True)
		self.enterBox = QtGui.QLineEdit()
		self.blackLabel = QtGui.QLabel('2')
		self.whiteLabel = QtGui.QLabel('2')
		self.window = self.createWindow()				
		startWindow.hide()
		self.window.show()

	def convertBoard(self, board):
		for x in range(8):
			for y in range(8):
				try:				
					if board[x][y] == 'X':
						buttonGrid[x][y].setIcon(QtGui.QIcon('white.png'))
					elif board[x][y] == 'O':
						buttonGrid[x][y].setIcon(QtGui.QIcon('black.png'))
					else:
						buttonGrid[x][y].setIcon(QtGui.QIcon('null.png'))
				except:
					pass	

	def setEnabled(self, enabled):
		for x in range(8):
			for y in range(8):
				buttonGrid[x][y].setEnabled(enabled)

	def createWindow(self):
		#convertBoard(board)
		w = QtGui.QWidget()	
		p = QtGui.QPalette()
		p.setColor(QtGui.QPalette.Background, QtGui.QColor(0, 100, 0, 127))	
		#w.setAutoFillBackground(True);
		w.setPalette(p);
		
		#w.setStyleSheet('background-color:green;')	
		grid = QtGui.QGridLayout()
		#grid.setEnabled(False)
		grid.setSpacing(0)
		#grid.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		for i in range (0, 8):
			new = []
			for j in range (0, 8):
				button = QtGui.QPushButton()
				button.setMinimumSize(46, 46)
				button.setMaximumSize(46, 46)
				button.setFlat(True)
				button.setEnabled(False)
				button.setAutoFillBackground(True);
				button.setIcon(QtGui.QIcon('null.png'));
				button.setIconSize(QtCore.QSize(46, 46));
				button.setStyleSheet(""
						 "background-repeat: no-repeat;"
						 "background-position: center center");
				

				QtCore.QObject.connect(button, QtCore.SIGNAL("clicked()"), 
					lambda i=i, j=j: self.sendMove(i, j))
				new.append(button)
				grid.addWidget(new[j], i, j)
			buttonGrid.append(new)
		
		colorPalette = QtGui.QPalette()
		#colorPalette.setColor(QtGui.QPalette.Background, QtGui.QColor(50, 68, 43, 0))
		
		whitePointLayout = QtGui.QHBoxLayout()
		#whitePointLayout.setSpacing(0)
		
		whiteIcon = QtGui.QLabel()
		whiteIcon.setPixmap(QtGui.QPixmap('white_small.png'))
		whiteIcon.setGeometry(QtCore.QRect(0, 0, 20, 20))	

		policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		#policy.setHeightForWidth(True)
		#policy.setWidthForHeight(True)
		policy.setHorizontalStretch(0)
		policy.setVerticalStretch(0)
		policy.setHeightForWidth(whiteIcon.sizePolicy().hasHeightForWidth())

		#self.whiteLabel.setGeometry(QtCore.QRect(0, 0, 50, 20))
		#self.whiteLabel.setPalette(colorPalette)
		#self.whiteLabel.setAutoFillBackground(True);

		whitePointLayout.addWidget(whiteIcon)
		whitePointLayout.addWidget(self.whiteLabel)

		blackPointLayout = QtGui.QHBoxLayout()
		
		blackIcon = QtGui.QLabel()		
		blackIcon.setPixmap(QtGui.QPixmap('black_small.png'))
		blackIcon.setGeometry(QtCore.QRect(0, 0, 20, 20))

		whiteIcon.setSizePolicy(policy)		
		blackIcon.setSizePolicy(policy)		
		#blackLabel = QtGui.QLabel('0')

		#self.blackLabel.setGeometry(QtCore.QRect(0, 0, 50, 20))
		#self.blackLabel.setPalette(colorPalette)
		#self.blackLabel.setAutoFillBackground(True);		

		blackPointLayout.addWidget(blackIcon)
		blackPointLayout.addWidget(self.blackLabel)

		#self.whiteLabel.setGeometry(QtCore.QRect(0, 0, 50, 20))
		
		pointsLayout = QtGui.QHBoxLayout()
        
		pointsLayout.setContentsMargins(100, 0, 100, 0)	
		#pointsLayout.addWidget(whiteFrame)
		#pointsLayout.addWidget(blackFrame)
		pointsLayout.addLayout(whitePointLayout)
		pointsLayout.addLayout(blackPointLayout)

		self.blackLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.whiteLabel.setAlignment(QtCore.Qt.AlignCenter)

		chatLayout = QtGui.QVBoxLayout()

		#enterBox = QtGui.QLineEdit()
		sendButton = QtGui.QPushButton('Send')
		QtCore.QObject.connect(sendButton, QtCore.SIGNAL("clicked()"),
			lambda: self.sendMessage(self.enterBox.text()))
		#QtCore.QObject.connect(self.enterBox, QtCore.SIGNAL("returnPressed()"), sendButton, QtCore.SIGNAL("clicked()"))
		QtCore.QObject.connect(self.enterBox, QtCore.SIGNAL("returnPressed()"),
			lambda: self.sendMessage(self.enterBox.text()))

		sendBoxLayout = QtGui.QHBoxLayout()
		sendBoxLayout.addWidget(self.enterBox)
		#sendBoxLayout.addWidget(sendButton)

		chatLayout.setSpacing(5)
		chatLayout.addWidget(self.chatBox)
		chatLayout.addLayout(sendBoxLayout)

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addLayout(grid)
		mainLayout.addLayout(pointsLayout)
		mainLayout.addLayout(chatLayout)
		
		self.convertBoard(board)
		
		w.setWindowTitle('Reversi')	
		w.setLayout(mainLayout)
		return w

	def run(self):
		#asyncore.loop()
		while self.running:			
			response = self.client.recv(1024)
			if response:
				print(response)
				decoded = json.loads(response)
				if decoded.get('disconnect'):
					resetBoard()
					self.convertBoard(board)
					#.setWindowTitle('Waiting...')
					#w.hide()
					startWindow.show()
					self._stop.set()					
				elif decoded.get('tile'):
					self.tile = decoded['tile']
					#self.window.setWindowTitle('You are %s' % self.tile)
					if self.tile == 'X':
						self.setEnabled(True)
					else:
						self.setEnabled(False)
					self.chatBox.insertPlainText(QtCore.QString('You are %s.\n' % returnName(self.tile)))
				elif decoded.get('message'):
					self.chatBox.insertPlainText(QtCore.QString('%s: %s\n' % (decoded['nick'], decoded['message'])))
					cursor = self.chatBox.textCursor()
					cursor.movePosition(QtGui.QTextCursor.End)
					self.chatBox.setTextCursor(cursor)
				else:
					x = decoded['x']
					y = decoded['y']
					makeMove(board, getRivalTile(self.tile), x, y)
					self.convertBoard(board)
					scores = getScoreOfBoard(board)					
					self.blackLabel.setText(str(scores['O']))
					self.whiteLabel.setText(str(scores['X']))

					#self.window.setWindowTitle('You: %s, Opponent: %s' % (scores[self.tile], scores[getRivalTile(self.tile)]))
					self.setEnabled(True)

	def sendMessage(self, text):
		self.client.send(json.dumps({'message' : unicode(text), 'nick' : self.nick }, sort_keys=True, indent=4))
		self.chatBox.insertPlainText(QtCore.QString('%s: %s\n' % (self.nick, text)))
		cursor = self.chatBox.textCursor()
		cursor.movePosition(QtGui.QTextCursor.End)
		self.chatBox.setTextCursor(cursor)
		self.enterBox.clear()

	def sendMove(self, x, y):
		if makeMove(board, self.tile, x, y):
			self.convertBoard(board)			
			scores = getScoreOfBoard(board)	
			result = self.client.sendall(json.dumps({'x' : x, 'y' : y}, sort_keys=True, indent=4))
			#self.window.setWindowTitle('You: %s, Opponent: %s' % (scores[self.tile], scores[getRivalTile(self.tile)]))
			self.blackLabel.setText(str(scores['O']))
			self.whiteLabel.setText(str(scores['X']))
			self.setEnabled(False)
			
	
def __init__():
	super(Reversi, self).__init__()



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
				lambda: createThread(unicode(nickBox.text())))

	QtCore.QObject.connect(nickBox, QtCore.SIGNAL("returnPressed()"), connectButton, QtCore.SIGNAL("clicked()"))	
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
	
