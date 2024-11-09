#!/bin/bash

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

cd "$HOME/Downloads"

sudo apt install ardour -y

sudo apt install musescore -y

folder="$HOME/.config/MuseScore"
backup_or_create_folder "$folder"

# Key

wget https://jmantra.blob.core.windows.net/data/key

sudo cp key /usr/bin

sudo chmod 755 /usr/bin/key

#BPM

#wget https://jmantra.blob.core.windows.net/data/bpmbin

#sudo cp bpmbin /usr/bin

#sudo chmod 755 /usr/bin/bpmbin


while true; do
  read -p "Would you like to configure Ardour to automatically use Pipewire-Jack when launching? (This is the reccommneded way as it allows other applications to use the sound card as well connect Musescore to Ardour) (y/n): " choice
  case "$choice" in
    y|Y )
      # Replace the URL with the actual link to the file you want to download
      echo "Configuring Pipewire-Jack"
      sudo apt install pipewire-jack
    sed -i 's|^Exec=/usr/bin/ardour %f$|Exec=/usr/bin/pw-jack /usr/bin/ardour %f|' ardour.desktop
    sudo apt install libspa-0.2-jack -y
sudo usermod -aG audio $USER

      break
      ;;
    n|N )
      echo "Skipping Pipewire autoconfig."
      break
      ;;
    * )
      echo "Invalid input. Please enter y or n."
      ;;
  esac
done

# Continue with the rest of your script here
echo "Continuing with the rest of the script..."


##########



while true; do
  read -p "Do you want to download some loops? (3.5 GB)(Please Note: Loops can be downloaded later in the Library Downloader, however not all loop libraries work in the distro version of Ardour ) (y/n): " choice
  case "$choice" in
    y|Y )
      # Replace the URL with the actual link to the file you want to download
      echo "Downloading loops..."
      folder="$HOME/.local/share/sounds/"
backup_or_create_folder "$folder"
      wget https://jmantra.blob.core.windows.net/data/clips.zip
      unzip clips.zip -d $folder
      rm -rf clips.zip
      break
      ;;
    n|N )
      echo "Skipping download."
      break
      ;;
    * )
      echo "Invalid input. Please enter y or n."
      ;;
  esac
done

# Continue with the rest of your script here
echo "Continuing with the rest of the script..."

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




wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.1/surge-xt-linux-x64-1.3.1.deb

sudo apt install xclip -y

sudo apt install libxcb-cursor0 -y


sudo dpkg -i surge-xt-linux-x64-1.3.1.deb

#sudo apt upgrade -y
sudo apt install zam-plugins -y

sudo apt install samplv1 -y


sudo apt install git

git clone https://github.com/jmantra/LogicalArdour.git

cd LogicalArdour

cp MuseScore2.ini $HOME/.config/MuseScore






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

for file in $HOME/.config/MuseScore/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/justin", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done



#DIR=$(find /opt -maxdepth 1 -type d -name "Ardour-*" | sort -V | tail -n 1)







cd "$HOME/Downloads"


rm -rf LogicalArdour/*

# Prompt the user for confirmation
read -p "In order for everything to work properly it is highly reccommended you restart your computer? Do you want to restart the computer? (y/n): " answer

# Check the user's response
if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo "Restarting the computer..."
    sudo shutdown -r now
else
    echo "Restart canceled."
fi










