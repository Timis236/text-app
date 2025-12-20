import os
import socket

MAX_MSG_SIZE = 4194304
MAX_ID_SIZE = 24
MAX_TITLE_SIZE = 50

FORBIDDEN_TITLE = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|", "@", "\n"]

# initialize files
if (not os.path.exists("s_data")):
    os.makedirs("s_data")
if (not os.path.exists("s_accounts.txt")):
    fp = open("s_accounts.txt", "a")
    fp.close()
if (not os.path.exists("s_blacklist.txt")):
    fp = open("s_blacklist.txt", "a")
    fp.close()

# get port from server host
def port_valid(port):
    if (not port.isdecimal()):
        print("Invalid port!")
        return False
    elif (int(port) < 1 or int(port) > 65535):
        print("Bad port!")
        return False
    print()
    return True

# verify username locally
def verify_username(username_string):
    username = username_string.strip()
    if (len(username) == 0):
        return False
    for i in username:
        if (i.isdigit() == False and i.isalpha() == False and i != "_" and i != "-"):
            return False
    return True

# verify password locally
def verify_password(password_string):
    password = password_string.strip()
    if (len(password) == 0):
        return False
    for i in password:
        if (i == " " or i == "\n"):
            return False
    return True

# verify title locally
def verify_title(title_string):
    title = title_string.strip("@")
    if (len(title) == 0):
        return False
    for i in title:
        for j in FORBIDDEN_TITLE:
            if (i == j):
                return False
    return True
    
# determine account status
# returns:
#       -1 - doesn't exist in the account file
#       0 - exists in account file, password does not match
#       1 - exists in account file, password matches
def account_status(username, password):
    fp = open("s_accounts.txt", "r")
    for line in fp:
        data = line.strip("\n").split()
        if (data[0] == username):
            if (data[1] == password):
                fp.close()
                return 1
            else:
                fp.close()
                return 0
    fp.close()
    return -1

# print the reply to the console and attempt to respond to the client
def print_and_respond(client, reply):
    print(reply)
    try:
        client.send(reply.encode())
    except:
        print("Failed to send reply to client.")

# --- BEGIN OPERATION ---
print("Enter an IP directly into a line in the file 's_blacklist.txt' to blacklist an IP from connecting.")
print("The file 's_accounts.txt' automatically stores all accounts which have previously stored a file on the server, with usernames and passwords separated by a whitespace.")
print()

port = input("Enter port to listen on (1-65535): ")
while (not port_valid(port)):
    port = input("Enter port to listen on (1-65535): ")

port = int(port)

