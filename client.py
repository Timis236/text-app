import tkinter as tk
import socket

WIDTH = 1280
HEIGHT = 960

MAX_MSG_SIZE = 4194304
MAX_ID_SIZE = 24
MAX_TITLE_SIZE = 50
MAX_CONTENT_LENGTH = MAX_MSG_SIZE - (MAX_ID_SIZE * 2) - MAX_TITLE_SIZE - 1

# list of characters forbidden in the title (\, /, :, *, ?, ", <, >, |, @)
FORBIDDEN_TITLE = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|", "@"]

id_user = ""
id_pass = ""
id_newpass = ""
title = ""
content = ""
ip = ""
port = ""

# keep track of when the user info window is open
uinfo_open = False

# keep track of when the change password layout for the user info window is active
uinfo_changepass = False

# set default text file
def initialize_default(m):
    global id_user
    global id_pass
    global ip
    global port
    
    try:
        fp = open("c_default.txt", "r")
        
        if (m == "a" or m == "d"):
            tmp = fp.readline()
            if (tmp.count("\"") >= 2):
                id_user = tmp[tmp.find("\"") + 1:tmp.rfind("\"")]
            tmp = fp.readline()
            if (tmp.count("\"") >= 2):
                id_pass = tmp[tmp.find("\"") + 1:tmp.rfind("\"")]
        if (m == "u" or m == "d"):
            if (m == "u"):
                fp.readline()
                fp.readline()
            tmp = fp.readline()
            if (tmp.count("\"") >= 2):
                ip = tmp[tmp.find("\"") + 1:tmp.rfind("\"")]
            tmp = fp.readline()
            if (tmp.count("\"") >= 2):
                port = tmp[tmp.find("\"") + 1:tmp.rfind("\"")]

        fp.close()
        fp = open("c_default.txt", "w")
        fp.write("user:\"" + id_user + "\"\n")
        fp.write("pass:\"" + id_pass + "\"\n")
        fp.write("ip:\"" + ip + "\"\n")
        fp.write("port:\"" + port + "\"\n")
        fp.close()
    except:
        fp = open("c_default.txt", "w")
        fp.write("user:\"" + id_user + "\"\n")
        fp.write("pass:\"" + id_pass + "\"\n")
        fp.write("ip:\"" + ip + "\"\n")
        fp.write("port:\"" + port + "\"\n")
        fp.close()
        
        
# run immediately to initialize file/user/address
initialize_default("d")

# ----- TEXT FILTERING AND UPDATING FUNCTIONS -----

# prevent forbidden characters in title text
def title_filter(entry, text):
    for i in FORBIDDEN_TITLE:
        tmp = entry.get().replace(i, "")
        entry.delete(0, tk.END)
        entry.insert(0, tmp)
    size_filter(text, MAX_TITLE_SIZE)
    
# prevent forbidden characters in ip text
def ip_filter(entry, text):
    tmp = entry.get()
    for i in tmp:
        if (i.isdecimal() == False and i != "."):
            tmp2 = entry.get().replace(i, "")
            entry.delete(0, tk.END)
            entry.insert(0, tmp2)
    size_filter(text, 15)
    
# prevent forbidden characters in port text
def port_filter(entry, text):
    tmp = entry.get()
    for i in tmp:
        if (i.isdecimal() == False):
            tmp2 = entry.get().replace(i, "")
            entry.delete(0, tk.END)
            entry.insert(0, tmp2)
    size_filter(text, 5)
    
# prevent forbidden characters in username text
def username_filter(entry, text):
    tmp = entry.get()
    for i in tmp:
        if (i.isdigit() == False and i.isalpha() == False and i != "_" and i != "-"):
            tmp2 = entry.get().replace(i, "")
            entry.delete(0, tk.END)
            entry.insert(0, tmp2)
    size_filter(text, MAX_ID_SIZE)
    
# prevent forbidden characters in password text
def password_filter(entry, text):
    tmp = entry.get()
    for i in tmp:
        if (i == " "):
            tmp2 = entry.get().replace(i, "")
            entry.delete(0, tk.END)
            entry.insert(0, tmp2)
    size_filter(text, MAX_ID_SIZE)

# limit the length of entries
def size_filter(text, size):
    if (len(text.get()) > size):
        text.set(text.get()[:size])
        
