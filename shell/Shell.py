import os, sys, re

# Replace the current process with "ls" command
#os.execve("/bin/ls", "ls", "-l")

#need the read to break on lines that have . |  
#We want it to acknowlage . to be a file.  Ideally we have something along the lines of a dictionary with some basics files types such as 
# .txt .py 

#then we need | to register as a pipe

#so i propose that we do the swtich from hell //edit the if statment from hell lol
#something along the lines  if | in data.encode then

def shellExec(data):

    #data handler
    wait = True
    if("&" in data):
        data.remove('&')
        print(data)
        wait = False
     
    pid = os.getpid()

    #os.write(1, ("About to fork (pid:%d)\n" % pid).encode())

    rc = os.fork()

    if rc == 0: # child process has been created 
        
        #TODO: go through, find program is path var first the
        args = data
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())  #This is just the line that allows use to see which path the child is attemping to exec
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly

        os.write(2, ("command not found\n").encode())
        sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                    (pid, rc)).encode())
        if(wait == True):
            os.write(1, ("Parent: i am waiting on the child\n").encode())
            childPidCode = os.wait()
            os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                    childPidCode).encode())


''' single pipe
def shellPipe(data, prev_read):
    #pwd | wc
    read_fd, write_fd = os.pipe()
    

    
    pipeLocations = [i for i, pipes in enumerate(data) if pipes == '|']
    print(data[:pipeLocations[0]])
    currentData = data[:pipeLocations[0]]
    data = data[pipeLocations[0]+1:]
    
    print(pipeLocations)

    child1 = os.fork()  
    

    if child1 == 0: # child process has been created 
        
        #TODO: go through, find program is path var first the
        args = currentData
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            full_path = os.path.join(dir, args[0])
            os.write(1, ("Child:  ...trying to exec %s\n" % full_path).encode())

            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                os.dup2(write_fd,1)
                os.close(write_fd)
                os.execve(full_path, args, os.environ) 

                break                  

        os.write(2, ("command not found\n").encode())
        sys.exit(1)                 # terminate with error

    child2 = os.fork() 

    if child2 == 0: # child process has been created 
        
        #TODO: go through, find program is path var first the
        args = data
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            full_path = os.path.join(dir, args[0])
            os.write(1, ("Child:  ...trying to exec %s\n" % full_path).encode())

            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                os.dup2(read_fd, 0)      # redirect stdin to pipe's read end
                os.close(write_fd)       # not used in this child
                os.close(read_fd) 
                os.execve(full_path, args, os.environ) 

                break                  

        os.write(2, ("command not found\n").encode())
        sys.exit(1)  
                        
    os.close(write_fd)
    os.close(read_fd)

    os.waitpid(child1, 0)
    os.waitpid(child2, 0)


'''

def shellPipe(data):
    prev_read = None
    while '|' in data:
        pipe_index = data.index('|')
        currentData = data[:pipe_index]
        data = data[pipe_index + 1:] 
        read_fd, write_fd = os.pipe()
        child = os.fork()  
        if child == 0: # child process has been created 
        
            args = currentData
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                full_path = os.path.join(dir, args[0])

                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    if prev_read is not None:
                        os.dup2(prev_read, 0)  
                        os.close(prev_read)
                    os.dup2(write_fd, 1)   
                    os.close(write_fd)
                    os.close(read_fd)
                    os.execve(full_path, args, os.environ) 
                                      

            os.write(2, ("command not found\n").encode())
            sys.exit(1)                 # terminate with error
        else:
            
            if prev_read is not None:
                 os.close(prev_read)
            os.close(write_fd)
            prev_read = read_fd  # Set for the next command  
            os.waitpid(child, 0)
        


    # Now handle the final command (no more pipes)
    pid = os.fork()
    
    if pid == 0:
        if prev_read is not None:
            os.dup2(prev_read, 0)
            os.close(prev_read)

        for dir in os.environ['PATH'].split(':'):
            #print(data)
            full_path = os.path.join(dir, data[0])
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                os.execve(full_path, data, os.environ)

        os.write(2, b"Command doenst exist\n")
        sys.exit(1)
    else:
        if prev_read is not None:
            os.close(prev_read)
        os.waitpid(pid, 0)








