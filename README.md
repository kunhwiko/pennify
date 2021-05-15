# Introduction

The design and the implementation of this protocol informs users the concerns behind constructing different protocols for streaming services. Common constraints that are involved are header and message formats, proper framing of messages, and the behavior between the client and server in response to a message. 

# Setup

Environment:

Note that the server and client run on Python 2, and your environment must be able to handle the imports in this program. In our case, a virtual machine (Vagrant) was used to handle such an environment. 

Although the original application uses an EC2 instance to host the server to handle scalability, **here we help to set up the server locally**. Feel free to set the server inside an EC2 instance to duplicate our results. 

Open up a terminal and type the following to spin up the server:  

```bash
python server.py 8080 music
``` 

In a separate terminal, spin up a client instance: 

```bash
python client.py 127.0.0.1 8080
```

If this fails to work, locate line 168 on the `server.py` file and replace it with the following code:

```python
s.bind(("127.0.0.1", port))
```

# Messages

## Message Types

Similar to an RTSP protocol, the program must be able to handle the following commands: 

Client requests:\

  - list : request the list of songs existing in the server and their ID number\

  - play (song id) : request to play a certain song, a song id must be specified\

  - stop : request the server to stop sending data\

  - quit : request to disconnect with the server\


Server responses:\

  - list : return the list of songs existing in the server and their ID number\

  - play : provide the client with chunks of data for the specified song\

  - stop : stop providing client with chunks of data for the specified song\ 


Upon a client quit request, the server will send a response back to the client. If the client is able to exit gracefully, this indicates that the quit request has been properly executed.   

If a non-existant song ID is provided by the user, the server will not send a response back to the client.  


## Packets 

The client and server communicates via packets that store information about message types (e.g. list, play), song ID, and data in text format.

When transmitting packets, only necessary components are stringified, sent, and decoded back to a packet at the other end. 


## Message Formats 

When packets are stringified, the string is delimited by <NEXT;>, and the end of the string will be noted as <END;>. 

To reassemble back to a packet structure, the string is split by <NEXT;>.  

Client --> Server Example:\

  
  - play<NEXT;>song ID<NEXT;><END;>\


Server --> Client Example:\

  
  - play<NEXT;>data<NEXT;><END;>\



# Streaming

## Step 1 : Creating a Client Request

Once a connection has been established through sock.connect(), the client is ready to send a request. All invalid commands will be discarded, and once a valid command has been inputted by the user, a packet will be generated. This packet holds information on the message type and the song ID (if any). 

Once the packet has been generated, it **SHOULD** be encoded into a string with the format mentioned in the "Message" section of this document and then sent over to the server.

## Step 2 : Processing Server Response 

Once a string has been received from the client, the server **MUST** decode the string back into a packet. The server will then process the packet to observe the message type and song ID (if any). 

If a list or play request is to be processed, the server **SHALL** inject data into the packet. For list requests, this **SHOULD** be the list of songs and for play requests, this **SHOULD** be the raw data of music files. Typically, music files tend to have a higher capacity than the send buffer, and must be sent in separate chunks. Please see the "Performance Consideration" section of this document for details. 

Once the injection process is finished, the packet is then decoded into a string and sent to the client.

## Step 3: Processing Client Response 

Once a string has been received from the server, the client **MUST** decode the string back into a packet. The client will then process the packet to observe the message type and data (if any). 

If a play request had been issued, the music data will be buffered as much as the receive buffer can handle. Once the client observes that a packet has data, it will output that data.  


# Performance Considerations

  - The "play" command will first issue a stop request if a song is playing, sleep for a short period to process the packet, and then reissue a play request. A sleep period is important as without it, there could be a collision between the stop and play requests.\

  - The max buffer size on both the server and client here is capped at 4096 and the music data itself is capped at 4072. If the buffer is too low, this may result in stuttering, but if the buffer is too high, it may fail to drain at an appropriate delay and the initial wait could be long.   


