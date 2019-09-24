from kryptonite import *
from getpass import getpass
import os, glob
from shutil import rmtree


fs_loc = "./kryp_fs/"

print("Kryptonite Interface v0.1")

fs = CryptFS(getpass(), fs_loc)

open_dirs = {}
cwd = '/'

def ls(d = None):
    if d==None:
        d = cwd
    else:
        if not d.startswith('/'):
            d='/'+d
        if not d.endswith('/'):
            d+='/'
    matching = d[1:]
    ln = len(matching)
    listed_subdirs = []
    for i in fs.filenames:
        if i.startswith('/'):
            i = i[1:]
        if i.startswith(matching):
            i = i[ln:]
            l = i.find('/')
            if l!=-1:
                i = i[:l]
                if not i in listed_subdirs:
                    listed_subdirs.append(i)
                    yield i
def cpo(realdir, d=None):
    if d==None:
        d = cwd
    elif not d.endswith('/'):
        d+='/'
    for i in ls(d):
        path = os.path.join(realdir, i)
        fs.cpout(d+i, path)
        #print(d+i, path)
def cpi(realdir, d=None):
    if d==None:
        d = cwd
    elif not d.endswith('/'):
        d+='/'
    files = [f for f in glob.glob(realdir + "/**/*", recursive=True)]
    for i in files:
        if os.path.isfile(i):
            path = d+os.path.relpath(i, realdir)
            fs.cpin(i, path)
def opendir(realdir):
    global open_dirs
    absdir = os.path.abspath(realdir)
    if absdir in open_dirs.keys():
        print("Error: {} is already opened at {}!".format(open_dirs[absdir], realdir))
        return
    os.makedirs(realdir, exist_ok=True)
    if not os.path.isdir(absdir):
        print("Error: {} is not a valid real path!".format(realdir))
        return
    cpo(realdir, cwd)
    open_dirs[absdir] = cwd
def closedir(realdir):
    global open_dirs
    absdir = os.path.abspath(realdir)
    if not absdir in open_dirs.keys():
        print("Error: {} is not a mount point!".format(realdir))
        return
    cpi(realdir, open_dirs[absdir])
    open_dirs.pop(absdir)
    rmtree(absdir)
    
while True:
    inp = input("kryptonite: {} >".format(cwd))
    tokens = inp.split(' ')

    cmd = tokens[0]
    tokens = tokens[1:]

    if cmd=='ls':
        if len(tokens)>0:
            d = tokens[0]
        else:
            d = cwd
        for i in ls(d):
            print(i)
    elif cmd=='cd':
        if len(tokens)<1:
            cwd = '/'
        else:
            cwd = tokens[0]
            if not cwd.startswith('/'):
                cwd='/'+cwd
            if not cwd.endswith('/'):
                cwd+='/'
    elif cmd=='open':
        if len(tokens)<1:
            print("Usage: open realdir")
            print("Opens the current working directory in a decrypted filesystem")
            continue
        opendir(tokens[0])
    elif cmd=='close':
        if len(tokens)<1:
            print("Usage: close realdir")
            print("Closes the current working directory in a decrypted filesystem")
            continue
        closedir(tokens[0])
    elif cmd=='cpo':
        if len(tokens)<1:
            print("Usage: cpo realdir")
            print("Copies the current working directory to a decrypted filesystem")
            continue
        cpi(tokens[0])
    elif cmd=='closeall':
        # open_dirs keysize will change during loop, so get all keys before execution
        # to prevent crash
        for i in list(open_dirs.keys()):
            print("Closing {}...".format(i))
            closedir(i)
    elif cmd=='die':
        # open_dirs keysize will change during loop, so get all keys before execution
        # to prevent crash
        for i in list(open_dirs.keys()):
            print("Closing {}...".format(i))
            closedir(i)
        print("Shutting down...")
        fs.break_instance()
        break
        
    elif cmd=='help':
        print("""Commands:
  ls [dir] : default to cwd
  cd [dir] : default to /
  open realdir
  close realdir
  cpo realdir
  closeall
  die
  help""")
    else:
        print("Unknown command: {}.  Type 'help' for a list of commands.".format(cmd))
        