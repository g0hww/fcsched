fcsched
=======

A simple python scheduler for the fcdec telemetry decoder for the Funcube-1 
(AO-73) satellite that uses a predict server for pass predictions.  It has been
observed to work at least once, so far :)

fcsched requires netcat (nc) and pexpect to be installed, as well as fcdec.

Before running fcsched.py, you should:

1) Have a predict server running (use "predict -s") that has good keps
for the AO-73 satellite.

2) Have fcd_sequencer.sh running.

Currently you must also edit fcsched.py to configure the predict server and 
fcd_sequencer server host and port number info (defaults are for both on
localhost).  The query to predict is done by catalogue number.

When invoked, fcsched queries the predict server to determine when the next pass
of FUNcube-1 starts and how long the next pass is.  It then sleeps until AOS and
then commands fcd_sequencer to begin data collection for the duration of that
pass. It then sleeps during the pass and then queries the predict server for the
details of the nesxt pass.

