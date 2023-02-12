import random
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

address = "127.0.0.1"
port = random.randint(10000,50000)
NB_USER=1