import multiprocessing
import os, signal
import socket
import time
import random
import threading
import sys 
import concurrent.futures
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.animation as animation

class User(multiprocessing.Process):
    def __init__(self,id,address,port,shared):
        super().__init__()
        self.id=id
        self.shared=shared
        self.amount_ETH=100.0
        self.port=port
        self.address=address
        self.amount_DAI=5000.0
        self.amount_LPToken=0
        self.client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.address, self.port))
        self.poolEthHisto=[]
        self.poolDaiHisto=[]
        self.meDaiHisto=[]
        self.meEthHisto=[]
        self.prix=[]

    def run(self):
        #fig, axs = plt.subplots(3,3)
                    


        #EXAMPLE MSG : "{ID};{SWAP};{ETH_QUANTITY};{DAI_QUANTTITY}"
        #EXAMPLE MSG : "{ID};{ADD_LP};{ETH_QUANTITY};{DAI_QUANTTITY}" ! ATTENTION A ENVOYER 50/50
        #EXAMPLE MSG : "{ID};{REM_LP};{LPTOKEN_QUANTITY}"

        # self.poolDaiHisto.append(self.shared[0])
        # self.poolEthHisto.append(self.shared[1])
        # self.meDaiHisto.append(self.amount_DAI)
        # self.meEthHisto.append(self.amount_ETH)
        # self.prix.append(self.shared[0]/self.shared[1])

        # for i in tqdm(range(100)):
        #     self.swap("ETH",1)
        #     self.poolDaiHisto.append(self.shared[0])
        #     self.poolEthHisto.append(self.shared[1])
        #     self.meDaiHisto.append(self.amount_DAI)
        #     self.meEthHisto.append(self.amount_ETH)
        #     self.prix.append(self.shared[0]/self.shared[1])


        # axs[1,1].plot(self.poolDaiHisto,self.poolEthHisto)
        # axs[0,0].plot(self.meDaiHisto)
        # axs[1,0].plot(self.meEthHisto)
        # axs[2,0].plot(self.prix)
        # plt.show()


            
            
            
            
            # msg="0;SWAP;+1;-1600"
            # self.send(msg)

            # time.sleep(3)

            # msg="0;SWAP;+2;-3200"
            # self.send(msg)

            # time.sleep(3)

            # msg="0;SWAP;-5;-1600"
            # self.send(msg)
            return

    def swap(self,peer,quantity):
        if peer == "ETH":
            self.amount_ETH-=quantity
            anticipation = abs(  ((self.shared[1]*self.shared[0])  /  (self.shared[1]+quantity))  -self.shared[0])
            #print(f'{quantity} $ETH  <=>  {round(anticipation,2)} $DAI')
            msg=f'{self.id};SWAP;{quantity};0'
            return_data = eval(self.send(msg))
            self.amount_DAI+=return_data
            if abs(return_data-anticipation)>10**(-2):
                print(f'SLIPPAGE ! {return_data=}   {anticipation=}')       
        
        if peer == "DAI":
            self.amount_DAI-=quantity
            anticipation = abs(  ((self.shared[1]*self.shared[0])  /  (self.shared[0]+quantity))  -self.shared[1])
            #print(f'{quantity} $DAI  <=>  {round(anticipation,2)} $ETH')
            msg=f'{self.id};SWAP;0;{quantity}'
            return_data = eval(self.send(msg))
            self.amount_ETH+=return_data
            if abs(return_data-anticipation)>10**(-2):
                print(f'SLIPPAGE ! A CALCULER !!!') 

    def send(self,msg):
        self.client_socket.sendall(str(msg).encode())
        data = self.client_socket.recv(1024)
        return data.decode()

    def addLiq(self):
        a=1
    
    def remLiq(self):
        a=1

class Pool(multiprocessing.Process):
    def __init__(self,address,port,shared):
        super().__init__()
        self.amount_ETH=100
        self.price_ETH=1500
        self.price_DAI=1
        self.shared=shared
        self.fee=0
        self.amount_DAI=50000
        self.address = address
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((address, port))
        self.server.listen(1)
        self.server.setblocking(True)
        self.shared[0]=self.amount_DAI
        self.shared[1]=self.amount_ETH

    def run(self):
         with concurrent.futures.ThreadPoolExecutor(max_workers=NB_USER) as executor:
            while True:
                conn, addr = self.server.accept()
                executor.submit(self.userHandler, conn, addr)
    
    def userHandler(self,conn, addr):
        with conn:
            #print(f'Connected by {addr}')
            while True:
                #print(f'{round(self.amount_ETH,2)}  {round(self.amount_DAI,2)}')
                data = conn.recv(1024)
                if not data:
                    break
                dataList=data.decode().split(";")
                #[  ID,   SWAP,   ETH_QUANTITY,   DAI_QUANTTITY   ]
                #[  ID,   ADD_LP, ETH_QUANTITY,   DAI_QUANTTITY   ]
                #[  ID,   REM_LP, LPTOKEN_QUANTITY                ]
                match dataList[1]:
                    case "SWAP":
                        
                        recv_eth=int(dataList[2])
                        recv_dai=int(dataList[3])
                        if recv_eth!=0:
                            dai_swapped = abs(((self.amount_DAI*self.amount_ETH)/(self.amount_ETH+recv_eth))-self.amount_DAI)
                            self.amount_ETH+=recv_eth
                            self.amount_DAI-=dai_swapped
                            conn.sendall(str(dai_swapped).encode())
                            
    
                        if recv_dai!=0:
                            
                            eth_swapped = abs(((self.amount_DAI*self.amount_ETH)/(self.amount_DAI+recv_dai))-self.amount_ETH)
                            self.amount_DAI+=recv_dai
                            self.amount_ETH-=eth_swapped
                            conn.sendall(str(eth_swapped).encode())

                    case "ADD_LP":
                        conn.sendall(str("ADD OK").encode())
                        self.amount_DAI+=int(dataList[3])
                        self.amount_ETH+=int(dataList[2])
                    case "REM_LP":
                        conn.sendall(str("REM OK").encode())
                    case _:
                        print("err")
                self.shared[0]=self.amount_DAI
                self.shared[1]=self.amount_ETH
                
                






def interrupt_handler(signal, frame):
    print("Interrupted")
    sys.exit("FIN")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, interrupt_handler)
    address = "127.0.0.1"
    port = random.randint(10000,50000)
    NB_USER=1
    shared_memory_pool=multiprocessing.Array('d',range(10))
    
    Process_Pool = Pool(address,port,shared_memory_pool)
    Process_Pool.start()
    time.sleep(0.5)

    user = [ User(i,address,port,shared_memory_pool).start() for i in range(NB_USER)]
    

    #Process_Pool.join()
    #Process_User_1.join()