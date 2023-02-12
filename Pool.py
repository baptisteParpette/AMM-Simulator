import multiprocessing
import socket
import concurrent.futures
import math
import matplotlib.animation as animation
from var import *

class Pool(multiprocessing.Process):
    def __init__(self,address,port,shared):
        super().__init__()
        self.amount_ETH=0
        self.price_ETH=0
        self.price_DAI=1
        self.shared=shared
        self.fee=0
        self.amount_DAI=0
        self.LPsupply=0
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
                        
                        recv_eth=eval(dataList[2])
                        recv_dai=eval(dataList[3])
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
                        recv_eth=eval(dataList[2])
                        recv_dai=eval(dataList[3])
                        
                        liquidity = math.sqrt(self.amount_DAI*self.amount_ETH)
                        if(liquidity!=0):
                            tokenToMint=(recv_eth/self.amount_ETH)*self.LPsupply
                            self.amount_DAI=self.amount_DAI+recv_dai
                            self.amount_ETH=self.amount_ETH+recv_eth
                            self.LPsupply=self.LPsupply+tokenToMint
                            conn.sendall(str(tokenToMint).encode())
                        else:
                            self.amount_DAI=self.amount_DAI+recv_dai
                            self.amount_ETH=self.amount_ETH+recv_eth
                            self.LPsupply=100
                            conn.sendall("100".encode()) # For the first LP, I decide to give him 100LP token


                    case "REM_LP":
                        LPamout_User=eval(dataList[2])
                        ethToSend=self.amount_ETH*(LPamout_User/self.LPsupply)
                        daiToSend=self.amount_DAI*(LPamout_User/self.LPsupply)
                        self.amount_ETH=self.amount_ETH-ethToSend
                        self.amount_DAI=self.amount_DAI-daiToSend
                        msg=str(ethToSend)+";"+str(daiToSend)

                        self.LPsupply=self.LPsupply-LPamout_User
                        conn.sendall(str(msg).encode())
                    case _:
                        print("err")
                self.shared[0]=self.amount_DAI
                self.shared[1]=self.amount_ETH