# updates the label under the content text box to display the proper length in characters
def update_content_label(event):
    c_label.config(text=str(len(c_text.get("1.0", 'end-1c'))))
        
# ----------------------------------------



# ----- TEXT VERIFICATION FUNCTIONS -----

# verify a string representing an ip
def verify_ip(ip):
    ip_list = ip.split(".")
    if (len(ip_list) != 4):
        return False
    else:
        valid = True
        for i in ip_list:
            if (int(i) < 0 or int(i) > 255):
                valid = False
                break
        
        return valid

# verify a string representing a port
def verify_port(port):
    return (int(port) > 0 and int(port) < 65536)

# ----------------------------------------



# ----- USER INFO FUNCTIONS -----

# set the uinfo_open variable and uinfo_changepass variable (if applicable) to false when the uinfo window is closed
def set_uinfo_closed(event):
    global uinfo_open
    global uinfo_changepass
    
    uinfo_open = False
    if (uinfo_changepass):
        uinfo_changepass = False

# run user information window
def run_uinfo():
    global uinfo_open
    global uinfo_changepass
    
    # if the window is already open, we do not want to open another one
    if not uinfo_open:
        uinfo_open = True
        
        # initialize identification tkinter window
        uinfo = tk.Toplevel(main)
        uinfo.title("ID")
        uinfo.resizable(width=False, height=False)
        uinfo.geometry("200x250")
        uinfo.configure(bg="#dddddd")
        uinfo.bind('<Destroy>', set_uinfo_closed)
        uinfo.attributes('-topmost', True)
    
        # username and password label/entry creation
        user_label = tk.Label(uinfo, text="Username", bg="#dddddd")
        user_label.pack()
        user_text = tk.StringVar()
        user_text.set(id_user)
        user_entry = tk.Entry(uinfo, textvariable=user_text)
        user_entry.pack()
        user_text.trace_add("write", lambda *args: username_filter(user_entry, user_text))
        
        pass_label = tk.Label(uinfo, text="Password", bg="#dddddd")
        pass_label.pack()
        pass_text = tk.StringVar()
        pass_text.set(id_pass)
        pass_entry = tk.Entry(uinfo, textvariable=pass_text)
        pass_entry.pack()
        pass_text.trace_add("write", lambda *args: password_filter(pass_entry, pass_text))
    
        # new password label/entry creation
        newpass_label = tk.Label(uinfo, text="New Password", bg="#dddddd")
        newpass_text = tk.StringVar()
        newpass_entry = tk.Entry(uinfo, textvariable=newpass_text)
        newpass_text.trace_add("write", lambda *args: password_filter(newpass_entry, newpass_text))
    
        # save the contents of the two entries to the global user/pass variables
        def set_uinfo():
            global uinfo_changepass
            global id_user
            global id_pass
            global id_newpass
            global ip
            global port
            
            if (not uinfo_changepass):
                if (len(user_text.get()) == 0 or len(pass_text.get()) == 0):
                    save_label.config(text="Please fill both fields.")
                    save_label.place_configure(x=42)
                else:
                    id_user = user_text.get()
                    id_pass = pass_text.get()
                    save_label.config(text="Saved!")
                    save_label.place_configure(x=79)
            else:
                # handle changing password
                log.config(state=tk.NORMAL)
                
                if (len(user_text.get()) == 0 or len(pass_text.get()) == 0 or len(newpass_text.get()) == 0):
                    save_label.config(text="Please fill all fields.")
                    save_label.place_configure(x=48)
                elif (len(ip_entry.get()) == 0 or len(port_entry.get()) == 0):
                    log.delete("1.0", tk.END)
                    log.insert("1.0", "Error: One or more parameters are blank.")
                elif (verify_ip(ip_entry.get()) == False):
                    log.delete("1.0", tk.END)
                    log.insert("1.0", "Error: IP is invalid.")
                elif (verify_port(port_entry.get()) == False):
                    log.delete("1.0", tk.END)
                    log.insert("1.0", "Error: Port is invalid.")
                else:
                    ip = ip_entry.get()
                    port = port_entry.get()
                    id_user = user_text.get()
                    id_pass = pass_text.get()
                    id_newpass = newpass_text.get()
                    
                    reply = send_and_receive(chr(5) + id_user.ljust(MAX_ID_SIZE) + id_pass.ljust(MAX_ID_SIZE) + id_newpass.ljust(MAX_ID_SIZE))
                    save_label.config(text="Request sent, check log.")
                    save_label.place_configure(x=35)
                    if (reply != ""):
                        log.delete("1.0", tk.END)
                        log.insert("1.0", reply)
                
                log.config(state=tk.DISABLED)
        
        # toggle the change password entry and label, and enable change password mode
        def set_change_password():
            global uinfo_changepass
            
            if (not uinfo_changepass):
                newpass_label.pack()
                newpass_entry.pack()
                changepass_button.config(text="Return to User Setting")
                changepass_button.place_configure(x=37, y=210)
                default_user_button.config(state=tk.DISABLED)
                
                uinfo_changepass = True
            else:
                newpass_label.pack_forget()
                newpass_entry.pack_forget()
                changepass_button.config(text="Change Server-Side Password")
                changepass_button.place_configure(x=16, y=210)
                default_user_button.config(state=tk.NORMAL)
                
                uinfo_changepass = False
                
            save_label.config(text="")
                
        # set the default user
        def set_default_user():
            global uinfo_changepass
            global id_user
            global id_pass
            
            id_user = user_text.get()
            id_pass = pass_text.get()
        
            initialize_default("u")
            
            save_label.config(text="Saved as default!")
            save_label.place_configure(x=53)
    
        # save label creation
        save_label = tk.Label(uinfo, text="", bg="#dddddd")
        save_label.place(x=80, y=125)

        # set button creation
        set_button_info = tk.Button(uinfo, text="Set", bg="#bcbcbc", command=set_uinfo)
        set_button_info.place(x=85, y=150)
        
        # change password toggle button
        changepass_button = tk.Button(uinfo, text="Change Server-Side Password", bg="#bcbcbc", command=set_change_password)
        changepass_button.place(x=16, y=210)
        
        # set default user button
        default_user_button = tk.Button(uinfo, text="Save as Default", bg="#bcbcbc", command=set_default_user)
        default_user_button.place(x=54, y=180)

