#!/bin/bash
BADDR=$1
USER=$(/bin/grep $BADDR /home/pi/hackathon/baddr.txt|cut -d"=" -f2)
/usr/bin/sudo /usr/bin/hcitool cc $BADDR;/usr/bin/hcitool lq $BADDR|/bin/grep Link
if [ $? -eq 0 ]; then
	echo "1" > /var/rpicache/"$USER"
	exit 0
fi
echo "0" > /var/rpicache/"$USER"
exit 1
