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

class Packet:
    def __init__(self, msg_type = None, song_id = None, str_packet = None, data = "<NO DATA>"):
        self.msg_type = msg_type 
        self.sid = song_id 
        self.data = data 
        self.str_packet = str_packet 
    
    def encode_to_string(self): 
        if self.msg_type == 'play':
            self.str_packet = self.msg_type + '<NEXT;>' + self.sid + '<NEXT;>' + self.data + '<NEXT;>' + '<END;>'
        else:
            self.str_packet = self.msg_type + '<NEXT;>' + '<END;>'

    def decode_to_packet(self, encoded_string): 
        decoding = encoded_string.split('<NEXT;>')[:-1]
        if len(decoding) == 1:
            self.msg_type = decoding[0]
        elif len(decoding) == 3:
            self.msg_type, self.sid, self.data = decoding[0], decoding[1], decoding[2] 

# Thread that sends music and lists to the client.  All send() calls
# should be contained in this function.  Control signals from client_read could
# be passed to this thread through the associated Client object.  Make sure you
# use locks or similar synchronization tools to ensure that the two threads play
# nice with one another!
def client_write(client):
    while True:
        if len(client.packet_queue) > 0:
            client.lock.acquire()
            packet = client.packet_queue.popleft()
            client.lock.release()

            if packet.msg_type == 'stop':
                packet.encode_to_string()
                try: 
                    client.conn.sendall(packet.str_packet)
                except:
                    print 'Error sending stop response to client'
            
            elif packet.msg_type == 'list':
                pass 

            elif packet.msg_type == 'play':
                pass







# Thread that receives commands from the client.  All recv() calls should
# be contained in this function.
def client_read(client):
    while True:
        recv_msg = client.conn.recv(SEND_BUFFER)
        p = Packet()
        p.decode_to_packet(recv_msg)

        # queue the packets to be accessed in client_write
        if p.msg_type == 'stop':
            client.lock.acquire()
            print 'User asked to stop'
            client.packet_queue.append(p)
            client.lock.release()  

        elif p.msg_type == 'list':
            client.lock.acquire()
            print 'User asked for list'
            client.packet_queue.append(p)
            client.lock.release() 

        elif p.msg_type == 'play':
            client.lock.acquire()
            print 'User asked to play'
            if int(p.sid) >= len(client.songlist):
                print 'Client requested an invalid song id'
                client.lock.release() 
                continue 
            # update client's current song playing 
            # add data to this client 
            client.packet_queue.append(p)
            client.curr_song = p.sid 
            client.lock.release() 
        
        elif p.msg_type == 'quit':
            client.lock.acquire()
            client.conn.close()
            client.lock.release()  
            break 


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

