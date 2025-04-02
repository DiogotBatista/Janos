import os
import sys


sys.path.insert(0, os.path.dirname(__file__))


import janus.wsgi

application = janus.wsgi.application