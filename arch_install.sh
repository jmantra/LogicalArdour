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

sudo_backup_or_create_folder() {
    local folder="$1"

    if [ -d "$folder" ]; then
        echo "Folder '$folder' already exists. Making a backup..."
        sudo cp -r "$folder" "${folder}_backup"
    else
        echo "Folder '$folder' does not exist. Creating folder..."
        sudo mkdir -p "$folder"
    fi
}

cd "$HOME/Downloads"

# Check if yay or paru is installed for AUR packages
AUR_HELPER=""
if command -v yay &> /dev/null; then
    AUR_HELPER="yay"
elif command -v paru &> /dev/null; then
    AUR_HELPER="paru"
else
    echo "Warning: No AUR helper (yay/paru) found. Installing yay..."
    cd /tmp
    git clone https://aur.archlinux.org/yay.git
    cd yay
    makepkg -si --noconfirm
    AUR_HELPER="yay"
    cd "$HOME/Downloads"
fi

while true; do
  read -p "Do you already have Ardour installed? If you say no Ardour will be installed for you. Note: You must have Ardour 8.6 or higher for everything to work properly (y/n): " choice
  case "$choice" in
    y|Y )
      echo "Skipping Ardour install"
      break
      ;;
    n|N )
      echo "Installing Ardour"
      # Install Ardour from AUR (or use the same zip method if preferred)
      echo "Installing Ardour dependencies..."
      sudo pacman -S --needed base-devel git boost gcc pkg-config alsa-lib gtk2 glibmm libsndfile libarchive liblo taglib vamp-plugin-sdk rubberband fftw aubio libxml2 libsamplerate lv2 serd sord sratom lilv gtkmm jack2 libogg cppunit systemd libwebsockets libusb suil dbus xjadeo readline pangomm python git wget unzip --noconfirm
      
      # Option 1: Install from AUR (recommended for Arch)
      echo "Installing Ardour from AUR..."
      $AUR_HELPER -S ardour --noconfirm
      
      # Option 2: Use the same zip method as Ubuntu (uncomment if preferred)
      # wget https://jmantra.blob.core.windows.net/data/ardour.zip
      # unzip ardour.zip
      # cd ardour
      # sudo ./waf install
      
      compiled=true
      break
      ;;
    * )
      echo "Invalid input. Please enter y or n."
      ;;
  esac
done

# Continue with the rest of your script here
echo "Continuing with the rest of the script..."

while true; do
  read -p "Would you like to configure Ardour to automatically use Pipewire-Jack when launching? (This is the recommended way as it allows other applications to use the sound card as well connect Musescore to Ardour) (y/n): " choice
  case "$choice" in
    y|Y )
      echo "Configuring Pipewire-Jack"
      sudo pacman -S --needed pipewire pipewire-alsa pipewire-audio pipewire-jack pipewire-pulse wireplumber --noconfirm

      # Tell all apps that use JACK to now use the Pipewire JACK
      # Arch uses a different path structure, create the config manually
      sudo mkdir -p /etc/ld.so.conf.d
      echo "/usr/lib/pipewire-0.3/jack" | sudo tee /etc/ld.so.conf.d/pipewire-jack.conf > /dev/null
      sudo ldconfig

      sudo usermod -aG audio $USER
      pipewire=true
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

sudo pacman -S --needed sox bpm-tools --noconfirm

# Install required dependencies if needed
sudo pacman -S --needed wget --noconfirm

# Note: Arch doesn't use debconf, so we skip the jackd2 tweak_rt_limits setting
# Users can configure realtime limits manually if needed via /etc/security/limits.conf

sudo pacman -S --needed yoshimi --noconfirm

# Install LV2 plugins - package names may vary in Arch
sudo pacman -S --needed x42-plugins avldrums-lv2 swh-lv2 calf tap-plugins guitarix-lv2 mda-lv2 --noconfirm

# For Surge XT, we need to handle the .deb file differently
# Option 1: Use debtap to convert .deb to .pkg.tar.xz
# Option 2: Extract and install manually
# Option 3: Install from AUR if available
if $AUR_HELPER -Ss surge-xt &> /dev/null; then
    echo "Installing Surge XT from AUR..."
    $AUR_HELPER -S surge-xt --noconfirm
