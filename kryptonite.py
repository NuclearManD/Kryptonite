from crypt import decrypt1, encrypt1, shortstrhash
import os, random

class CryptFS:
    def __init__(self, password, location="."):
        self.location = os.path.realpath(location)+'/'
        if type(password)==str:
            password=password.encode()
        self.key=password

        if not os.path.isdir(self.location):
            self.broken=False
            os.makedirs(self.location)
            self.filenames = []
        else:
            self.broken=False
            self.filenames = self.read("@filenames")
            if self.filenames==-1:
                self.filenames = []
            else:
                self.filenames = eval(self.filenames)
    def read(self, fn):
        if self.broken:
            return -2
        nfn=shortstrhash(fn+self.key.decode())+".enc"
        p=os.path.join(self.location, nfn)
        if not os.path.isfile(p):
            print(p, "dne")
            return -1

        f=open(p,'rb')
        return decrypt1(f.read(), (self.key+fn.encode())[:32])
    def write(self, fn, data):
        if self.broken:
            return -2
        nfn=shortstrhash(fn+self.key.decode())+".enc"
        p=os.path.join(self.location, nfn)

        f=open(p,'wb')
        f.write(encrypt1(data, (self.key+fn.encode())[:32]))
        f.close()

        if not fn in self.filenames and fn!="@filenames":
            self.filenames.append(fn)
            self.write("@filenames",repr(self.filenames))
        return 0
    def cpin(self, src, dst):
        if self.broken:
            return -2
        f = open(src, 'rb')
        data = f.read()
        f.close()

        self.write(dst, data)
        return 0
    def cpout(self, src, dst):
        if self.broken:
            return -2
        data = self.read(src)
        f=open(dst,'wb')
        f.write(data)
        f.close()
        return 0
    def break_instance(self):
        if self.broken:
            return -2
        # this function tries to make the RAM unusable.  Deletes password and other data byte-by-byte.
        self.key=os.urandom(100)
        for i in range(len(self.filenames)):
            self.filenames[i]=os.urandom(40)
        self.filenames=[]
        self.location="~instance broken~"
        self.broken=True
