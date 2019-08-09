#!/usr/bin/python
import sys
import os
import logging

#path = '/var/www/FlaskApp/FlaskApp'
#if path not in sys.path:
#        sys.path.append(path)

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/FlaskApp/")

from FlaskApp import app as application
application.secret_key = 'GEOM Cookie Monster'
