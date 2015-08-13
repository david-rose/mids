#!/bin/bash

# create an entry for the data directory
mkdir -m 777 /data

# configure the second disk for use

DEV=`fdisk -l | grep "214.7 GB" | awk '{print substr($2, 0, length($2) -1)}'`

# format the device
mkfs.ext4 $DEV

# add an entry to the file system table that links the device to the data directory
echo "$DEV /data ext4 defaults,noatime 0 0" >> /etc/fstab

# mount the directory
mount /data

# install ntp server, which seems to be missing
yum install -y ntp
/etc/init.d/ntpd restart

touch ~/provision_success

