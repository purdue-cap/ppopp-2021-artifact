#!/bin/bash
set -e

# Build Retreet
# cd Retreet && make
# echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib' >> /home/user/.bashrc

cd /home/user/ && git clone https://github.rcac.purdue.edu/wang3204/Retreet
cd Retreet
make
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib' >> /home/user/.bashrc

cp -f /scripts/run_benchmarks.py /home/user/Retreet
