from time import sleep
from tkinter import*
from tkinter import messagebox 
import psycopg2
import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint
import PIL 
from PIL import Image,ImageTk
import RPi.GPIO as io

buzzer = 8

io.setmode(io.BOARD)
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
		acdbacyScore = result[1]

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
	
	uidLb =Label(root,text="Enter your Aadhaar Number: ",fg="black")
	uidLb.place(relx = 0.5, rely = 0.4,anchor = 'ne')

	uid =Entry(root)
	uid.place(relx = 0.5, rely = 0.4,anchor ='nw')

	button = Button(text="Proceed",fg="red",bg="blue",command=lambda: fingerprint(uid.get()))
	button.place(relx = 0.5, rely = 0.55,anchor ='s')
	
	l.extend([menubar,uidLb,uid,button])

def fingerprint(uid):
	
	l_clear()

	img1 = Image.open("fingerprint.png")
	img = ImageTk.PhotoImage(img1)
	fImage = Label(root,image=img)
	fImage.place(relx=.5,rely=.5,anchor="center")

	title = Label(root,text="Fingerprint Verification",fg="white", bg="#26232a",font = "bold")
	title.place(relx = 0.5, rely = 0.1,anchor = 'center')

	f_index = search()

	l.extend([fImage, title])

	if f_index == -1:
		
		sleep(3)
		
		msg = messagebox.askretrycancel("Warning", "We can't recognise your fingerprint.")
		
		if msg:
			return fingerprint(uid)
		return mainWindow() 
	
	db.execute('SELECT * FROM electoral_roll WHERE aadhar_uid=%s AND fingerprint_index=%s',(uid,f_index))
	res = db.fetchone()
	
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
	  
	db.execute('SELECT * FROM vote_counting');
	candidates = db.fetchall();

	# Dictionary to create multiple buttons 
	values = {}
	for i in candidates:
		values[f"{i[1]} - {i[2]}"] = i[0]
	# values = {"DMK  - M.K Stalin" : "1", 
	#           "ADMK - Edapadi K.Palaniswamy" : "2", 
	#           "Naam Thamizhar - Seeman" : "3", 
	#           "Makkal Neethi Maiyam - Kamal Hassan" : "4", 
	#           "Independent Candidate - Manoj Kumar" : "5"} 
	  
	# Loop is used to create multiple Radiobuttons 
	# rather than creating each button separately 
	for (text, value) in values.items(): 
	    
	    rb = Radiobutton(root, text = text, variable = v, value = value)
	    rb.pack(side = TOP, ipady = 5)
	    l.append(rb)
	
	button = Button(text="Vote",fg="red",bg="yellow",command=lambda : vote(int(v.get()),uid))
	button.place(relx = 0.9,rely = 0.9 ,anchor=SE)
	l.append(button)


def vote(v,uid):
	
	l_clear()
	
	b = messagebox.askquestion("Vote", "Are you sure to proceed with your vote?")
	print(v,uid)
	if b == "yes":
		db.execute('UPDATE electoral_roll SET vote=%s WHERE aadhar_uid=%s',(1,uid))
		db.execute('SELECT vote_count FROM vote_counting WHERE id=%s',(v,));
		vc = db.fetchone();
		db.execute('UPDATE vote_counting SET vote_count=%s WHERE id=%s',((vc[0]+1),v))
		db_conn.commit()
		
		sleep(2)
		messagebox.showinfo("Information", "Your vote has been casted successfully.")
		return mainWindow() 
	else:
		candidate_list()

def authenticate(username,password):
	name = username.get()
	password = password.get()
	db.execute('SELECT * FROM users WHERE name=%s AND password=%s',(name,password))
	key = db.fetchone()
	if key:
		adminPanel() 
	else:
		messagebox.showinfo('info','Incorrect Credentials')

def admin():
	
	l_clear()

	menubar = Menu(root)
	menubar.add_command(label="Vote",command=mainWindow)
	root.config(menu=menubar)

	frame = Frame(root, height=400, width=400) 
	frame.place(relx = 0.5, rely = 0.5,anchor = 'center')
  
	Log = Label(frame,text = 'Login:')
	Log.place(relx=0.485,rely= 0.4,anchor='se')

	username = Entry(frame)
	username.place(relx=0.5,rely= 0.4,anchor='sw')

	pswrd = Label(frame,text = 'Password:')
	pswrd.place(relx=0.49,rely= 0.45,anchor='ne')
	password = Entry(frame,show="*")
	password.place(relx=0.5,rely= 0.45,anchor='nw')

	button = Button(frame, text = 'Login',command = lambda :authenticate(username,password))
	button.place(relx=0.60,rely= 0.65,anchor='s')
	
	l.extend([menubar,Log,username,password,pswrd,button])

def adminPanel():
	l_clear()

	db.execute('SELECT * FROM vote_counting')
	row = db.fetchall()
	# row -> individual party details
	# field[0] - id ,field[1] - partyname, field[2] - candidate name, field[3] - age, field[4] - Gender(0 - Male, 1- Female), field[5] - count
	final = "Vote Count Status\n\n\n"
	var = StringVar()
	for field in row:
		final += f'{field[1]} - {field[2]} - {field[5]}\n\n'
	row.sort(key = lambda x: x[5],reverse = True) 
		
	var.set(final)
	statusbar = Label(root, textvariable=var, height = 30, width = 200,fg="black", font=50, bd=1, relief=SUNKEN, anchor="center")
	statusbar.place(relx=0.5,rely = 0.6,anchor = "center")
	button = Button(root,text = 'View Result',command = lambda :result(row[0],row[1]))
	button.pack()
	root.update_idletasks()
	l.extend([statusbar,button])


def result(first,second):
	l_clear()
	final = "Polling Results\n\n\n"
	var = StringVar()
	final += f'Winning Party - {first[1]}\n\nOpposition Party - {second[1]}\n\n'
	var.set(final)
	statusbar = Label(root, textvariable=var, height = 30, width = 200,fg="black", font=50, bd=1, relief=SUNKEN, anchor="center")
	statusbar.place(relx=0.5,rely = 0.6,anchor = "center")
	root.update_idletasks()

# Initializing and db_connecting to the database

db_conn = psycopg2.connect(
    host="ec2-54-159-113-254.compute-1.amazonaws.com",
    database="d1grhha61ks3og",
    user="cwwudhhqqxpoeo",
    password="8d76e80f38062331d9a63fef8c4a04b1b736d8b148d014acb8984709c08c52f2")

db = db_conn.cursor()


# mainWindow()
adminPanel()
root.mainloop()





# postgres://cwwudhhqqxpoeo:8d76e80f38062331d9a63fef8c4a04b1b736d8b148d014acb8984709c08c52f2@ec2-54-159-113-254.compute-1.amazonaws.com:5432/d1grhha61ks3og
