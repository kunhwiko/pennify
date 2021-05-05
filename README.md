### How to connect to the EC2 instance:
1. Go to the pennify directory (doesn't have to be in Vagrant).
2. Run "ssh -i ec2/login2.pem ubuntu@ec2-34-228-194-115.compute-1.amazonaws.com" to enter the EC2 instance
3. When inside the EC2 instance, try "cd pennify". If the pennify directory exists, continue to step 5.
4. If the pennify directory doesn't exist, clone it from this repository.
5. Inside the pennify directory, run "python server.py 55353 music"
6. The server is now running on EC2
7. Use ctrl \ to exit the server

### How to run the client
1. In vagrant, go to the pennify directory
2. Run "python client.py 34.228.194.115 55353"


# Project 6: Streaming Music Service

In this project, you'll be designing and implementing a protocol of your own in order to learn all of the concerns that go into constructing one.
Specifically, you will be building a protocol for a music streaming service in which a server with music files responds to client requests for music.
You'll need to worry about things like header and message formats, proper framing of messages, and the behavior of both sides in response to every message.
In class, we discussed a few approaches to building such a service: simple HTTP gets, a custom streaming protocol like RTSP, or DASH-like chunking via HTTP.
Note that while RTSP is a good strawman, it is likely *much* more complicated than you need for this project.

Since you will be developing the protocol, client, and server, there is no single correct design or architecture.
You just need to be sure that we can run your implementation and play music.


### Requirements

* You will turn in an RFC for your protocol that specifies the exact behavior of your protocol.  You will turn in a shortened, preliminary version of this before the final implementation so that we know that you've thought about your protocol.  With the final implementation, you will turn in a more in-depth version that fully and completely describes the protocol format and client/server behavior.  The RFC should be like any other RFC - detailed enough that any of the instruction staff could implement their own version just from the description.

* Your implementation should be directly on top of raw sockets.  You should not, for instance, use any existing HTTP or RPC implementation.

* We have provided skeleton code for a threaded client and server in Python.  Feel free to start from scratch in a different language or with a different architecture (e.g.,  select() statements).  If you choose a different language, you will be responsible for finding libraries that can play mp3 files.

* Your server should be able to handle multiple clients simultaneously.  They should be able join and leave at any time, and the server should continue to operate seamlessly.

* Your client should be interactive and it should know how to handle at least the following commands:
    * `list`: Retrieve a list of songs that are available on the server, along with their ID numbers.
    * `play [song number]`: Begin playing the song with the specified ID number. If another song is already playing, the client should switch immediately to the new one.
    * `stop`: Stops playing the current song, if there is one playing.

* The client should be able to stream, i.e., start playing music before the mp3 has been downloaded and terminate transmission early if the client stops playing the song.  Note that mp3s are designed exactly for this purpose!  If you start feeding  mp3 data frames to the provided mp3 library, it will be able to play without needing the entire file.

* Similar to the above, the server should be able to handle new commands without needing to finish sending the previous file.  For instance, if it receives a `list` command during playback of a giant music file, the client should be able to see the list of songs immediately.

* The client should not cache data. In other words, if the user tells the client to get a song list or play a song, the two should exchange messages to facilitate this. Don't retrieve an item from the server once and then repeat it back again on subsequent requests.

* One of the parameters to your server should be a path to a directory that contains audio files. Within this directory, you may assume that any file ending in ".mp3" is an mp3 audio file. We have provided three CC-licensed songs as a start.  Feel free to use those or your own mp3 files for testing. **Please do not submit audio files to Canvas!**

* Your client and server should try to avoid stuttering as much as possible.  At a minimum, you should have some strategy to pre-buffer in order to avoid stuttering at the beginning of the song.  **More interesting approaches may be rewarded with extra credit**

## Amazon AWS

Your demo should have the server running on an AWS EC2 instance and the client running on your laptop in your local Vagrant VM.


### Signing up for an AWS Educate credit

As a student, you can sign up for an AWS account with free credits as follows.

NOTE: at some point, you will be asked if you want to create a starter account or if you want to use an existing account.  A starter account does not require a credit card, but it also has some limitations of available features and tools.  For this class, a starter account should be sufficient, but if you are in other classes that require AWS, you may find a real account to be more useful.

1. Go to https://aws.amazon.com/education/awseducate/apply/, click Apply for AWS Educate for Students.  You will be asked to enter some information.  You will need to use your upenn.edu email account so Amazon will know you are affiliated with Penn and grant you credits.  After they review and approve your application, you will receive an email with instructions that may include a promo code, etc.
3. [Only if using an existing account:] Visit https://console.aws.amazon.com/billing/home#/credits and enter your credit code there.
4. In your Vagrant Terminal, make a new subdirectory .ec2 under your home directory.
5. Log in again (under http://aws.amazon.com/, 'Sign in to the AWS Management Console'), find the account menu in the upper right corner (with your name), and select My Security Credentials.
6. Go to Access keys and create a new key, and then either Download Key File (in .csv format) or save your Access Key ID and the Secret Access Key directly to a text file (click on Show Access Key to reveal it).  You can copy and paste them to other files later.
7. Click on Key Pair, scroll down to the Amazon EC2 Key Pairs area, and click on Access Your Amazon EC2 Key Pairs using the AWS Management Console.  Then click on Key Pairs in the sidebar on the left and Create Key Pair.  Save the file as `~/.ec2/login.pem`.

### Launching an EC2 Instance

Go to the AWS Management Console (https://console.aws.amazon.com/) and sign in. 

1. Choose EC2 from the big list (left column, second from the top, orange icon)
2. Verify that the drop-down box on the upper right shows "N. Virginia", so you'll get an instance on the East coast.  Sometimes you’ll see this region listed as “us-east-1.”
3. Click on the "Launch Instance" button. Now you need to choose a type of virtual machine. Let's go with "Ubuntu Server 16.04 LTS", which matches your Vagrant VM.
4. Choose the smallest instance type available (or free tier eligible if that applies to you).
5. You can leave most of the subsequent configuration options as their defaults, except the security group.  Click "6. Configure Security Group" at the very top of the screen.
6. AWS usually pre-populates a rule to allow incoming SSH connections and blocks all others with a firewall.  We'll want to allow a port for our music protocol as well.
7. Click "Add Rule" and configure a "Custom TCP Rule" type with Port Range "55353", Source "Anywhere", and Description "Music streaming".
8. Click "Review and Launch", then "Launch".
9. You will be asked to select an existing key pair. Choose the key pair you created initially, and check the box to acknowledge that you do have the private key file available. Click "Launch Instances". Recall that, from now on, you will be billed on an hourly basis, so don’t forget to turn the instance(s) off later! Click View Instances.
10. Wait for the instance list to indicate the instance(s) are ready (Status 'running', with a green dot next to it). If the status is 'pending', with a yellow dot next to it, you need to wait a bit. 
11. Click on the instance, look at the bottom of the pane (EC2 Instance: i-xxxxx), and scroll down until the Public DNS entry appears. This is your instance's public DNS name. Write it down.



### Connecting to an EC2 Instance 

You can connect to a Linux EC2 instance using ssh as follows:

1.  Connect to your instance using the its public DNS name. For example, if instance's DNS name is ec2-75-101-230-211.compute-1.amazonaws.com, use commands like: 

```
ssh -i ~/.ec2/login.pem ubuntu@ec2-75-101-230-211.compute-1.amazonaws.com
```

You should see a response like the following:

> The authenticity of host 'ec2-75-101-230-211.compute-1.amazonaws.com (75.101.230.211)' can't be established. 
RSA key fingerprint is fc:8d:0c:eb:0e:a6:4a:6a:61:50:00:c4:d2:51:78:66. 
Are you sure you want to continue connecting (yes/no)? 

2.  Enter yes. You'll see a response like the following:

> Warning: Permanently added ' ec2-75-101-230-211.compute-1.amazonaws.com' (RSA) 
to the list of known hosts. 

You're now logged in and can work with the instance like you would any normal server.  Just remember that you are being billed while the server is alive and you're responsible for any charges! Log out using exit or logout.


### Terminating an EC2 Instance 

Please note that you will be billed for AWS instances as they are alive, so you will want to terminate them when they aren’t in direct use.

1.  In the AWS Management Console (http://aws.amazon.com/console/), locate the instance in your list of instances on the EC2 Instances page. 
2.  Right-click the instance, and then click Terminate.
3.  Click Yes, Terminate when prompted for confirmation. 

Amazon EC2 begins terminating the instance. As soon as the instance status changes to shutting down or terminated, you stop incurring charges for that instance.  Similarly, you should delete EBS volumes (or any other resources) that you aren't using anymore.  Also note that the EC2 Dashboard has an overview of the resources you're currently using.



## Part A: Protocol Design

For the first part of this assignment, you and your partner will be designing your own protocol and describing it in RFC format.
RFCs, or a Requests for Comments, are the documents that we use to communicate methods, protocols, and observations about the Internet.
In the context of standards, RFCs from "IETF Working Groups" ensure that anyone building a network device, operating system, or just looking at packets will be able to understand the protocol and implement it correctly on their own.
Not all RFCs describe Internet standards, however, some of them are just informational.
You've already seen some examples of RFCs in previous projects (esp. HW2) so you should have at least some idea of what they look like.

### Getting started

We've provided a utility that can compile markdown, the markup language used in things like github/bitbucket's README files to RFC format.
If you've never used markdown, don't worry -- it's very easy to use and is an essential tool for today's repo management.
The first step is getting the RFC compilation utility working and compiling some example RFCs.
From your `553-hw6/` directory, run:

```
setup/rfc.sh
cd mmark/rfc
make txt
make html
```

This will generate both the text and the html versions of several actual RFCs.
You should take a look at the `.md` files to see the syntax of Markdown, specifically how the number of #'s changes the size of the section heading and how packet formats are laid out.
RFC7511 includes many features that you might find useful in your descriptions.

### Writing the RFC

You'll write the RFC in two stages.

In a preliminary version of the RFC (due on Canvas before the full deadline), you will describe your plans for the protocol.
This version, at a minimum, should include a detail specification of your message formats and options.
Note that, at this stage, the protocol you describe does **not** need to be the protocol you end up implementing (although good design at this stage will help you when you are implementing).
It's okay if, during the course of your implementation, you find and fix bugs in your original protocol implementation.

In the full version, you will need to also describe the necessary behavior of your client and server in a way that is detailed, precise, and complete.
Your grade for this RFC will be on correctness of the protocol, the clarity, the style, and the precision of the wording.
This should include but not be limited to correct use of [RFC2119](https://www.ietf.org/rfc/rfc2119.txt) in your RFCs.

To get you started, here are a few questions that you should ask yourselves during the course of designing the protocol:

* What types of messages does your streaming server/client send, and what do they mean?
* How are your messages formatted?  Are they text or binary, and what does the header look like?
* How do you determine where one message ends and another begins (i.e., framing)?
* What type of state does the server need to store per-client?  What does that state mean (e.g., the fields in the client struct)?
* How do messages transition the client/server from one state to another?
* Anything else I should know about the way it works?

There is no hard minimum or maximum length as long as you describe the protocol well.
As reference, you should base your RFC on the `.md` files included in the `mmark/rfc/` directory, and look at other RFCs for inspiration.
A few other resources that might be helpful:

[Markdown cheatsheet](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

[mmark markdown information](https://mmark.miek.nl/post/syntax/)

[RFC style guide](https://www.rfc-editor.org/rfc/rfc7322.html)

## Part B: Client and server implementation

Your client and server should implement the protocol above (or a fixed version of it).
The implementation should satisfy the requirements at the beginning of this document.
Note that the implementation here is in Python, but the socket interface should be pretty similar to C++.
For example, the Python server should probably do something like:

```
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', server_port))
s.listen(QUEUE_LENGTH)
```

You can refer to Python's socket API for more information:

[Python socket](https://docs.python.org/2/library/socket.html)

### Getting started

The provided repository contains a few pieces of code:

 * `setup/` contains a few bash scripts for setting up your environment.  We will discuss this below.
 * `client.py` and `server.py` include some skeleton code that you may find helpful for structuring your implementations.
 * `mp3-example.py` is a utility file that just plays mp3 files.  You can use this to test your machine setup and to see how to play an mp3 file from Python.
 * `music` contains the example mp3 files.


The first step is to ensure that you can play music in your Vagrant VM.  Try running from the 553-hw6 directory:

```
python mp3-example.py music/cinematrik\ -\ Revolve.mp3
```

##### Troubleshooting

1. Depending on your Linux kernel version, you may need to run the following script to patch a compatibility issue with our Vagrantfile and recent Linux kernels:

```
setup/fix.sh
```

2. You may also need to run the following commands after a `vagrant halt` and `vagrant up`.

```
sudo alsa force-reload
sudo alsactl init
amixer set Master 100%
amixer set Master unmute
```

3. Make sure that the sound on your Host OS is turned all the way up.

4.  If the `mp3-example.py` script still does not work after the above steps, please post the output of `sudo alsa force-reload` and `sudo alsactl init` to Piazza.


### Helpful hints

* When using threads, be very careful with thread safety.  Python has a threading module that gives you threads, locks, and condition variables.  Note that socket `send`s/`recv`s are thread safe, meaning you can have a thread send() and another thread recv() concurrently without the help of locks, etc.  You probably don't want to execute *split* sends (or recvs) for the same connection in two different threads as messages can become interleaved.

* The python struct module is very useful for serializing and deserializing arbitrary datatypes.

* It's possible that a client closes a connection just before your server attempts to send to it. In this case, by default, two things will happen: 1) your process will receive the SIGPIPE signal, which by default, kills your process, and 2) send will return an error and set errno to EPIPE to indicate the connection (pipe) was broken. Obviously you don't want (1) to occur, since you still want to service other clients. Luckily, we can easily prevent that signal by using the that extra "flags" parameter to send that we've been ignoring thus far. By setting the flags to MSG_NOSIGNAL, the kernel will only do (2), which is a much more convenient way for you to detect and handle a client disconnection.

* You should think a lot about different interleavings of messages as this is an asynchronous system.  For example, what if, between the sending of two chunks of music, the server receives a play-stop-play sequence of messages?  Presumably the result should be that the second play command happens and the first does not.

* Test your code in small increments. It's much easier to localize a bug when you've only changed a few lines.

* If you want your client to begin playing a new file, you need to create a new MadFile object. This tells mad (our audio library) to interpret the next bytes as the beginning of a new file (which includes some metadata) rather than the middle of the previously playing file.


### Submission and grading

For the preliminary RFC, *one partner* should submit the .txt and .html files generated by `mmark` to Canvas.  Again, see `mmark/rfc/Makefile` for how to do this from a `.md` file.

For the full submission, *one partner* should submit the client implementation, server implementation, and the .txt/.html RFC to Canvas.  You should also submit a readme with instructions on how to run your code.  If we can't get it to run, you will lose points!

Adapted with permission from Kevin Webb at Swarthmore College
