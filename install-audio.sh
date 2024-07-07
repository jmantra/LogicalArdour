#!/bin/bash
# ---------------------------
# This is a bash script for configuring Ardour and all dependencies for LogicalArdour for  Ubuntu 24.04 (Noble Nombat)
# This script is based on Bredan Ingraham's scripts for setting up pro audio on various distros, you can view his Github at 
# https://github.com/brendaningram/linux-audio-setup-scripts

# Exit if any command fails
 #set -e

notify () {
  echo "--------------------------------------------------------------------"
  echo $1
  echo "--------------------------------------------------------------------"
}


# ---------------------------
# Update our system
# ---------------------------
notify "Update the system"
sudo apt update && sudo apt dist-upgrade -y


read -p "Do you want to install a real-time kernel? (A real time kernel helps to reduce latency when recording) (yes/no): " answer


answer_lower=$(echo "$answer" | tr '[:upper:]' '[:lower:]')


if [[ "$answer_lower" == "yes" || "$answer_lower" == "y" ]]; then
    kernel="yes"
   
fi




if [[ "$kernel" == "yes" ]]; then
    
 
# Install the Liquorix kernel
# https://liquorix.net/
# ---------------------------
notify "Install the Liquorix kernel"
sudo add-apt-repository ppa:damentz/liquorix -y && sudo apt-get update
sudo apt-get install linux-image-liquorix-amd64 linux-headers-liquorix-amd64 -y
    
# ---------------------------
# Modify GRUB options
# threadirqs:
# mitigations=off:
# cpufreq.default_governor=performance:
# ---------------------------
notify "Modify GRUB options"
sudo systemctl disable ondemand
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash threadirqs mitigations=off cpufreq.default_governor=performance"/g' /etc/default/grub
sudo update-grub

# ---------------------------
# sysctl.conf
# ---------------------------
notify "sysctl.conf"
# See https://wiki.linuxaudio.org/wiki/system_configuration for more information.
echo 'vm.swappiness=10
fs.inotify.max_user_watches=600000' | sudo tee -a /etc/sysctl.conf

# ---------------------------
# audio.conf
# ---------------------------
notify "audio.conf"
# See https://wiki.linuxaudio.org/wiki/system_configuration for more information.
echo '@audio - rtprio 90
@audio - memlock unlimited' | sudo tee -a /etc/security/limits.d/audio.conf
fi


read -p "Do you want to configure Pipewire? (Configuring Pipewire will allow you to use Ardour and other audio applications (such as your web browser)simultaneously. Otherwise you will need to choose ALSA when starting Ardour or configure JACK audio manually (yes/no): " answer


answer_lower=$(echo "$answer" | tr '[:upper:]' '[:lower:]')


if [[ "$answer_lower" == "yes" || "$answer_lower" == "y" ]]; then
    pw="yes"
    
   fi
   


if [[ "$pw" == "yes" ]]; then


# ------------------------------------------------------------------------------------
# Install the latest Pipewire
# https://pipewire-debian.github.io/pipewire-debian/
# ------------------------------------------------------------------------------------
notify "Install Pipewire"
sudo add-apt-repository ppa:pipewire-debian/pipewire-upstream -y
sudo add-apt-repository ppa:pipewire-debian/wireplumber-upstream -y
sudo apt update
sudo apt install gstreamer1.0-pipewire libpipewire-0.3-{0,dev,modules} libspa-0.2-{bluetooth,dev,jack,modules} pipewire{,-{audio-client-libraries,pulse,bin,jack,alsa,v4l2,libcamera,locales,tests}} -y
sudo apt install wireplumber{,-doc} gir1.2-wp-0.4 libwireplumber-0.4-{0,dev} -y
systemctl --user --now disable pulseaudio.{socket,service}
systemctl --user mask pulseaudio
sudo cp -vRa /usr/share/pipewire /etc/
systemctl --user --now enable pipewire{,-pulse}.{socket,service} filter-chain.service
systemctl --user --now enable wireplumber.service

fi











# ---------------------------
# Add the user to the audio group
# ---------------------------
notify "Add user to the audio group"
sudo adduser $USER audio



notify "Install Ardour"

sudo apt install ardour -y



notify "Installing x42 plugins"

wget -O gm.tar.gz "https://x42-plugins.com/x42/linux/x42-gmsynth-v0.6.0-x86_64.tar.gz"

tar xavf gm.tar.gz

cd x42-gmsynth/

sh install-lv2.sh

sudo apt install x42-plugins -y







notify "Installing Musescore"

sudo apt install musescore -y




notify "Downloading and installing tools for detecting key and bpm"

# Key


wget https://jmantra.blob.core.windows.net/data/key



sudo cp key /usr/bin

sudo chmod 755 /usr/bin/key

#BPM

wget https://jmantra.blob.core.windows.net/data/bpmbin



sudo cp bpmbin /usr/bin

sudo chmod 755 /usr/bin/key

notify "Installing Calf Plugins"

sudo apt install calf-plugins -y




notify "Installing Steven Harris plugins"

sudo apt install swh-lv2 -y




notify "Installing TAP plugins"

sudo apt install tap-plugins -y



notify "Installing Guitarix and plugins"

sudo apt install guitarix -y



sudo apt install guitarix-lv2 -y



sudo apt install gxplugins -y



notify "Install Surge XT"

wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.2/surge-xt-linux-x64-1.3.2.deb

sudo apt install xclip -y



sudo dpkg -i surge-xt-linux-x64-1.3.2.deb













notify "download and installing  ardour config files"





