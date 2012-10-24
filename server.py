#!/opt/local/bin/python
from __future__ import print_function
import asyncore
import socket
import json
import sys
import random
import time
import threading
import SocketServer

clients = []
board = []
for i in range(8):
	board.append([' '] * 8)
board[3][3] = 'X'
board[3][4] = 'O'
board[4][3] = 'O'
board[4][4] = 'X'
playerTile = 'X'
computerTile = 'O'

clients = []

class gameServer(object):

	def __init__(self, host, port):
		print('gameServer init')
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.bind((host, port))
			self.server.listen(1)
			self.running = True
			while self.running:
				try:
					client = self.server.accept()
					thread = clientThread(client[0])
					thread.daemon = True
					clients.append(thread)
					thread.start()
				except KeyboardInterrupt:
					print('parent received control-c')
					self.running = False
		except socket.error, (value,message): 
			if self.server: 
				self.server.close() 
			print ("Could not open socket: " + message)
				
class clientThread(threading.Thread):

	def __init__(self, sock):
		threading.Thread.__init__(self)
		self.sock = sock
		self.haveRival = False
		self.running = True

	def getRivalTile(self, tile):
		if tile == 'X':
			return 'O'
		else:
			return 'X'

	def findPindol(self):
		if self.haveRival == True: 
			#print('already have rival')
			return True
		#pindol = random.choice(clients)
		if len(clients) >= 2:
			pindol = random.choice(clients)
			while (pindol.haveRival == True) or (pindol.sock == self.sock):
				pindol = random.choice(clients)
			self.rival = pindol.sock
			print(pindol.sock.getpeername())
			print(self.sock.getpeername())
			self.haveRival = True
			pindol.rival = self.sock
			pindol.haveRival = True
			self.tile = random.choice([computerTile, playerTile])
			pindol.tile = self.getRivalTile(self.tile)
			pindol.sock.send(json.dumps({'tile' : self.tile}, sort_keys=True, indent=4))	
			self.sock.send(json.dumps({'tile' : pindol.tile}, sort_keys=True, indent=4))
			print('found rival')
			return True
		else: return False
	
	def run(self):
		#self.findPindol()
		print("beginning client thread loop")	
		#if self.findPindol():
		#print(self.sock.getpeername())
		#if self.findPindol():		
		while self.running:
			if self.findPindol():
				data = self.sock.recv(1024)
				if data:
					print(data)
					self.rival.send(data)
				else:
					self.sock.close()
					print('closing socket')
					self.running = False


###############
# old handler
###############

class gameHandler(asyncore.dispatcher_with_send):

	def handle_read(self):
		data = self.recv(8192)
		print(data)
		if data != '':
			decoded = json.loads(data)
			print(decoded['x'])
			print(decoded['y'])
			makeMove(board, playerTile, decoded['x'], decoded['y'])
			x, y = getComputerMove(board, computerTile)
			makeMove(board, computerTile, x, y)			
			print(json.dumps({'x' : x, 'y' : y}, sort_keys=True, indent=4))
			self.send(json.dumps({'x' : x, 'y' : y}, sort_keys=True, indent=4))

	def handle_write(self):
		sent = self.send('siema')
		#to anuluje dalsze wysylanie w loopie
		self.buffer = self.buffer[sent:]

#class gameServer(asyncore.dispatcher):
#
	#def __init__(self, host, port):
		#asyncore.dispatcher.__init__(self)
		#self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		#self.set_reuse_addr()
		#self.bind((host, port))
		#self.listen(5)
#
	#def handle_accept(self):
		##adding client to clients list
		#client = self.accept()
		##if client is None:
			##pass
		#else:
			#clients.append(clientObject(client))
			#data = sock.recv(8192)
			#print(data)
			#print(client[0])
			#handler = gameHandler(sock)
	
	#def handle_close(self):
		#self.close()
		
def resetBoard(board):
	# Blanks out the board it is passed, except for the original starting position.
	for x in range(8):
		for y in range(8):
			board[x][y] = ' '

	# Starting pieces:
	board[3][3] = 'X'
	board[3][4] = 'O'
	board[4][3] = 'O'
	board[4][4] = 'X'

def getNewBoard():
	# Creates a brand new, blank board data structure.
	board = []
	for i in range(8):
		board.append([' '] * 8)

	return board

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


def getBoardWithValidMoves(board, tile):
	# Returns a new board with . marking the valid moves the given player can make.
	dupeBoard = getBoardCopy(board)

	for x, y in getValidMoves(dupeBoard, tile):
		dupeBoard[x][y] = '.'
	return dupeBoard


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
	#if tile == 'X':
		return ['X', 'O']
	#else:
		#return ['O', 'X']

def makeMove(board, tile, xstart, ystart):
	tilesToFlip = isValidMove(board, tile, xstart, ystart)

	if tilesToFlip == False:
		return False

	board[xstart][ystart] = tile
	for x, y in tilesToFlip:
		board[x][y] = tile

	return True

def getBoardCopy(board):
	dupeBoard = getNewBoard()

	for x in range(8):
		for y in range(8):
			dupeBoard[x][y] = board[x][y]

	return dupeBoard


def isOnCorner(x, y):
	# Returns True if the position is in one of the four corners.
	return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)	

def getComputerMove(board, computerTile):
	possibleMoves = getValidMoves(board, computerTile)

	random.shuffle(possibleMoves)

	for x, y in possibleMoves:
		if isOnCorner(x, y):
			return [x, y]

	bestScore = -1
	for x, y in possibleMoves:
		dupeBoard = getBoardCopy(board)
		makeMove(dupeBoard, computerTile, x, y)
		score = getScoreOfBoard(dupeBoard)[computerTile]
		if score > bestScore:
			bestMove = [x, y]
			bestScore = score
	return bestMove

board = getNewBoard()
resetBoard(board)

server = gameServer('localhost', 8888)
