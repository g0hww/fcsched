fcsched
=======

A simple python scheduler for the fcdec telemetry decoder for the Funcube-1 
(AO-73) satellite (here: https://github.com/csete/fcdec). Fcsched uses a predict
server for pass predictions.

fcsched requires netcat (nc) and pexpect to be installed, as well as fcdec.

Before running fcsched.py, you should:

1) Have a predict server running (use "predict -s") that has good keps
for the AO-73 satellite.  See:

http://funcube.org.uk/working-documents/latest-two-line-elements/

2) Have fcd_sequencer.sh running.

You must edit fcsched.py to configure the predict server and fcd_sequencer server
host and port number (defaults are for the server on localhost and the 
default predict port).  The query to predict is done by catalogue number.  This
should match the one in the keps you are using for predict.

When invoked, fcsched asks the predict server to determine when the next pass
of FUNcube-1 starts.  It then sleeps for half the time until AOS then asks again
(to allow for predict to provide an updated solution with new keps). It loops 
like that until AOS is within 1 minute, sleeps until AOS and then commands
fcd_sequencer to begin data collection for the duration of that pass. It then
sleeps during the pass and then asks the predict server for the details of the 
next pass.

