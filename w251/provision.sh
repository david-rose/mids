#!/bin/bash

# create an entry for the data directory
mkdir -m 777 /data

# configure the second disk for use
# locate the device name, look for the entry with the largest size
cat /proc/partitions
 - or -
fdisk -l | grep "2147.5 GB" | awk '{print substr($2, 0, length($2) -1)}'
 - or -
DEV=`fdisk -l | grep "2147.5 GB" | awk '{print substr($2, 0, length($2) -1)}'`

# assuming the device name is /dev/xvdc:
# format the device
mkfs.ext4 /dev/xvdc # or whichever disk is the san disk

# add an entry to the file system table that links the device to the data directory
echo '/dev/xvdc /data ext4 defaults,noatime 0 0' >> /etc/fstab
 - or -
echo "$DEV /data ext4 defaults,noatime 0 0" >> /etc/fstab

# mount the directory
mount /data

# install ntp server, which seems to be missing
yum install -y ntp
/etc/init.d/ntpd restart

touch ~/provision_success

