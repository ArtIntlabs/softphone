sudo apt install python3 python3-dev build-essential libasound2-dev
wget https://github.com/DiscordPhone/pjproject/archive/py37.zip
sudo unzip py37.zip
sudo cd pjproject-py37
sudo chmod +x configure aconfigure
sudo ./configure CXXFLAGS=-fPIC CFLAGS=-fPIC LDFLAGS=-fPIC CPPFLAGS=-fPIC
sudo make dep
sudo make
sudo make install
