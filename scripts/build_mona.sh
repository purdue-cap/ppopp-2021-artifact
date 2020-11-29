#!/bin/bash
set -e

# Build MONA
cd /home/user/ && git clone https://github.com/cs-au-dk/MONA
cd MONA && git checkout 1.4-18
./configure --prefix=/usr/local
make
sudo make install-strip
