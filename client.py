#!/usr/bin/env python
import ao
import mad
import readline
import socket
import struct
import sys
import threading
from time import sleep


# global variables 
curr_song = None 
curr_play = False
RECV_BUFFER = 4096


# The Mad audio library we're using expects to be given a file object, but
# we're not dealing with files, we're reading audio data over the network.  We
# use this object to trick it.  All it really wants from the file object is the
# read() method, so we create this wrapper with a read() method for it to
# call, and it won't know the difference.
class mywrapper(object):
    def __init__(self):
        self.mf = None
        self.data = ""

    # When it asks to read a specific size, give it that many bytes, and
    # update our remaining data.
    def read(self, size):
        result = self.data[:size]
        self.data = self.data[size:]
        return result


# Packets can be useful when we would like to acquire some information such as message type
# When sending info over to the server, the packet has to be stringified
# These strings can then be decoded back to packets   
class Packet:
    def __init__(self, msg_type = None, song_id = None):
        self.msg_type = msg_type 
        self.sid = song_id 
        self.data = None 
        self.str_packet = None 
    
    # encode string to send to server
    def encode_to_string(self): 
        if self.msg_type == 'play':
            self.str_packet = self.msg_type + '<NEXT;>' + self.sid + '<NEXT;>' + '<END;>'
        elif self.msg_type == 'list':
            self.str_packet = self.msg_type + '<NEXT;>' + '<END;>'
        else:
            self.str_packet = self.msg_type + '<NEXT;>' + '<END;>'

    # decode packet received from client 
    def decode_to_packet(self, encoded_string): 
        decoding = encoded_string.split('<NEXT;>')
        if decoding[0] == 'stop':
            self.msg_type = decoding[0]
        else:
            self.msg_type, self.data = decoding[0], decoding[1]


# send over packets to server 
def send_packet(packet, sock, msg_type): 
    packet.encode_to_string()
    try: 
        sock.sendall(packet.str_packet)
    except:
        print 'Error sending ' + msg_type + ' command to server'


# stop playing current song if playing 
def stop_play(wrap, cond_filled):
    cond_filled.acquire()
    wrap.data = ""
    cond_filled.release()


# Receive messages.  If they're responses to info/list, print
# the results for the user to see.  If they contain song data, the
# data needs to be added to the wrapper object.  Be sure to protect
# the wrapper with synchronization, since the other thread is using
# it too!
def recv_thread_func(wrap, cond_filled, sock):
    while True:
        message = sock.recv(RECV_BUFFER)
        
        if message == None:
            continue 

        p = Packet()
        p.decode_to_packet(message)
        p.sid = curr_song 

        if p.msg_type == 'stop':
            continue 

        elif p.msg_type == 'list':
            print str(p.data)      
        
        elif p.msg_type == 'play':
            cond_filled.acquire()
            if curr_play == True:
                wrap.data += p.data
            cond_filled.release()
        
        cond_filled.acquire()

        if wrap.mf is None:
            wrap.mf = mad.MadFile(wrap)

        cond_filled.release()  
        
        
# If there is song data stored in the wrapper object, play it!
# Otherwise, wait until there is.  Be sure to protect your accesses
# to the wrapper with synchronization, since the other thread is
# using it too!
def play_thread_func(wrap, cond_filled, dev):
    while True:
        """
        example usage of dev and wrap (see mp3-example.py for a full example):
        buf = wrap.mf.read()
        dev.play(buffer(buf), len(buf))
        """
        if wrap.mf:
            cond_filled.acquire()
            buf = wrap.mf.read()
            cond_filled.release()
            if buf and curr_play:
                dev.play(buffer(buf), len(buf))

def main():
    if len(sys.argv) < 3:
        print 'Usage: %s <server name/ip> <server port>' % sys.argv[0]
        sys.exit(1)

    # Create a pseudo-file wrapper, condition variable, and socket.  These will
    # be passed to the thread we're about to create.
    wrap = mywrapper()

    global curr_song 
    global curr_play 

    # Create a condition variable to synchronize the receiver and player threads.
    # In python, this implicitly creates a mutex lock too.
    # See: https://docs.python.org/2/library/threading.html#condition-objects
    cond_filled = threading.Condition()

    # Create a TCP socket and try connecting to the server.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((sys.argv[1], int(sys.argv[2])))

    # Create a thread whose job is to receive messages from the server.
    recv_thread = threading.Thread(
        target=recv_thread_func,
        args=(wrap, cond_filled, sock)
    )
    recv_thread.daemon = True
    recv_thread.start()

    # Create a thread whose job is to play audio file data.
    dev = ao.AudioDevice('pulse')
    play_thread = threading.Thread(
        target=play_thread_func,
        args=(wrap, cond_filled, dev)
    )
    play_thread.daemon = True
    play_thread.start()

    # Enter our never-ending user I/O loop.  Because we imported the readline
    # module above, raw_input gives us nice shell-like behavior (up-arrow to
    # go backwards, etc.).
    while True:
        line = raw_input('>> ')

        if ' ' in line:
            cmd, args = line.split(' ', 1)
        else:
            cmd, args = line, None 

        if cmd in ['l', 'list']:
            print 'The user asked for list.'
            p = Packet(msg_type = 'list')
            send_packet(p, sock, 'list')

        elif cmd in ['p', 'play']:
            if args == None or unicode(args).isnumeric() == False: 
                print 'Please enter a song ID number to play'
                continue 
            print 'The user asked to play:', args

            # stop playing the current song before playing a new song 
            curr_song = None 
            curr_play = False 
            p = Packet(msg_type = 'stop')
            send_packet(p, sock, 'stop')
            stop_play(wrap, cond_filled)
            sleep(1)

            # now send play packet 
            curr_song = args 
            curr_play = True 
            p = Packet(msg_type = 'play', song_id = args)
            send_packet(p, sock, 'play')

        elif cmd in ['s', 'stop']:
            print 'The user asked to stop.'
            curr_song = None 
            curr_play = False 
            p = Packet(msg_type = 'stop')
            send_packet(p, sock, 'stop')
            stop_play(wrap, cond_filled)

        elif cmd in ['quit', 'q', 'exit']:
            print 'The user asked to quit.'
            p = Packet(msg_type = 'quit')
            send_packet(p, sock, 'quit')
            sys.exit(0)
        
        else: 
            print 'Please input a valid command'


if __name__ == '__main__':
    main()