# set the default address
def set_default_address():
    global ip
    global port
    
    ip = ip_text.get()
    port = port_text.get()

    initialize_default("a")
    
    log.config(state=tk.NORMAL)
    
    log.delete("1.0", tk.END)
    log.insert("1.0", "IP and port saved as default!")
    
    log.config(state=tk.DISABLED)

# ----------------------------------------

# ----- CONNECT BUTTON FUNCTIONS -----

def get_files():
    global ip
    global port
    
    log.config(state=tk.NORMAL)
    
    if (len(ip_entry.get()) == 0 or len(port_entry.get()) == 0):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: One or more parameters are blank.")
    elif (verify_ip(ip_entry.get()) == False):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: IP is invalid.")
    elif (verify_port(port_entry.get()) == False):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: Port is invalid.")
    else:
        ip = ip_entry.get()
        port = port_entry.get()
        
        reply = send_and_receive(chr(1))
        if (reply != ""):
            reply_list = reply.split("\n")
            for i in range(len(reply_list)):
                reply_list[i] = reply_list[i][:-4]
            f_var_list.set(reply_list)
        
            log.delete("1.0", tk.END)
            log.insert("1.0", "Successfully received file names from \"" + ip + ":" + port + "\".")
        
    log.config(state=tk.DISABLED)

def upload_file():
    global title
    global content
    global ip
    global port
    global id_user
    global id_pass
    
    log.config(state=tk.NORMAL)
    
    if (len(t_entry.get()) == 0 or len(c_text.get("1.0", "end-1c")) == 0 or len(ip_entry.get()) == 0 or len(port_entry.get()) == 0):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: One or more parameters are blank.")
    elif (verify_ip(ip_entry.get()) == False):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: IP is invalid.")
    elif (verify_port(port_entry.get()) == False):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: Port is invalid.")
    elif (len(c_text.get("1.0", 'end-1c')) > MAX_CONTENT_LENGTH):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: Content length exceeds maximum size. (" + str(len(c_text.get("1.0", 'end-1c'))) + "/" + str(MAX_CONTENT_LENGTH) + ")")
    else:
        title = t_entry.get()
        content = c_text.get("1.0", "end-1c")
        ip = ip_entry.get()
        port = port_entry.get()
        
        reply = send_and_receive(chr(2) + id_user.ljust(MAX_ID_SIZE) + id_pass.ljust(MAX_ID_SIZE) + title.ljust(MAX_TITLE_SIZE, "@") + content)
        if (reply != ""):
            log.delete("1.0", tk.END)
            log.insert("1.0", reply)
            if (reply == "Successfully uploaded file: " + title + "@" + id_user and title + "@" + id_user not in f_box.get(0, tk.END)):
                f_box.insert(tk.END, title + "@" + id_user)
        
    log.config(state=tk.DISABLED)

