#!/usr/bin/env python

'''
fcsched.py
fcsched is a python utility that queries a predict server and schedules the use 
of the fcdec utilities for each pass of the FUNcube-1 (AO-73) satellite.

https://github.com/g0hww/fcsched

This file is part of fcsched.

fcsched is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

fcsched is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with fcsched.  If not, see <http://www.gnu.org/licenses/>.

Copyright (C) 2013. Darren Long, G0HWW. darren.long@mac.com
'''

import pexpect
import time
import sys
import socket
import binascii
import os

predict_server_host = "localhost"
predict_server_port = "1210"
fcd_sequencer_host  = "localhost"
fcd_sequencer_port  = 12345
funcube_name		= "39444" # funcube catalog id

if __name__ == '__main__':

	predict_client = pexpect.spawn("nc -u "+predict_server_host+" "+predict_server_port)
	
	while(True):
		predict_client.sendline("PREDICT "+funcube_name)
		time.sleep(1.0)
		predict_client.timeout=2.0	
		res=predict_client.expect([binascii.unhexlify("0A1A"), pexpect.TIMEOUT, pexpect.EOF])
		if res == 0:
			print predict_client.before
			num_lines =  len(predict_client.before.split(os.linesep))
			time_aos = predict_client.before.split(os.linesep)[1].split(" ")[0]
			print "Next AOS at " + time_aos
			time_aos = float(time_aos)
			time_los = predict_client.before.split(os.linesep)[num_lines-1].split(" ")[0]
			print "Then LOS at " + time_los
			time_los = float(time_los)
			pass_duration = int(time_los - time_aos + 1)
			print "Pass duration is " + str(pass_duration) + " secs."
			time_now = time.time()
			print "Time now is " + str(time_now)
			time_to_sleep = time_aos - time_now;
			if(time_to_sleep < 0):
				time_to_sleep = 0
				pass_duration = int(time_los - time_now)
				print "Satellite is visible."
				print "Pass remaining is " + str(pass_duration) + " secs."
			if(time_to_sleep > 0):				
				print "Sleeping for " + str(time_to_sleep) + " seconds."
			time.sleep(time_to_sleep)
			cmd = "start +"+str(pass_duration)
			print "Sending command to fcdec: " + cmd
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((fcd_sequencer_host, fcd_sequencer_port))
			s.send(cmd)
			s.close()
			print "Sleeping for " + str(pass_duration) + " seconds."			
			time.sleep(float(pass_duration))
		else:
			print "ERROR: Unable to get response from predict server!"
			exit()
	predict_client.close()
	
	