try:
    # create a socket at server side using TCP / IP protocol
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    sock.bind(('', port))
    sock.listen(1)
    
    print("-----NOW LISTENING FOR CONNECTIONS-----")
    print()
    while True:
        # wait for connection
        client, address = sock.accept()
        
        print("Connection from", str(address))
        fp = open("s_blacklist.txt", "r")
        blacklisted = False
        for line in fp.readlines():
            if (line.strip("\n") == address[0]):
                print("Address is blacklisted, refusing further communication.")
                blacklisted = True
        fp.close()
        if (blacklisted == False):
            try:
                msg = client.recv(MAX_MSG_SIZE)
                raw_msg = msg.decode()
                
                # message handling
                if (len(raw_msg) == 0 or ord(raw_msg[0]) == 0 or ord(raw_msg[0]) > 5):
                    print_and_respond(client, "Error: Invalid message type.")
                    
                elif (ord(raw_msg[0]) == 1):    # retrieve files request
                    print("Client wants to receive server file data...")
                    reply = ""
                    for i in os.listdir("./s_data"):
                        reply += i
                        reply += "\n"
                    if (len(reply) > MAX_MSG_SIZE + 1):
                        print("Warning: File data length exceeds maximum message size, data will be truncated.")
                    try:
                        client.send(reply[:-1].encode())
                        print("File data sent to client.")
                    except:
                        print("Failed to send reply to client.")
                        
                elif (ord(raw_msg[0]) == 2):    # upload request
                    print("Client wants to upload a file...")
                    
                    username_start = 1
                    password_start = username_start + MAX_ID_SIZE
                    title_start = password_start + MAX_ID_SIZE
                    content_start = title_start + MAX_TITLE_SIZE
                    
                    # STEP 1: VERIFY MESSAGE LENGTH
                    if (len(raw_msg) < content_start):
                        print_and_respond(client, "Error: Bad message.")
                    else:
                        
                        # STEP 2: VERIFY MESSAGE CHARACTERS
                        invalid = False
                        if (verify_username(raw_msg[username_start : password_start]) == False):
                            print_and_respond(client, "Error: Invalid username. (Cannot have special characters)")
                            invalid = True
                        if (not invalid and verify_password(raw_msg[password_start : title_start]) == False):
                            print_and_respond(client, "Error: Invalid password. (Cannot have empty characters)")
                            invalid = True
                        if (not invalid and verify_title(raw_msg[title_start : content_start]) == False):
                            print_and_respond(client, "Error: Invalid title.")
                            invalid = True
                            
                        # STEP 3: DETERMINE ACCOUNT STATUS
                        if (not invalid):
                            username = raw_msg[username_start : password_start].strip()
                            password = raw_msg[password_start : title_start].strip()
                            title = raw_msg[title_start : content_start].strip("@")
                            content = raw_msg[content_start :]
                            
                            status = account_status(username, password)
                            if (status == 0):
                                print_and_respond(client, "Error: Incorrect password. / Account already exists.")
                            else:
                                print("Message is valid!")

                                # STEP 4: MAKE NECESSARY CHANGES
                                if (status == -1):
                                    fp = open("s_accounts.txt", "a")
                                    fp.write(username + " " + password + "\n")
                                    fp.close()
                                    print("Account does not already exist, created account: " + username)
                                
                                try:
                                    fp = open("./s_data/" + title + "@" + username + ".txt", "w")
                                    fp.write(content)
                                    fp.close()
                                    print_and_respond(client, "Successfully uploaded file: " + title + "@" + username)
                                except:
                                    print_and_respond(client, "Error: Failed to create file.")
                                        
                elif (ord(raw_msg[0]) == 3):    # delete request
                    print("Client wants to delete a file...")
                    
                    username_start = 1
                    password_start = username_start + MAX_ID_SIZE
                    title_start = password_start + MAX_ID_SIZE
                    
                    # STEP 1: VERIFY MESSAGE LENGTH
                    if (len(raw_msg) < (title_start + 1) or raw_msg[title_start :].find("@") == -1):
                        print_and_respond(client, "Error: Bad message.")
                    else:
                        
                        # STEP 2: VERIFY MESSAGE CHARACTERS
                        invalid = False
                        if (verify_username(raw_msg[username_start : password_start]) == False):
                            print_and_respond(client, "Error: Invalid username. (Cannot have special characters)")
                            invalid = True
                        if (not invalid and verify_password(raw_msg[password_start : title_start]) == False):
                            print_and_respond(client, "Error: Invalid password. (Cannot have empty characters)")
                            invalid = True
                            
                        # STEP 3: DETERMINE ACCOUNT STATUS
                        if (not invalid):
                            username = raw_msg[username_start : password_start].strip()
                            password = raw_msg[password_start : title_start].strip()
                            title = raw_msg[title_start :]
                            
                            if (username != title[title.find("@") + 1:]):
                                print_and_respond(client, "Error: Cannot delete a file belonging to another user.")
                            else:
                                status = account_status(username, password)
                                if (status == 0):
                                    print_and_respond(client, "Error: Incorrect password.")
                                else:
                                    print("Message is valid!")
                                    
                                    # STEP 4: MAKE NECESSARY CHANGES
                                    if (status == -1):
                                        print_and_respond(client, "Error: Account does not exist.")
                                    else:
                                        try:
                                            os.remove("./s_data/" + title + ".txt")
                                            print_and_respond(client, "Successfully deleted file: " + title)
                                        except:
                                            print_and_respond(client, "Error: File does not exist.")
                                    
                elif (ord(raw_msg[0]) == 4):    # load request
                    print("Client wants to load a file...")
                    if (len(raw_msg) <= 1):
                        print_and_respond(client, "Error: Bad message.")
                    else:
                        try:
                            fp = open("./s_data/" + raw_msg[1 :] + ".txt", "r")
                            reply = raw_msg[1 : raw_msg.find("@")] + "\n" + fp.read()
                            try:
                                client.send(reply.encode())
                                print("File contents sent to client.")
                            except:
                                print("Failed to send reply to client.")
                            fp.close()
                        except:
                            print_and_respond(client, "Error: File does not exist.")
                        
                elif (ord(raw_msg[0]) == 5):    # change password request
                    print("Client wants to change a password...")
                    
                    username_start = 1
                    password_start = username_start + MAX_ID_SIZE
                    new_password_start = password_start + MAX_ID_SIZE
                    new_password_end = new_password_start + MAX_ID_SIZE
                    
                    # STEP 1: VERIFY MESSAGE LENGTH
                    if (len(raw_msg) != new_password_end):
                        print_and_respond(client, "Error: Bad message.")
                    else:
                        
                        # STEP 2: VERIFY MESSAGE CHARACTERS
                        invalid = False
                        if (verify_username(raw_msg[username_start : password_start]) == False):
                            print_and_respond(client, "Error: Invalid username. (Cannot have special characters)")
                            invalid = True
                        if (not invalid and verify_password(raw_msg[password_start : new_password_start]) == False):
                            print_and_respond(client, "Error: Invalid password. (Cannot have empty characters)")
                            invalid = True
                        if (not invalid and verify_password(raw_msg[new_password_start : new_password_end]) == False):
                            print_and_respond(client, "Error: Invalid new password. (Cannot have empty characters)")
                            invalid = True
                            
                        # STEP 3: DETERMINE ACCOUNT STATUS
                        if (invalid == False):
                            username = raw_msg[username_start : password_start].strip()
                            password = raw_msg[password_start : new_password_start].strip()
                            new_password = raw_msg[new_password_start : new_password_end].strip()
                            
                            status = account_status(username, password)
                            if (status == 0):
                                print_and_respond(client, "Error: Incorrect password.")
                            else:
                                print("Message is valid!")
                                
                                # STEP 4: MAKE NECESSARY CHANGES
                                if (status == -1):
                                    print_and_respond(client, "Error: Account does not exist.")
                                else:
                                    fp = open("s_accounts.txt", "r")
                                    accounts = ""
                                    for line in fp:
                                        data = line.strip("\n").split()
                                        if (data[0] == username):
                                            accounts = accounts + username + " " + new_password + "\n"
                                        else:
                                            accounts = accounts + line
                                    fp.close()
                                    fp = open("s_accounts.txt", "w")
                                    fp.write(accounts)
                                    fp.close
                                    print_and_respond(client, "Successfully changed password of user: " + username)
            except:
                print("Failed to send reply to client.")
            
        try:
            client.close()
            print(str(address), "has disconnected\n")
        except:
            print("Failed to close socket.")
        
except:
    print("Address is currently being used, cannot start.")