else
    echo "Installing Surge XT from .deb file..."
    wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.1/surge-xt-linux-x64-1.3.1.deb
    
    # Check if debtap is installed
    if ! command -v debtap &> /dev/null; then
        echo "Installing debtap to convert .deb to Arch package..."
        $AUR_HELPER -S debtap --noconfirm
        sudo debtap -u
    fi
    
    # Convert and install
    debtap surge-xt-linux-x64-1.3.1.deb
    sudo pacman -U surge-xt-linux-x64-1.3.1-*.pkg.tar.xz --noconfirm
    rm -f surge-xt-linux-x64-1.3.1.deb surge-xt-linux-x64-1.3.1-*.pkg.tar.xz
fi

sudo pacman -S --needed xclip libxcb --noconfirm

sudo pacman -S --needed zam-plugins --noconfirm

sudo pacman -S --needed samplv1 --noconfirm

sudo pacman -S --needed git --noconfirm

git clone https://github.com/jmantra/LogicalArdour.git

cd LogicalArdour

sudo mkdir -p /opt/LogicalArdour

sudo cp minibpm /opt/LogicalArdour/minibpm
sudo chmod +x /opt/LogicalArdour/minibpm

folder="$HOME/.lv2"
backup_or_create_folder "$folder"

cp -rf lv2/* $HOME/.lv2

folder="$HOME/.vst"
backup_or_create_folder "$folder"

folder="$HOME/.local/share/Trackbout/Ripchord/Presets/"
backup_or_create_folder "$folder"

cp -rf Ripchord/* $folder

folder="$HOME/.vst3"
backup_or_create_folder "$folder"

cp -rf vst3/* "$HOME/.vst3"

folder="$HOME/.ladspa"
backup_or_create_folder "$folder"

cp -rf ladspa/* "$HOME/.ladspa"

folder="/usr/lib/ladspa"
sudo_backup_or_create_folder "$folder"

sudo cp -rf ladspa-rubberband.cat $folder
sudo cp -rf ladspa-rubberband.so $folder

sudo cp -rf samples/* /opt/LogicalArdour

sudo pacman -S --needed fuse3 fuse2 --noconfirm
wget https://jmantra.blob.core.windows.net/data/mscore
sudo cp -rf mscore /opt/LogicalArdour
sudo chmod 755 /opt/LogicalArdour/mscore

folder="$HOME/.config/MuseScore"
backup_or_create_folder "$folder"

cp MuseScore3.ini $HOME/.config/MuseScore
cp MuseScore2.ini $HOME/.config/MuseScore

wget https://jmantra.blob.core.windows.net/data/key

sudo cp key /opt/LogicalArdour

sudo chmod 755 /opt/LogicalArdour/key

wget https://jmantra.blob.core.windows.net/data/newchord

sudo cp newchord /opt/LogicalArdour

sudo chmod 755 /opt/LogicalArdour/newchord

wget https://jmantra.blob.core.windows.net/data/bassline_generator

sudo cp bassline_generator /opt/LogicalArdour
sudo chmod 755 /opt/LogicalArdour/bassline_generator

sudo chmod 755 /opt/LogicalArdour/bassline_generator.py
sudo mkdir -p /usr/local/lib/vst3

folder="$HOME/.config/ardour8"
backup_or_create_folder "$folder"

cp -rf ardour8/*  $folder

folder="$HOME/.config/guitarix"
backup_or_create_folder "$folder"

cp -rf guitarix/*  $folder

for file in $HOME/.config/ardour8/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/justin", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done
for file in $HOME/.config/ardour8/route_templates/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/justin", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done
for file in $HOME/.config/MuseScore/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/justin", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done

cd "$HOME/Downloads"

rm -rf LogicalArdour/*

# Prompt the user for confirmation
read -p "In order for everything to work properly it is highly recommended you restart your computer? Do you want to restart the computer? (y/n): " answer

# Check the user's response
if [[ "$answer" =~ ^[Yy]$ ]]; then
    echo "Restarting the computer..."
    sudo reboot
else
    echo "Restart canceled."
fi