notify "downloading and installing Ardour config files"

wget https://codeload.github.com/jmantra/LogicalArdour/zip/refs/heads/main

mkdir LogicalArdour

unzip main -d LogicalArdour


cd LogicalArdour/LogicalArdour-main

cp -rf /ardour8  ~/.config/

notify "installing  lv2 presets"

mkdir ~/.lv2

cp -rf "lv2 presets/*"  ~/.lv2

notify "installing Guitarix VST and presets"

mkdir ~/.vst3

cp -rf vst3/*  ~/.vst3

notify "installing soundfonts and samples"

sudo mkdir /opt/LogicalArdour

sudo cp -rf /samples/* /opt/LogicalArdour

#rm -rf LogicalArdour/*


notify "Install zynaddsubfx and enable kxstudio repos"
# Install required dependencies if needed
sudo apt-get install apt-transport-https gpgv wget

ensure_app_installed "apt-transport-https"
ensure_app_installed "gpgv"
ensure_app_installed "wget"


# Download package file
wget https://launchpad.net/~kxstudio-debian/+archive/kxstudio/+files/kxstudio-repos_11.1.0_all.deb

# Install it
sudo dpkg -i kxstudio-repos_11.1.0_all.deb



sudo apt install zynaddsubfx zynaddsubfx-lv2 zynaddsubfx-data -y





# ---------------------------
# Wine (staging)
# This is required for yabridge
# See https://wiki.winehq.org/Ubuntu and https://wiki.winehq.org/Winetricks for additional information.
# ---------------------------
notify "Install Wine"
sudo dpkg --add-architecture i386
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources
sudo apt update
sudo apt install --install-recommends winehq-staging -y
ensure_app_installed "winehq-staging"

# Winetricks
sudo apt install cabextract -y
ensure_app_installed "cabextract"
mkdir -p ~/.local/share
wget -O winetricks https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks
mv winetricks ~/.local/share
chmod +x ~/.local/share/winetricks
echo '' >> ~/.bash_aliases
echo '# Audio: winetricks' >> ~/.bash_aliases
echo 'export PATH="$PATH:$HOME/.local/share"' >> ~/.bash_aliases
. ~/.bash_aliases

# Base wine packages required for proper plugin functionality
winetricks corefonts

# Make a copy of .wine, as we will use this in the future as the base of
# new wine prefixes (when installing plugins)
cp -r ~/.wine ~/.wine-base




# ---------------------------
# Yabridge
# Detailed instructions can be found at: https://github.com/robbert-vdh/yabridge/blob/master/README.md
# ---------------------------
# NOTE: When you run this script, there may be a newer version of yabridge available.
# Check https://github.com/robbert-vdh/yabridge/releases and update the version numbers below if necessary
notify "Install yabridge"
wget -O yabridge.tar.gz https://github.com/robbert-vdh/yabridge/releases/download/5.1.0/yabridge-5.1.0.tar.gz
mkdir -p ~/.local/share
tar -C ~/.local/share -xavf yabridge.tar.gz
rm yabridge.tar.gz
echo '' >> ~/.bash_aliases
echo '# Audio: yabridge path' >> ~/.bash_aliases
echo 'export PATH="$PATH:$HOME/.local/share/yabridge"' >> ~/.bash_aliases
. ~/.bash_aliases

# libnotify-bin contains notify-send, which is used for yabridge plugin notifications.
sudo apt install libnotify-bin -y

ensure_app_installed "libnotify-bin"

# Create common VST paths
mkdir -p "$HOME/.wine/drive_c/Program Files/Steinberg/VstPlugins"
mkdir -p "$HOME/.wine/drive_c/Program Files/Common Files/VST2"
mkdir -p "$HOME/.wine/drive_c/Program Files/Common Files/VST3"
mkdir -p "$HOME/.vst"
mkdir -p "$HOME/.vst3"


# Add them into yabridge
yabridgectl add "$HOME/.wine/drive_c/Program Files/Steinberg/VstPlugins"
yabridgectl add "$HOME/.wine/drive_c/Program Files/Common Files/VST2"
yabridgectl add "$HOME/.wine/drive_c/Program Files/Common Files/VST3"
yabridgectl add "$HOME/.vst"
yabridgectl add "$HOME/.vst3"








notify "Install WINE plugin  MTpowerDrumkit"



wget -O mtpower.zip https://downloads.manda-audio.com/download76187/mtpdk2_free/2.1.2/MTPDK-2.1.2-VST2-64bit-Linux-with-Wine-FULL.zip

unzip mtpower.zip -d ./$(basename -s .zip mtpower.zip)

cp -rf mtpower "$HOME/.wine/drive_c/Program Files/Common Files/VST3"

notify "Install Beat DRMR WINE plugin"

wget -O beatdrmr.zip http://studiodrive.de/upload/plugins/Beat_DRMR-Win.zip

unzip beatdrmr.zip -d ./$(basename -s .zip beatdrmr.zip)

cp -rf beatdrmr "$HOME/.wine/drive_c/Program Files/Common Files/VST2"

notify "Install Neural Amp Modeler WINE plugin"

wget -O nam.zip  https://github.com/sdatkinson/NeuralAmpModelerPlugin/releases/download/v0.7.8/NeuralAmpModeler-v0.7.8-win.zip

unzip nam.zip

wine "NeuralAmpModeler Installer.exe"



notify "Sync WINE plugins with yabridge"



yabridgectl sync
yabridgectl status


# ---------------------------
notify "Done - please reboot."