#To save myself pain and suffering
def dataCheck(data):
    correctDataLocations = [i for i, quotes in enumerate(data) if '"' in quotes]
    start = correctDataLocations[0]
    end = correctDataLocations[1] 
    correctData = []
    correctString = ""
    while (len(correctDataLocations) > 0):
        start = correctDataLocations[0]
        end = correctDataLocations[1] 
        correctData += data[:start]
        correctString = ""
        while(start != end+1):
            correctString += data[start] + " "
            start+=1
        correctData.append(correctString.strip())
        correctDataLocations = correctDataLocations[end+1:]
    correctData += data[end+1:]
    return correctData



    
def redirect(data):
    #pwd > test.txt

    #redirect and overwrite 
    if(">" in data):
        command, file = ("".join(data)).split(">")
        print(command)
        print(file)

        child = os.fork()  
        

        if child == 0: # child process has been created 
            
            #TODO: go through, find program is path var first the
            args = command
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                full_path = os.path.join(dir, args)
                os.write(1, ("Child:  ...trying to exec %s\n" % full_path).encode())

                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    output_fd = os.open(file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
                    os.dup2(output_fd, 1)
                    os.close(output_fd)
                    os.execve(full_path, [args], os.environ) 

                    break                  

            os.write(2, ("command not found\n").encode())
            sys.exit(1)                 # terminate with error

        os.waitpid(child, 0)

    #redirect and append 
    elif(">>" in data):
            command, file = ("".join(data)).split(">>")
            print(command)
            print(file)

            child = os.fork()  
            

            if child == 0: # child process has been created 
                
                #TODO: go through, find program is path var first the
                args = command
                for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                    full_path = os.path.join(dir, args)
                    os.write(1, ("Child:  ...trying to exec %s\n" % full_path).encode())

                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        output_fd = os.open(file, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
                        os.dup2(output_fd, 1)
                        os.close(output_fd)
                        os.execve(full_path, [args], os.environ) 

                        break                  

                os.write(2, ("command not found\n").encode())
                sys.exit(1)                 # terminate with error

            os.waitpid(child, 0)
        
    #redirect and take stdin 
    elif("<" in data):
        command, file = ("".join(data)).split("<")
        print(command)
        print(file)

        child = os.fork()  
        

        if child == 0: # child process has been created 
            
            #TODO: go through, find program is path var first the
            args = command
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                full_path = os.path.join(dir, args)
                os.write(1, ("Child:  ...trying to exec %s\n" % full_path).encode())

                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    input_fd = os.open(file, os.O_RDONLY)
                    os.dup2(input_fd, 0)
                    os.close(input_fd)
                    os.execve(full_path, [args], os.environ) 

                    break                  

            os.write(2, ("command not found\n").encode())
            sys.exit(1)                 # terminate with error

        os.waitpid(child, 0)



'''
Lets set a scope of what we will be 
We will deal with
    - pipe() //Done
    - fork() //Done
    - dup() or dup2() //Done
    - execve() (you cannot use execvp) //Done
    - wait() //Done
    - open() and close() //Done
    - chdir() //Done
'''
 
while(True):
    #1. Prints a prompt string specified by shell variable PS1 when expecting a command (if PS1 is not set, the default prompt should be "$ ").
    #Sets and writes PS1 to via writing it to the screen and prints CWD and PS1.  I didnt do "$ " but it can be set if need be cd 
    os.write(1, os.environ.get("PS1", os.getcwd() + " -> ").encode()) 

    data = [dir.strip() for dir in re.split(r"[\s]+", os.read(0,100).decode().strip())]
    if '"' in data:
        data = dataCheck(data)
    
    print (data)

    if "cd" == data[0]:
        os.chdir(data[1])

    elif "exit" in data:
        print("Goodby")
        sys.exit(1)  

    elif "|" in data:
        shellPipe(data)

    elif ">" or ">>" or "<" in data:
        redirect(data)


    elif ("|" not in data and "cd" not in data):
        if('"' in data):
            data = dataCheck(data)
        shellExec(data)

