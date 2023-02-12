import multiprocessing
import socket
from var import *

class User(multiprocessing.Process):
    def __init__(self,id,address,port,shared):
        super().__init__()
        self.id=id
        self.shared=shared
        self.amount_ETH=100.0
        self.port=port
        self.address=address
        self.amount_LPtoken=0
        self.amount_DAI=5000.0
        self.client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.address, self.port))
        self.poolEthHisto=[]
        self.poolDaiHisto=[]
        self.meDaiHisto=[]
        self.meEthHisto=[]
        self.prix=[]
                #[  ID,   SWAP,   ETH_QUANTITY,   DAI_QUANTTITY   ]
                #[  ID,   ADD_LP, ETH_QUANTITY,   DAI_QUANTTITY   ]
                #[  ID,   REM_LP, LPTOKEN_QUANTITY                ]
    


    def run(self):
        #fig, axs = plt.subplots(3,3)
        time.sleep(1)
        
        for i in range(5):
            print(f'{self.id=} {self.amount_ETH=} {self.amount_DAI=} {self.amount_LPtoken=}')
            self.addLP(1,1500)
            print(f'{self.shared[0]=}   {self.shared[1]=}  ratio:{self.shared[1]/(self.shared[0]+10**(-15))}')
            print(" ")
            time.sleep(0.1)


        self.RemLP(100)

        print(f'{self.id=} {self.amount_ETH=} {self.amount_DAI=} {self.amount_LPtoken=}')
        print(f'{self.shared[0]=}   {self.shared[1]=}  ratio:{self.shared[1]/(self.shared[0]+10**(-15))}')


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

    def RemLP(self,quantity):
        if(quantity<=0 or quantity>self.amount_LPtoken):
            print("Error or not Enough LPToken")
            return
        msg=f'{self.id};REM_LP;{quantity}'
        msg_return=self.send(msg).split(';')
        ETH = eval(msg_return[0])
        DAI = eval(msg_return[1])
        self.amount_LPtoken=self.amount_LPtoken-quantity
        self.amount_ETH=self.amount_ETH+ETH
        self.amount_DAI=self.amount_DAI+DAI

    def addLP(self,qETH,qDAI):
        #print(qDAI,qETH)
        if(qETH>self.amount_ETH or qETH<=0):
            print("Not enough ETH")
            return
        if(qDAI>self.amount_DAI or qDAI<=0):
            print("Not enough DAI")
            return

        if(self.shared[0]*self.shared[1]==0):
            msg=f'{self.id};ADD_LP;{qETH};{qDAI}'
            self.amount_DAI=self.amount_DAI-qDAI
            self.amount_ETH=self.amount_ETH-qETH
            self.amount_LPtoken=self.amount_LPtoken+eval(self.send(msg))
            #print(f'{self.id}  {self.amount_LPtoken=}')

        else:
            ratio_before=self.shared[0]/self.shared[1]
            actual_ratio=qDAI/qETH
            if(actual_ratio==ratio_before):
                self.amount_DAI=self.amount_DAI-qDAI
                self.amount_ETH=self.amount_ETH-qETH
                msg=f'{self.id};ADD_LP;{qETH};{qDAI}'
                self.amount_LPtoken=self.amount_LPtoken+eval(self.send(msg))
                #print(f'{self.id}  {self.amount_LPtoken=}')
            
            if(actual_ratio>ratio_before):
                qDAI=(self.shared[0]*qETH)/self.shared[1]
                qETH=qETH
                self.amount_DAI=self.amount_DAI-qDAI
                self.amount_ETH=self.amount_ETH-qETH
                msg=f'{self.id};ADD_LP;{qETH};{qDAI}'
                self.amount_LPtoken=self.amount_LPtoken+eval(self.send(msg))
                #print(f'{self.id}  {self.amount_LPtoken=}')
            if(actual_ratio<ratio_before):
                qETH=(self.shared[1]*qDAI)/self.shared[0]
                qDAI=qDAI
                self.amount_DAI=self.amount_DAI-qDAI
                self.amount_ETH=self.amount_ETH-qETH
                msg=f'{self.id};ADD_LP;{qETH};{qDAI}'
                self.amount_LPtoken=self.amount_LPtoken+eval(self.send(msg))
                #print(f'{self.id}  {self.amount_LPtoken=}')

    def swap(self,peer,quantity):
        if peer == "ETH":
            if(quantity>self.amount_ETH):
                print("Not enough ETH")
                return
            self.amount_ETH-=quantity
            anticipation = abs(  ((self.shared[1]*self.shared[0])  /  (self.shared[1]+quantity))  -self.shared[0])
            #print(f'{quantity} $ETH  <=>  {round(anticipation,2)} $DAI')
            msg=f'{self.id};SWAP;{quantity};0'
            return_data = eval(self.send(msg))
            self.amount_DAI+=return_data
            if abs(return_data-anticipation)>10**(-2):
                print(f'SLIPPAGE ! {return_data=}   {anticipation=}')       
        
        if peer == "DAI":
            if(quantity>self.amount_DAI):
                print("Not enough DAI")
                return
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