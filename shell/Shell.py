import os, sys, time, re

# Replace the current process with "ls" command
#os.execve("/bin/ls", "ls", "-l")

#need the read to break on lines that have . |  
#We want it to acknowlage . to be a file.  Ideally we have something along the lines of a dictionary with some basics files types such as 
# .txt .py 

#then we need | to register as a pipe

#so i propose that we do the swtich from hell //edit the if statment from hell lol
#something along the lines  if | in data.encode then

def shellExec(data):
     
    pid = os.getpid()

    os.write(1, ("About to fork (pid:%d)\n" % pid).encode())

    rc = os.fork()

    if rc == 0: # child process has been created 
        
        
        args = [data.decode().strip()]
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            #os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())  #This is just the line that allows use to see which path the child is attemping to exec
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly

        os.write(2, ("command not found\n").encode())
        sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                    (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                    childPidCode).encode())

    os.write(2, ("fork failed, returning %d\n" % rc).encode())
    sys.exit(1)
"""
def shellPipe(data):
     for dir in re.split("|", data):
"""
        

while(True):

    data = os.read(0,100)

    if "|" in data.decode().strip():
        print("lol that funny")
            

    if("exit" in data.decode().strip()):
            print("exiting")
            sys.exit(0)
    
    shellExec(data)



    
