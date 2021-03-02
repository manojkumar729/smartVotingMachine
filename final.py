from time import sleep
from tkinter import*
from tkinter import messagebox 
import psycopg2
import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint
import PIL 
from PIL import Image,ImageTk
import RPi.GPIO as io
io.setmode(io.BOARD)
buzzer = 8
io.setup(buzzer,io.OUT)
io.output(buzzer,io.LOW)
io.setwarnings(False)

l=[]

root=Tk()
root.geometry("720x480")
root.title('Smart Voting Machine')

img = PhotoImage(file='/home/pi/Documents/smartVotingMachine/icon.png')
root.tk.call('wm', 'iconphoto', root._w, img)

def search():
	var = StringVar()
	var.set('Initializing')
	statusbar = Label(root, textvariable=var, height = 2, width = 40, bg = "#26232a",fg="white", bd=1, relief=SUNKEN, anchor="center")
	statusbar.place(relx=0.5,rely = 0.94,anchor = "center")
	l.append(statusbar)

	## Tries to initialize the sensor
	try:
		f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

		if (f.verifyPassword() == False ):
			raise ValueError('The given fingerprint sensor password is wrong!')

	except Exception as e:
		var.set('Initialization Error!')
		root.update_idletasks()
	
    ## Tries to search the finger and calculate hash
	try:
		var.set('Waiting for finger...')
		root.update_idletasks()

		## Wait that finger is read
		while ( f.readImage() == False ):
			pass

		## Converts read image to characteristics and stores it in charbuffer 1
		f.convertImage(0x01)

		## Searchs template
		result = f.searchTemplate()

		positionNumber = result[0]
		accuracyScore = result[1]

		print(positionNumber,"pos")
		if ( positionNumber == -1 ):
			var.set("Fingerprint Not found.")
			root.update_idletasks()
			return -1
	
		else:
			var.set("Success")
			root.update_idletasks()

		return positionNumber

	except Exception as e:
		var.set('Operation failed!'+'Exception message: ' + str(e))
		root.update_idletasks()

def l_clear():
	for i in l:
		i.destroy()


def mainWindow():
	l_clear()

	menubar = Menu(root)
	menubar.add_command(label="Admin",command=admin)
	root.config(menu=menubar)
	
	label_1=Label(root,text="Enter your Aadhaar Number: ",fg="black")
	label_1.place(relx = 0.5, rely = 0.4,anchor = 'ne')
	entry_1=Entry(root)
	entry_1.place(relx = 0.5, rely = 0.4,anchor ='nw')
	button=Button(text="Proceed",fg="red",bg="blue",command=lambda: fingerprint(entry_1.get()))
	button.place(relx = 0.5, rely = 0.55,anchor ='s')
	l.extend([menubar,label_1,entry_1,button])

def fingerprint(uid):
	l_clear()
	img1 = Image.open("/home/pi/Documents/smartVotingMachine/fingerprint.png")
	img = ImageTk.PhotoImage(img1)
	label = Label(root,image=img)
	label.place(relx=.5,rely=.5,anchor="center")
	label_1=Label(root,text="Fingerprint Verification",fg="white", bg="#26232a",font = "bold")
	label_1.place(relx = 0.5, rely = 0.1,anchor = 'center')
	f_index = search()
	l.extend([label,label_1])
	if f_index == -1:
		sleep(3)
		msg = messagebox.askretrycancel("Warning", "We can't recognise your fingerprint.")
		if msg:
			return fingerprint(uid)
		return mainWindow() 
	print(uid,f_index)	
	cur.execute('SELECT * FROM electoral_roll WHERE aadhar_uid=%s AND fingerprint_index=%s',(uid,f_index))
	res = cur.fetchone()
	if res== None:
		io.output(buzzer,io.HIGH)
		messagebox.showerror("ERROR", "Bogus Vote") 
		sleep(5)
		io.output(buzzer,io.LOW)
		return mainWindow()
	if res[7] != -1:
		messagebox.showinfo("Information", "You have aldready casted your Vote.")
		return mainWindow()
	voter_details(res)