def delete_file():
    global ip
    global port
    global id_user
    global id_pass
    
    log.config(state=tk.NORMAL)
    
    if (len(ip_entry.get()) == 0 or len(port_entry.get()) == 0):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: One or more parameters are blank.")
    elif (verify_ip(ip_entry.get()) == False):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: IP is invalid.")
    elif (verify_port(port_entry.get()) == False):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: Port is invalid.")
    elif (len(f_box.curselection()) == 0):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: No file is selected.")
    else:
        ip = ip_entry.get()
        port = port_entry.get()
        selected = f_box.curselection()[0]
        title_username = f_box.get(selected)
        
        reply = send_and_receive(chr(3) + id_user.ljust(MAX_ID_SIZE) + id_pass.ljust(MAX_ID_SIZE) + title_username)
        if (reply != ""):
            log.delete("1.0", tk.END)
            log.insert("1.0", reply)
            if (reply == "Successfully deleted file: " + title_username):
                f_box.delete(selected)
    
    log.config(state=tk.DISABLED)
        
def load_file():
    global ip
    global port
    
    log.config(state=tk.NORMAL)
    
    if (len(ip_entry.get()) == 0 or len(port_entry.get()) == 0):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: One or more parameters are blank.")
    elif (verify_ip(ip_entry.get()) == False):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: IP is invalid.")
    elif (verify_port(port_entry.get()) == False):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: Port is invalid.")
    elif (len(f_box.curselection()) == 0):
        log.delete("1.0", tk.END)
        log.insert("1.0", "Error: No file is selected.")
    else:
        ip = ip_entry.get()
        port = port_entry.get()
        selected = f_box.curselection()[0]
        title_username = f_box.get(selected)
        
        reply = send_and_receive(chr(4) + title_username)
        if (reply != ""):
            t_entry.delete(0, tk.END)
            t_entry.insert(0, reply[:reply.find("\n")])
            c_text.delete("1.0", tk.END)
            c_text.insert("1.0", reply[reply.find("\n") + 1:])
        
            log.delete("1.0", tk.END)
            log.insert("1.0", "Successfully loaded file: " + title_username)
        
    log.config(state=tk.DISABLED)
    
