Connecting to EC2 instance:

  1) SSH into the Vagrant Terminal and move to the directory that holds the subdirectory "ec2"  

  2) Connect to the EC2 instance. In our case, this is "ssh -i ec2/login.pem ubuntu@ec2-34-228-194-115.compute-1.amazonaws.com".
     You may need to change "ec2/login.pem" accordingly based on your pem file.  

  3) Inside the EC2 instance, run "cd pennify" to move to the pennify directory

  4) Start the server by running "python server.py 55353 music"


Running a client instance:

  1) SSH into the Vagrant Terminal and move to the directory that holds client.py

  2) Run "python client.py 34.228.194.115 55353"

