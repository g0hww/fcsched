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

predict_server_host = "soltek.local"
predict_server_port = "1210"
fcd_sequencer_host  = "localhost"
fcd_sequencer_port  = 12345
funcube_name		= "39444" # funcube catalog id

if __name__ == '__main__':
	
    try:
		while(True):
			time_now = time.time()
			print "________________________________________________________________________"
			print "Time now is " + str(time_now)
			# query the predict server	
			predict_client = pexpect.spawn("nc -u "+predict_server_host+" "+predict_server_port)	
			predict_client.sendline("PREDICT "+funcube_name)
			predict_client.timeout=2.0	
			res=predict_client.expect([binascii.unhexlify("0A1A"), pexpect.TIMEOUT, pexpect.EOF])
			if res == 0:
				# we got details of a pass
				print predict_client.before
				num_lines =  len(predict_client.before.split(os.linesep))
				# see if the pass info seems valid
				if num_lines < 3:
					print "ERROR: The predict server made no predictions for the satellite!"
					exit();
				# determine the pass AOS
				time_aos = predict_client.before.split(os.linesep)[1].split(" ")[0]
				print "Next AOS at " + time_aos
				time_aos = float(time_aos)
				# determine the pass LOS
				time_los = predict_client.before.split(os.linesep)[num_lines-1].split(" ")[0]
				print "Then LOS at " + time_los
				time_los = float(time_los)
				# determine the pass duration
				pass_duration = int(time_los - time_aos + 1)
				# see if the pass info seems valid
				if(pass_duration > 0):
					time_now = time.time()
					time_to_sleep = time_aos - time_now;
					# if AOS is in the past ...
					if(time_to_sleep < 0):
						# if LOS is in the past ...
						if(time_now >= time_los):
							# this is a stale prediction, wait for a new one
							print "LOS has occurred already. Sleeping for 30 seconds."
							time.sleep(30.0)
							continue
						else:
							# a pass is in progress now
							time_to_sleep = 0
							pass_duration = int(time_los - time_now)
							print "Satellite is visible."
							print "Pass remaining is " + str(pass_duration) + " secs."
					else:
						# AOS is in the future
						print "Pass duration is " + str(pass_duration) + " secs."
						print "AOS in " + str(time_to_sleep) + " seconds."
					# if AOS is not within 60 seconds
					if(time_to_sleep > (1*60.0)):
						# if we're going to wait more than n mins,
						# only sleep for half of that interval and
						# then check with the predict server again
						# in case the keps have been updated and 
						# we need to adjust the AOS time
						time_to_sleep = time_to_sleep/2.0
						print "Sleeping for " + str(time_to_sleep) + " seconds."
						time.sleep(time_to_sleep)
						continue
					# AOS is within 60 seconds				
					elif(time_to_sleep > 0):				
						print "Sleeping for " + str(time_to_sleep) + " seconds."
						time.sleep(time_to_sleep)
					# notify the sequencer of AOS
					cmd = "start +"+str(pass_duration)
					print "Sending command to fcd_sequencer: " + cmd
					try:
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						s.connect((fcd_sequencer_host, fcd_sequencer_port))
						s.send(cmd)
						s.close()
					except:
						print "ERROR: failed to send command to fcd_sequencer. Sleeping for 10 seconds."
						time.sleep(10.0)
						continue
					print "Sleeping for " + str(pass_duration+0.0) + " seconds."
					time.sleep(float(pass_duration)+0.0)
				else:
					# the pass info seems invalid - bad duration
					print "ERROR: Unable to get sensible response from predict server. Sleeping for 10 seconds."
					time.sleep(10.0)
			else:
				print "ERROR: Unable to get a response from predict server. Sleeping for 10 seconds."
				time.sleep(10.0)
			predict_client.close()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print "\nDone."
	
	
