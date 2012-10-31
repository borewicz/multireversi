#!/opt/local/bin/python
from __future__ import print_function
#import asyncore
import socket
import json
import sys
import random
#import time
import threading
#import SocketServer

clients = []
playerTile = 'X'
computerTile = 'O'

class gameServer(object):

	def __init__(self, host, port):
		print('gameServer init')
		try:
			self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.server.bind((host, port))
			self.server.listen(5)
			self.running = True
			while self.running:
				try:
					client = self.server.accept()
					thread = clientThread(client[0])
					#thread.daemon = True
					clients.append(thread)
					thread.start()
				except KeyboardInterrupt:
					print('parent received control-c')
					self.server.close()
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
		self._stop = threading.Event()				

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
			self.haveRival = True
			self.rivalID = clients.index(pindol)						
			clients[self.rivalID].haveRival = True
			clients[self.rivalID].rivalID = clients.index(self)
			#pindol.haveRival = True				
			#self.rival = pindol.sock
			#print(pindol.sock.getpeername())
			#print(self.sock.getpeername())
			#pindol.rival = self.sock
			self.tile = random.choice([computerTile, playerTile])
			clients[self.rivalID].tile = self.getRivalTile(self.tile)
			clients[self.rivalID].sock.send(json.dumps({'tile' : self.tile}, sort_keys=True, indent=4))	
			self.sock.send(json.dumps({'tile' : clients[self.rivalID].tile}, sort_keys=True, indent=4))
			print('found rival')
			return True
		else: return False
	
	def run(self):
		while self.running:
			if self.findPindol():
				data = self.sock.recv(1024)
				if data:
					print(data)
					sent = clients[self.rivalID].sock.send(data)
					if sent == 0:
						raise RuntimeError("socket connection broken, error: %s" % str(sent))

				else:
					#self.rival.send(json.dumps({'disconnect' : 'true'}, sort_keys=True, indent=4))
					self.sock.close()
					#clients[self.rivalID].sock.close()
					print('closing socket')
					self.running = False
					self._stop.set()
					for c in clients:
						if self.sock == c.sock:
							clients.remove(c)
					del self
					return
					

server = gameServer('localhost', 8888)

