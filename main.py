import multiprocessing
import os, signal
import socket
import time
import random
import threading
import sys 
import concurrent.futures      

class User(multiprocessing.Process):
    def __init__(self,id,address,port):
        super().__init__()
        self.id=id
        self.amount_ETH=0
        self.port=port
        self.address=address
        self.amount_DAI=0
        self.amount_LPToken=0
        self.client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.address, self.port))

    def send(self,msg):
        self.client_socket.sendall(str(msg).encode())



    def run(self):
        self.send(self.id)
        time.sleep(random.random())
        self.send(self.id)



    def addLiq(self):
        a=1
    
    def remLiq(self):
        a=1

class Pool(multiprocessing.Process):
    def __init__(self,address,port):
        super().__init__()
        self.amount_ETH=0
        self.price_ETH=1500
        self.price_DAI=1
        self.fee=0
        self.amount_DAI=0

        self.address = address
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((address, port))
        self.server.listen(1)
        self.server.setblocking(True)

        # signal.signal(signal.SIGINT, self.stop)

    def run(self):
         with concurrent.futures.ThreadPoolExecutor(max_workers=NB_USER) as executor:
            while True:
                conn, addr = self.server.accept()
                executor.submit(self.userHandler, conn, addr)
    # def stop(self,signum, frame):
    #     self.server.close()
    
    def userHandler(self,conn, addr):
        with conn:
            print(f'Connected by {addr}')
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f'Received data from {addr}: {data.decode()}')

def interrupt_handler(signal, frame):
    print("Interrupted")
    sys.exit("FIN")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, interrupt_handler)
    address = "127.0.0.1"
    port = random.randint(10000,50000)
    NB_USER=3
    
    Process_Pool = Pool(address,port)
    Process_Pool.start()
    time.sleep(0.5)

    user = [ User(i,address,port).start() for i in range(NB_USER)]
    

    #Process_Pool.join()
    #Process_User_1.join()