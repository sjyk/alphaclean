import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

parentdir = os.path.dirname(currentdir)

sys.path.insert(0,parentdir)


import logging 
import string
import random

logfilename =  ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)) +'.log'

logging.basicConfig(level=logging.DEBUG, filename=logfilename) 

logging.warn("Logs saved in " + logfilename)