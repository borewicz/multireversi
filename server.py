#!/opt/local/bin/python
#reversi-servers
from __future__ import print_function
import asyncore
import socket
import json
import random
import time

#test svn

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

class gameHandler(asyncore.dispatcher_with_send):

	def handle_read(self):
		data = self.recv(8192)
		#print(data)
		if data != '':
			decoded = json.loads(data)
			print(decoded['x'])
			print(decoded['y'])
			for y in range(8):
				print('%s|' % (y+1), end='')
				for x in range(8):
					print(board[x][y], end='')
				print('|')
			makeMove(board, playerTile, decoded['x'], decoded['y'])
			x, y = getComputerMove(board, computerTile)
			makeMove(board, computerTile, x, y)			
			print('wait for server')
			time.sleep(5)
			print(json.dumps({'x' : x, 'y' : y}, sort_keys=True, indent=4))
			self.send(json.dumps({'x' : x, 'y' : y}, sort_keys=True, indent=4))

	def handle_write(self):
		sent = self.send('siema')
		#to anuluje dalsze wysylanie w loopie
		self.buffer = self.buffer[sent:]


class gameServer(asyncore.dispatcher):

	def __init__(self, host, port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind((host, port))
		self.listen(5)

	def handle_accept(self):
		pair = self.accept()
		if pair is None:
			pass
		else:
			sock, addr = pair
			clients.append(sock)
			#print 'Incoming connection from %s' % repr(addr)
			#print clients[0].getpeername()
			#print(sock.recv(8192))
			#data = sock.recv(8192)
			#print(data)
			for x in range(len(clients)):
				ipaddr, port = clients[x].getpeername()
				if ipaddr == '127.0.0.1':
					print(x)
				print('%s %s' % (ipaddr, port))
			#sock.send(json.dumps({'address' : addr}, sort_keys=True, indent=4))
			handler = gameHandler(sock)
	
	def handle_close(self):
		self.close()
	
class clientObject(object)
	
	def __init__(self, clientInfo):
		self.sock = clientInfo[0]
		self.address = clientInfo[1]
		
	def send(self, x, y)
		self.sock.send(json.dumps({'x' : x, 'y' : y}, sort_keys=True, indent=4))
		
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
asyncore.loop()


