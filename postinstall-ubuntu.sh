#!/bin/bash
# ---------------------------
# This is a bash script for configuring Ardour and all dependencies for LogicalArdour for  Ubuntu 24.04 (Noble Nombat)
# This script is based on Bredan Ingraham's scripts for setting up pro audio on various distros, you can view his Github at 
# https://github.com/brendaningram/linux-audio-setup-scripts

# Exit if any command fails
 #set -e





cd "$HOME/Downloads"







sudo apt install musescore -y






# Key


wget https://jmantra.blob.core.windows.net/data/key



sudo cp key /usr/bin

sudo chmod 755 /usr/bin/key

#BPM

wget https://jmantra.blob.core.windows.net/data/bpmbin



sudo cp bpmbin /usr/bin

sudo chmod 755 /usr/bin/bpmbin









# Install required dependencies if needed
sudo apt-get install apt-transport-https gpgv wget



# Download package file
wget https://launchpad.net/~kxstudio-debian/+archive/kxstudio/+files/kxstudio-repos_11.1.0_all.deb

# Install it
sudo dpkg -i kxstudio-repos_11.1.0_all.deb

rm -rf kxstudio-repos_11.1.0_all.deb

sudo apt update 

sudo apt upgrade -y 





sudo apt install zynaddsubfx zynaddsubfx-lv2 zynaddsubfx-data -y









sudo apt install x42-plugins avldrums.lv2 swh-lv2 calf-plugins tap-plugins guitarix-lv2  drumgizmo -y

wget https://download.opensuse.org/repositories/home:/sfztools:/sfizz/xUbuntu_23.10/amd64/sfizz_1.2.3-0_amd64.deb

sudo dpkg -i sfizz_1.2.3-0_amd64.deb

rm -rf sfizz_1.2.3-0_amd64.deb


wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.1/surge-xt-linux-x64-1.3.1.deb

sudo apt install xclip -y

sudo dpkg -i surge-xt-linux-x64-1.3.1.deb

sudo apt upgrade -y











wget https://codeload.github.com/jmantra/LogicalArdour/zip/refs/heads/main

mkdir LogicalArdour

unzip main -d LogicalArdour


cd LogicalArdour/LogicalArdour-main



# Function to check if folder exists, make a backup if exists, create if not
backup_or_create_folder() {
    local folder="$1"

    if [ -d "$folder" ]; then
        echo "Folder '$folder' already exists. Making a backup..."
        cp -r "$folder" "${folder}_backup"
    else
        echo "Folder '$folder' does not exist. Creating folder..."
        mkdir -p "$folder"
    fi
}


folder="$HOME/.lv2"
backup_or_create_folder "$folder"


cp -rf lv2_presets/* $HOME/.lv2

folder="$HOME/.vst"
backup_or_create_folder "$folder"


cp -rf vst/* "$HOME/.vst"

folder="$HOME/.vst3"
backup_or_create_folder "$folder"

cp -rf vst3/* "$HOME/.vst3"




sudo mkdir -p /opt/LogicalArdour

sudo cp -rf samples/* /opt/LogicalArdour

mkdir ~/.config/LogicalArdour



folder="$HOME/.config/ardour8"
backup_or_create_folder "$folder"

cp -rf ardour8/*  $folder


#DIR=$(find /opt -maxdepth 1 -type d -name "Ardour-*" | sort -V | tail -n 1)




sudo cp -rf media/* /usr/share/ardour8/media


cd "$HOME/Downloads"


rm -rf LogicalArdour/*












# ---------------------------
notify "Done - please reboot."

