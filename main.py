import multiprocessing
import os,signal
import time
import sys 
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.animation as animation
from Pool import Pool
from User import User
from var import *


def interrupt_handler(signal, frame):
    print("Interrupted")
    sys.exit("FIN")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, interrupt_handler)
    
    shared_memory_pool=multiprocessing.Array('d',range(10))
    
    Process_Pool = Pool(address,port,shared_memory_pool)
    Process_Pool.start()
    time.sleep(0.5)

    user = [ User(i,address,port,shared_memory_pool).start() for i in range(NB_USER)]
    

    #Process_Pool.join()
    #Process_User_1.join()