#!/bin/bash

cd "$HOME/Downloads"

sudo apt install ardour -y

sudo apt install musescore -y

# Key

wget https://jmantra.blob.core.windows.net/data/key

sudo cp key /usr/bin

sudo chmod 755 /usr/bin/key

#BPM

#wget https://jmantra.blob.core.windows.net/data/bpmbin

#sudo cp bpmbin /usr/bin

#sudo chmod 755 /usr/bin/bpmbin

sudo apt install sox bpm-tools -y



# Install required dependencies if needed
sudo apt-get install apt-transport-https gpgv wget -y



# Download package file
wget https://launchpad.net/~kxstudio-debian/+archive/kxstudio/+files/kxstudio-repos_11.1.0_all.deb

# Install it
sudo dpkg -i kxstudio-repos_11.1.0_all.deb

rm -rf kxstudio-repos_11.1.0_all.deb

sudo apt update 

# sudo apt upgrade -y

wget https://launchpad.net/~kxstudio-debian/+archive/plugins/+files/zynaddsubfx_3.0.5-1kxstudio7_amd64.deb

sudo dpkg -i zynaddsubfx_3.0.5-1kxstudio7_amd64.deb

wget https://launchpad.net/~kxstudio-debian/+archive/plugins/+files/zynaddsubfx-data_3.0.5-1kxstudio7_all.deb

sudo dpkg -i zynaddsubfx-data_3.0.5-1kxstudio7_all.deb


sudo apt install x42-plugins avldrums.lv2 swh-lv2 calf-plugins tap-plugins  guitarix-lv2  mda-lv2  -y

 wget https://download.opensuse.org/repositories/home:/sfztools:/sfizz/xUbuntu_23.10/amd64/sfizz_1.2.3-0_amd64.deb

#wget https://download.opensuse.org/repositories/home:/sfztools:/sfizz/Debian_12/amd64/sfizz_1.2.3-0_amd64.deb

sudo dpkg -i sfizz_1.2.3-0_amd64.deb

rm -rf sfizz_1.2.3-0_amd64.deb


wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.1/surge-xt-linux-x64-1.3.1.deb

sudo apt install xclip -y

sudo dpkg -i surge-xt-linux-x64-1.3.1.deb

#sudo apt upgrade -y
sudo apt install zam-plugins


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


cp -rf lv2/* $HOME/.lv2

folder="$HOME/.vst"
backup_or_create_folder "$folder"




folder="$HOME/.vst3"
backup_or_create_folder "$folder"

cp -rf vst3/* "$HOME/.vst3"

folder="$HOME/.ladspa"
backup_or_create_folder "$folder"

cp -rf ladspa/* "$HOME/.ladspa"




sudo mkdir -p /opt/LogicalArdour

sudo cp -rf samples/* /opt/LogicalArdour

sudo mkdir /usr/local/lib/vst3



folder="$HOME/.config/ardour8"
backup_or_create_folder "$folder"

cp -rf ardour8/*  $folder

for file in $HOME/.config/ardour8/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/jman", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done

for file in $HOME/.config/ardour8/route_templates/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/jman", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done



#DIR=$(find /opt -maxdepth 1 -type d -name "Ardour-*" | sort -V | tail -n 1)




sudo cp -rf media/* /usr/share/ardour8/media


cd "$HOME/Downloads"


rm -rf LogicalArdour/*











