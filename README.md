# Overview
Allows for one server device to receive the messages of another client device over the network and store its contents in a locally saved file. The files can then be accessed by any client connecting to the server and can be viewed by others or edited/removed (provided they have the correct username and password). Accounts are created when files are uploaded and are tied to the file, both in name and in editing. Users are also able to change their password.

# Server Function
The server is a simple application that awaits connections from other clients on a user-chosen port, and receives a single message from them, telling the server of their request in a simple string. When reading a message, the first thing the server does is read the first character of the message, whose value corresponds to the type of request. Note that chr(n) indicates the character with ASCII value n.

Message Formats:

chr(1)
  - chr(1) indicates a request to view all files stored on the server.
  - Upon reading this character, the server simply sends a list of all saved file titles and associated usernames.

chr(2) + <username (20 chars)> + <password (20 chars)> + <title (50 chars)> + <file contents>
  - chr(2) indicates a request to upload a file to the server.
  - Upon reading this character, the server then reads and verifies the proper structure of the username, password, and title fields.
  - If the file doesn't exist, the server creates a file with said title, contents, and associated username, and adds the username and password to the database of "accounts".
  - If the file does exist, the password given act as a verification for permission to update the given file with the new contents, the password is compared against what is recorded in the database and if they don't match, the request is denied.

chr(3) + <username (20 chars)> + <password (20 chars)> + <title @ username>
  - chr(3) indicates a request to delete a file from the server.
  - Upon reading this character, the server then reads and verifies the proper structure of the username and password fields.
  - If the file doesn't exist, the server sends an error message response to the client.
  - If the file does exist, the password given act as a verification for permission to delete the given file, the password is compared against what is recorded in the database and if they don't match, the request is denied.

chr(4) + <title @ username>
  - chr(4) indicates a request to retrieve the contents of a particular file.
  - Upon reading this character, the server then searches for a stored file sharing the name sent by the client.
  - If the file doesn't exist, the server sends an error message response to the client.
  - If the file does exist, the server sends the title and contents to the client.

chr(5) + <username (20 chars)> + <old password (20 chars)> + <new password (20 chars)>
  - chr(5) indicates a request to change the password of a particular account.
  - Upon reading this character, the server then reads and verifies the proper structure of the username, old password, and new password fields.
  - If the account doesn't exist, the server sends an error message response to the client.
  - If the account does exist, but the old password does not match, the server sends an error message response to the client.
  - If the account does exist, and the old password does match, the password for the particular account is updated in the database of accounts.

# Client Function
The main purpose of the client is to interface with the server in an intuitive way. It is comprised of tkinter windows, buttons, and fields in order to make the experience as easy as possible for a typical user. It features:
  - Title and content text fields
  - Character count in order to keep track of size
  - Output feed giving a log of events and errors
  - IP and Port entries for connecting to a server
  - File menu for viewing files on a server
  - ID menu for changing username and password, as well as changing the server-side password for a particular user

Technically, such a client is not necessary. Messages can be sent directly to a server with any Python application, and the server is prepared to deal with any type of string it receives. However, it makes the experience much more pleasant for common users.
