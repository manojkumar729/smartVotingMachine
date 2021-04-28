import time
import psycopg2
from pyfingerprint.pyfingerprint import PyFingerprint

def enroll_fingerprint():
    ## Enrolls new finger

    ## Tries to initialize the sensor
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)

    ## Tries to enroll new finger
    try:
        print('Waiting for finger...')

        ## Wait that finger is read
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        ## Checks if finger is already enrolled
        result = f.searchTemplate()
        positionNumber = result[0]

        if ( positionNumber >= 0 ):
            print('Template already exists at position #' + str(positionNumber))
            exit(0)

        print('Remove finger...')
        time.sleep(2)

        print('Waiting for same finger again...')

        ## Wait that finger is read again
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 2
        f.convertImage(0x02)

        ## Compares the charbuffers
        if ( f.compareCharacteristics() == 0 ):
            raise Exception('Fingers do not match')

        ## Creates a template
        f.createTemplate()

        ## Saves template at new position number
        positionNumber = f.storeTemplate()
        print('Finger enrolled successfully!')
        print('New template position #' + str(positionNumber))
        return positionNumber

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)

def register_voter():
    uid = input("Enter voter's unique aadhar id: ")
    voter_id = input("Enter voter's voter id number: ")
    name = input("Enter voter's name: ")
    age = int(input("Enter voter's age: "))
    gender = input("Enter voter's gender (0/1): ")
    address = input("Enter voter's address: ")
    f_index = int(enroll_fingerprint())
    cur.execute('INSERT INTO electoral_roll(aadhar_uid,voter_id_num,name,age,gender,address,fingerprint_index) VALUES(%s,%s,%s,%s,%s,%s,%s)',(uid,voter_id,name,age,gender,address,f_index))
    conn.commit()


conn = psycopg2.connect(
    host="ec2-54-159-113-254.compute-1.amazonaws.com",
    database="d1grhha61ks3og",
    user="cwwudhhqqxpoeo",
    password="8d76e80f38062331d9a63fef8c4a04b1b736d8b148d014acb8984709c08c52f2")

cur = conn.cursor()

while 1:
    response = input("Register new Candidate?(yes/no)")
    if response == "yes":
        register_voter()
    else:
        cur.close()
        exit(1)
