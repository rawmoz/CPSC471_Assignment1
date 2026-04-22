Names and Emails:
Daniel Ramos - danielaramos@csu.fullerton.edu
- [Name 2] - [email2@csu.fullerton.edu]
- [Name 3] - [email3@csu.fullerton.edu]

Programming Language: Python

How to Execute:
1. Start the server:
   python serv.py <port>
   e.g. python serv.py 1234

2. Start the client (in a separate terminal):
   python cli.py <server> <port>
   e.g. python cli.py localhost 1234

3. Available commands:
   ftp> get <filename>   - download file from server
   ftp> put <filename>   - upload file to server
   ftp> ls               - list files on server
   ftp> quit             - disconnect and exit