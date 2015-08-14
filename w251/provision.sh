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

mkdir -m 700 ~/.ssh

echo \
'-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAtLBezA7VrNZ62sHutshJ7djojBc3MH9mjfMP0wW0J4bdh8Nm
cmX6Yh/Y2O1rzIGLYyGKBnpDDxkmYkpEd9g8LUWmTG8/w6wCB8WhOFP6BVoFmygH
Gz4v0FAlJzPVCgC4mofRkQj8FRhZzrTdDNhdmHlC5vzPCMhYVKoyCTJVRnCKXlNA
8QEC/D2dl1gu8SbCx2sSpXCtTcvGeF8++l7ft/A8zu7X4TFalr+DpbeAoq/xDQuk
lWRoGmystrf3Mn1pilD62N3arnRjSDIh8mL+b8t5q2Q7u1Ig17lLlW/BTj1bQSRa
FmVtg9v6JNX2w/vNUq1Ukw9aVVQmwSTOLSGSRQIDAQABAoIBADGxb+DfE5T9R7xy
KZzLaMmpJguhNuR3pVTUzD1VDD7ysGpuKva7ZSknaRP/9+2+kv8ocjVl2puEZzIR
CtOK/MHWre3HitndrJFGoRhEwDZIk9IgKBQt/ihkYlNtxeGCYULep5wjxHBoygo3
Y7PsrZEJiITOcoIP13sxc6Fj3mAIjK4ZPvEbv6mUPJE4MaZgr+kUyyRcwsMaETsj
EToo87fpsm/DesDgrQz33ZvEBzfHaIo5qfe9+Pc4MfNNodse5YNXuHPz6wu769BE
C/g5JiXjQy2eyROYSjy2bj5nNQ8JDOAoktAtTqhyXaUSYoVhFqgIDuNfNXCwsZNQ
ijJIhAECgYEA7KP+tgNFEx1pVx8qQ0NYnpaJ+joicZXdX9TYSLMMD4iMdbSYhXeb
31TWK+RBXjwrwD5Ru2/KohCGmPdTGPO28fa/ToSv2lkq7/XwIeFduf4cKnJyitUG
qJ1H1IP3aJcrgbzTl9Ig+5QWMlt+HIsOdj24Fu0z2bMqpSUnhn9W/6ECgYEAw3iR
8WLYOA+iFCtM5lvY9c5pgCS+vFhqpYOJg3EbZMvGtn4hczBEftA3I+P7COTjZ6py
uJvF2bxjnhhBdQQ/PinSf/ZgPQO3ybtAH0DI12BkwWeAw9dj7hnvxom5EHlIrPVL
1KnY+J2bMppqRAMEWVam97gQje3dHgQKfvmKoCUCgYEAj736HZOU5MyLzUj4Ag2p
igOFYoLnozlWVDzU+CwSWmkmcOU3dHM4Mou04Mpwzo4cQVVZjlKUsqb5K3eoeVKp
QQcSI97Ddw2M4F/y8pGTvkPV1g7Y9u35cni/Rh63LUgOPGt32BPixw6oAQTEcRAi
w74v0XVadpW3hMMx5Cf7r6ECgYADGha2zerAeP8JcuZ1gV+gBvaFog+kzYJjvgKg
o1rb7p/opXfCbDGqEYPOff+t1HQHYR0Q8Ofi3Kp4B8qCIN8gDWnZvf8o+LYh7WbH
GDAXut/ecdYJRZHAZYj4jZbyO/p7RCk/5rIav+WGmAy3p5SaFlXv+GvK1Mt9fnLs
MOmSQQKBgQDmzmtxpG2RqIUGzsP3kchLsbi65drEElwL1WQvJdpvT+8Gq7bUYLi/
5iLwsysd4lGcE1n8KdjRbwgSxhDgnW73hLCUiW1xb5/Hz6+Yi3X3bAhEumyi0gRb
xvfkqf6RqPFlDgt8m0+9mKrbaB9VYiH+WJygL4dOyHDs9reA9LjV3No1w==
-----END RSA PRIVATE KEY-----' > ~/.ssh/id_rsa

echo \
'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC0sF7MDtWs1nrawe62yEnt2OiMFzcwf2aN8w/TBbQnht2Hw2ZyZfpiH9jY7WvMgYtjIYoGekMPGSZiSkR32DwtRaZMbz/DrAIHxaE4U/oFWgWbKAcbPi/QUCUnM9UKALiah9GRCPwVGFnOtN0M2F2YeULm/M8IyFhUqjIJMlVGcIpeU0DxAQL8PZ2XWC7xJsLHaxKlcK1Ny8Z4Xz76Xt+38DzO7tfhMVqWv4Olt4Cir/ENC6SVZGgabKy2t/cyfWmKUPrY3dqudGNIMiHyYv5vy3mrZDu7UiDXuUuVb8FOPVtBJFoWZW2D2/ok1fbD+81SrVSTD1pVVCbBJM4tIZJF david@DataSci.local' > ~/.ssh/id_rsa.pub

cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

chmod 600 ~/.ssh/*

# install ntp server
yum install -y ntp
/etc/init.d/ntpd restart

# disable iptables, per Ambari instructions
chkconfig iptables off
/etc/init.d/iptables stop

#  install epel repository
wget http://mirror.sfo12.us.leaseweb.net/epel/6/i386/epel-release-6-8.noarch.rpm
rpm -Uvh epel-release-6-8.noarch.rpm

# leave some evidence
touch ~/provision_success

