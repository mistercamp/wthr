#!/bin/bash

sudo systemctl stop wthr.service
sudo systemctl disable wthr.service
sudo rm /etc/systemd/system/wthr.service
sudo rm -rf /opt/wthr
