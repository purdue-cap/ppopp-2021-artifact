#!/bin/bash
set -e

# Update system
apt update
apt upgrade -y

# Install dependencies
apt install -y sudo openjdk-11-jdk git build-essential \
 python cmake wget libgmp-dev curl \
 rsync mercurial m4 unzip darcs python3 \
 flex bison autotools-dev automake

# Setup normal user
useradd -m user -G sudo -s /bin/bash
echo -e "coaJae2e\ncoaJae2e" | passwd user
echo 'user ALL=(ALL) NOPASSWD: ALL' | env EDITOR='tee -a' visudo

# Prepare for build dependencies
mkdir -p /build && chown user:user /build
