# Python Keylogger

This project was carried out as a Master's Thesis for the Camilo José Cela University, in order to obtain the Master's Degree in Cybersecurity.

--------------------------------------
USAGE:
        keylogger.py time_interval --local [path] | --remote host port

Options:

time_interval   Time interval in between writing/sending the log.

--local         Use local execution (write log locally). /n

[path]          Path to save the log (local execution).

--remote        Use remote execution (send the log to web server).

host:           Host (ip address) to send the log to (remote execution).

port            Post to send the log to (remote execution).

--------------------------------------

When using local mode and no [path] is specified, it defaults to the temp folder of the OS.