def voter_details(res):
	l_clear()
	Header = Label(root, text = "Voter Details",font = "bold")
	Header.place(relx = 0.45 , rely=0.05)
	Name = Label(root, text ="Name: "+ res[2], font = "bold")
	Name.place(relx = 0.1 , rely=0.2)
	Age = Label(root, text = "Age: "+ str(res[3]), font = "bold")
	Age.place(relx = 0.1 , rely=0.3)
	Gender = Label(root, text = "Gender: "+ res[4], font = "bold")
	Gender.place(relx = 0.1 , rely=0.4)
	Uid = Label(root, text = "Aadhar Number: "+ res[0], font = "bold")
	Uid.place(relx = 0.1 , rely=0.5)
	Vid = Label(root, text = "Voter-ID Number: "+ res[1], font = "bold")
	Vid.place(relx = 0.1 , rely=0.6)
	Address = Label(root, text = "Address: "+ res[5], font = "bold")
	Address.place(relx = 0.1 , rely=0.7)
	button = Button(text="Proceed",fg="red",bg="yellow",command=lambda : candidate_list(res[0]))
	button.place(relx = 0.9,rely = 0.9 ,anchor=SE)
	l.extend([Header,Name,Age,Gender,Uid,Vid,Address,button])

def candidate_list(uid):
	l_clear()
	v = StringVar(root, "1") 
	  
	# Dictionary to create multiple buttons 
	values = {"DMK  - M.K Stalin" : "1", 
	          "ADMK - Edapadi K.Palaniswamy" : "2", 
	          "Naam Thamizhar - Seeman" : "3", 
	          "Makkal Neethi Maiyam - Kamal Hassan" : "4", 
	          "Independent Candidate - Manoj Kumar" : "5"} 
	  
	# Loop is used to create multiple Radiobuttons 
	# rather than creating each button separately 
	for (text, value) in values.items(): 
	    rb = Radiobutton(root, text = text, variable = v, value = value)
	    rb.pack(side = TOP, ipady = 5)
	    l.append(rb)
	button = Button(text="Vote",fg="red",bg="yellow",command=lambda : vote(uid,v.get()))
	button.place(relx = 0.9,rely = 0.9 ,anchor=SE)
	l.append(button)


def vote(v,uid):
	l_clear()
	b = messagebox.askquestion("Vote", "Are you sure to proceed with your vote?")

	if b == "yes":
		cur.execute('UPDATE electoral_roll SET vote=%s WHERE aadhar_uid=%s',(v,uid))
		conn.commit()
		sleep(2)
		messagebox.showinfo("Information", "Your vote has been casted successfully.")
		return mainWindow() 
	else:
		candidate_list()

def trylogin(entry1,entry2):
    Login=entry1.get()
    password = entry2.get()
    if (Login == 'mk' and  password == 'thedon'):
        messagebox.showinfo('info','Correct Login')
    else:
        messagebox.showinfo('info','Invalid Login')

def admin():
	l_clear()
	menubar = Menu(root)
	menubar.add_command(label="Vote",command=mainWindow)
	root.config(menu=menubar)

	Log = Label(root,text = 'Login:')
	Log.place(relx=0.485,rely= 0.4,anchor='se')
	entry1 = Entry(root)
	entry1.place(relx=0.5,rely= 0.4,anchor='sw')

	pswrd = Label(root,text = 'Password: ')
	pswrd.place(relx=0.49,rely= 0.45,anchor='ne')
	entry2 = Entry(root)
	entry2.place(relx=0.5,rely= 0.45,anchor='nw')

	btn = Button(root, text = 'Login',command = lambda :trylogin(entry1,entry2))
	btn.place(relx=0.52,rely= 0.555,anchor='s')
	l.extend([menubar,Log,entry1,entry2,pswrd,btn])

def adminRights():
	l_clear()
		

# Initializing and connecting to the database

conn = psycopg2.connect(
    host="ec2-54-159-113-254.compute-1.amazonaws.com",
    database="d1grhha61ks3og",
    user="cwwudhhqqxpoeo",
    password="8d76e80f38062331d9a63fef8c4a04b1b736d8b148d014acb8984709c08c52f2")

cur = conn.cursor()


mainWindow()
# candidate_list()
root.mainloop()





#     postgres://cwwudhhqqxpoeo:8d76e80f38062331d9a63fef8c4a04b1b736d8b148d014acb8984709c08c52f2@ec2-54-159-113-254.compute-1.amazonaws.com:5432/d1grhha61ks3og
