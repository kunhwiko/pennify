#!/usr/bin/env python

import os
import socket
import struct
import sys
from threading import Lock, Thread
from collections import deque 


QUEUE_LENGTH = 10
SEND_BUFFER = 4096

# per-client struct
class Client:
    def __init__(self, conn, addr, songlist):
        self.lock = Lock()
        self.conn = conn 
        self.addr = addr 
        self.songlist = songlist        # has the list of songs in the music directory 
        self.curr_song = None           # current song the instance of the client is playing 
        self.packet_queue = deque()     # queue for packets from this client 
        self.buffer = ""                # buffer with the song data 

class Packet:
    def __init__(self, msg_type, song_id = None, str_packet = None):
        self.msg_type = msg_type 
        self.sid = song_id 
        self.str_packet = str_packet 
    
    def encode_to_string(self): 
        if self.msg_type == 'play':
            self.str_packet = self.msg_type + '<NEXT;>' + self.sid + '<NEXT;>' + '<END;>'
        else:
            self.str_packet = self.msg_type + '<NEXT;>' + '<END;>'

    def decode_to_packet(self, encoded_string): 
        decoding = encoded_string.split('<NEXT;>')[:-1]
        if len(decoding) == 1:
            self.msg_type = decoding 
        elif len(decoding) == 2:
            self.msg_type, self.sid = decoding[0], decoding[1] 


# TODO: Thread that sends music and lists to the client.  All send() calls
# should be contained in this function.  Control signals from client_read could
# be passed to this thread through the associated Client object.  Make sure you
# use locks or similar synchronization tools to ensure that the two threads play
# nice with one another!
def client_write(client):
    pass 




# Thread that receives commands from the client.  All recv() calls should
# be contained in this function.
def client_read(client):
    recv_msg = client.conn.recv(SEND_BUFFER)
    p = Packet()
    p.decode_to_packet(recv_msg)
    while recv_msg:
        client.lock.acquire()

        # queue the packets to be accessed in client_write
        if p.msg_type == 'stop':
            print 'User asked to stop'
            client.packet_queue.append(p)  

        elif p.msg_type == 'list':
            print 'User asked for list'
            client.packet_queue.append(p)

        elif p.msg_type == 'play':
            print 'User asked to play'
            if int(p.sid) >= len(client.songlist):
                print 'Client requested an invalid song id'
                continue 
            # update client's current song playing 
            # add data to this client 
            client.curr_song = p.sid 
            with open('music/' + client.songlist[p.sid-1], 'r') as f:
                client.buffer = f.read()
        
        elif p.msg_type == 'quit':
            client.conn.close()

        client.lock.release()





def get_mp3s(musicdir):
    print("Reading music files...")
    songs = []

    for filename in os.listdir(musicdir):
        if not filename.endswith(".mp3"):
            continue
        songs.append(filename)
    return songs 

    print("Found {0} song(s)!".format(len(songs)))

def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python server.py [port] [musicdir]")
    if not os.path.isdir(sys.argv[2]):
        sys.exit("Directory '{0}' does not exist".format(sys.argv[2]))

    port = int(sys.argv[1])
    songlist = get_mp3s(sys.argv[2])
    threads = []

    # create a socket and accept incoming connections 
    # references: https://realpython.com/python-sockets/
    # references: https://stackoverflow.com/questions/30888397/how-to-set-send-buffer-size-for-sockets-in-python
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SEND_BUFFER)
    s.bind(('127.0.0.1', port))
    s.listen(QUEUE_LENGTH)

    while True:
        conn, addr = s.accept()
        client = Client(conn, addr, songlist)
        t = Thread(target=client_read, args=(client))
        threads.append(t)
        t.start()
        t = Thread(target=client_write, args=(client))
        threads.append(t)
        t.start()
    s.close()


if __name__ == "__main__":
    main()

