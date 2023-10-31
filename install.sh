#!/bin/bash

INSTALL_LOC='/opt/wthr'


echo "SUDO required for install"
sudo mkdir -p $INSTALL_LOC/img/{bg,icon,temp}
sudo cp -r * $INSTALL_LOC
sudo python3 -m venv $INSTALL_LOC/.venv
sudo $INSTALL_LOC/.venv/bin/python3 -m pip install -r $INSTALL_LOC/requirements.txt
sudo chown -R $USER:$USER $INSTALL_LOC

sed -i "s|__USER__|$USER|" wthr.service
sed -i "s|__DISPLAY__|$DISPLAY|" wthr.service
sed -i "s|__XAUTH__|$XAUTHORITY|" wthr.service
sed -i "s|__XDGRUN__|$XDG_RUNTIME_DIR|" wthr.service
sed -i "s|__INSTALL_LOC__|$INSTALL_LOC|g" wthr.service

if [ -f /etc/systemd/system/wthr.service ]; then
    sudo systemctl stop wthr.service
    sudo systemctl disable wthr.service
else
    sudo \cp -f ./wthr.service /etc/systemd/system/wthr.service
fi

sudo systemctl enable wthr.service
sudo systemctl start wthr.service

sudo rm $INSTALL_LOC/wthr.service $INSTALL_LOC/install.sh $INSTALL_LOC/requirements.txt
