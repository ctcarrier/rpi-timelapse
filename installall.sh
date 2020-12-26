sudo git clone https://github.com/ctcarrier/rpi-timelapse.git /usr/src/rpi-timelapse
sudo git clone https://github.com/ctcarrier/rpi-s3-monitor.git /usr/src/rpi-s3-monitor
sudo cp /usr/src/rpi-timelapse/etc/timelapse.service /lib/systemd/system
sudo cp /usr/src/rpi-s3-monitor/etc/s3monitor.service /lib/systemd/system
sudo pip install RPi.GPIO
sudo pip install tinys3
sudo apt-get install -y autoconf
sudo apt-get install -y autopoint
sudo apt install -y gettext
# sudo apt install -y libtool
# sudo apt install -y libtool-devel
# sudo apt install -y libtool
# sudo apt install -y msgfmt
sudo apt install -y libpopt-dev
sudo git clone https://code.videolan.org/videolan/x264 /usr/src/x264
cd /usr/src/x264 && sudo ./configure
cd /usr/src/x264 && sudo make
cd /usr/src/x264 && sudo make install

sudo git clone https://github.com/gphoto/gphoto2.git /usr/src/gphoto2
cd /usr/src/gphoto2 && sudo autoreconf -is
cd /usr/src/gphoto2 && sudo ./configure --prefix=/usr/local
cd /usr/src/gphoto2 && sudo make
cd /usr/src/gphoto2 && sudo make install

sudo git clone https://github.com/gphoto/libgphoto2.git /usr/src/libgphoto2
cd /usr/src/libgphoto2 && sudo autoreconf -is
cd /usr/src/libgphoto2 && sudo ./configure --prefix=/usr/local
cd /usr/src/libgphoto2 && sudo make
cd /usr/src/libgphoto2 && sudo make install
sudo touch /var/log/timelapse.log
sudo chmod 777 /var/log/timelapse.log
sudo mkdir /var/log/s3monitor
sudo chmod 755 /var/log/s3monitor/
sudo touch /var/log/s3monitor/s3monitor.log
sudo chmod 777 /var/log/s3monitor/s3monitor.log

sudo mkdir /var/lib/timelapse
sudo chmod 755 /var/lib/timelapse/
sudo mkdir /var/lib/timelapse/img
sudo chmod 755 /var/lib/timelapse/img/
sudo touch /var/lib/timelapse/settings.cfg
sudo chmod 644 /var/lib/timelapse/settings.cfg 
sudo mkdir /var/lib/s3monitor
sudo touch /var/lib/s3monitor/settings.cfg
sudo chmod 644 /var/lib/s3monitor/settings.cfg
sudo chmod 755 /var/lib/s3monitor/