def send_and_receive(msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    reply = ""
    
    try:
        sock.connect((ip, int(port)))
        try:
            sock.send(msg.encode())
            try:
                reply = sock.recv(MAX_MSG_SIZE)
            except:
                log.delete("1.0", tk.END)
                log.insert("1.0", "Failed to receive from \"" + ip + ":" + port + "\", changes may have been made.")
        except:
            log.delete("1.0", tk.END)
            log.insert("1.0", "Failed to send to \"" + ip + ":" + port + "\".")
    except:
        log.delete("1.0", tk.END)
        log.insert("1.0", "Failed to connect to \"" + ip + ":" + port + "\".")

    try:
        sock.close()
    except:
        log.insert("1.0", " (Couldn't close socket)")
    
    if (reply == ""):
        return reply
    else:
        return reply.decode()

# ----------------------------------------



# ----- MAIN WINDOW CODE -----

# initialize main tkinter window
main = tk.Tk()
main.title("Text App")
main.resizable(width=False, height=False)
main.geometry(str(WIDTH) + "x" + str(HEIGHT))

# initialize canvas for improved visuals
can = tk.Canvas(main, bg="#7d8d9c", height=HEIGHT, width=WIDTH)
can.pack()

# background element creation
info_bg = can.create_rectangle(125, 10, 1155, 160, fill="#dddddd")

# title label/entry creation
t_text = tk.StringVar()
t_entry = tk.Entry(main, textvariable=t_text, font=("Consolas"))
t_entry.place(height=20, width=480, x=200, y=30)
t_label = tk.Label(main, text="File Title:", bg="#dddddd")
t_label.place(x=145, y=30)
t_text.trace_add("write", lambda *args: title_filter(t_entry, t_text))

# server ip and port entry creation
ip_text = tk.StringVar()
ip_text.set(ip)
ip_entry = tk.Entry(main, textvariable=ip_text)
ip_entry.place(height=20, width=100, x=225, y=70)
ip_text.trace_add("write", lambda *args: ip_filter(ip_entry, ip_text))
ip_label = tk.Label(main, text="Server IP:", bg="#dddddd")
ip_label.place(x=168, y=70)

port_text = tk.StringVar()
port_text.set(port)
port_entry = tk.Entry(main, textvariable=port_text)
port_entry.place(height=20, width=100, x=425, y=70)
port_text.trace_add("write", lambda *args: port_filter(port_entry, port_text))
port_label = tk.Label(main, text="Server Port:", bg="#dddddd")
port_label.place(x=355, y=70)

# content text frame creation (with scrolling)
c_frame = tk.Frame(main)
c_frame.place(height=760, width=1230, x=25, y=175)
c_yscroll = tk.Scrollbar(c_frame, orient=tk.VERTICAL, bg="#000000")
c_yscroll.pack(side=tk.RIGHT, fill="y")
c_xscroll = tk.Scrollbar(c_frame, orient=tk.HORIZONTAL, bg="#000000")
c_xscroll.pack(side=tk.BOTTOM, fill="x")
c_label = tk.Label(main, text="0", bg="#7d8d9c", font=("Arial", 9))
c_label.place(x=25, y=937)
c_text = tk.Text(c_frame, yscrollcommand=c_yscroll.set, xscrollcommand=c_xscroll.set, wrap=tk.NONE, bg="#444444", fg="#ffffff", insertbackground="#ffffff")
c_text.pack(fill=tk.BOTH, expand=True)
c_text.bind("<KeyPress>", update_content_label)
c_text.bind("<KeyRelease>", update_content_label)
c_xscroll.config(command=c_text.xview)
c_yscroll.config(command=c_text.yview)

# file list frame creation (with scrolling)
f_frame = tk.Frame(main)
f_frame.place(height=100, width=440, x=700, y=25)
f_yscroll = tk.Scrollbar(f_frame, orient=tk.VERTICAL, bg="#000000")
f_yscroll.pack(side=tk.RIGHT, fill="y")
f_var_list = tk.Variable()
f_box = tk.Listbox(f_frame, yscrollcommand=f_yscroll.set, listvariable=f_var_list, selectmode=tk.SINGLE, font=("Segoe UI", 8))
f_box.pack(fill=tk.BOTH, expand=True)
f_yscroll.config(command=f_box.yview)

# log label/text creation
log = tk.Text(main, height=1, width=86, font=("Segoe UI", 9), state=tk.DISABLED)
log.place(x=150, y=130)
log_label = tk.Label(main, text="Output Feed", font=("Segoe UI", 9, "underline"), bg="#dddddd")
log_label.place(x=360, y=109)

# buttons
set_button = tk.Button(main, text="Set User", bg="#bcbcbc", command=run_uinfo)
set_button.place(x=627, y=60)
upload_button = tk.Button(main, text="Upload File", bg="#bcbcbc", command=upload_file)
upload_button.place(x=550, y=60)
get_button = tk.Button(main, text="Get Current Server Files", bg="#bcbcbc", command=get_files)
get_button.place(x=770, y=130)
load_button = tk.Button(main, text="Load File", bg="#bcbcbc", command=load_file)
load_button.place(x=913, y=130)
delete_button = tk.Button(main, text="Delete File", bg="#bcbcbc", command=delete_file)
delete_button.place(x=981, y=130)
default_address_button = tk.Button(main, text="Save IP/Port as Default", bg="#bcbcbc", command=set_default_address)
default_address_button.place(x=550, y=95)

# start GUI
main.mainloop()

# ----------------------------------------
