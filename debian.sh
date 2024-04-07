#!/bin/bash
# ---------------------------
# This is a bash script for configuring Debian 12 (bookworm) for pro audio USING PIPEWIRE.
# This is based on Brendan Ingram's Linux Audio Setup Scripts at https://github.com/brendaningram/linux-audio-setup-scripts
# ---------------------------


# Exit if any command fails
# set -e

notify () {
  echo "--------------------------------------------------------------------"
  echo $1
  echo "--------------------------------------------------------------------"
}


# ---------------------------
# Update our system
# ---------------------------
notify "Update the system"
sudo apt update && sudo apt upgrade -y


# ---------------------------
# Install Liquorix kernel
# https://liquorix.net/
# ---------------------------
sudo apt install curl -y
curl 'https://liquorix.net/add-liquorix-repo.sh' | sudo bash
sudo apt install linux-image-liquorix-amd64 linux-headers-liquorix-amd64 -y

sudo apt install wget -y


# ---------------------------
# Pipewire
# https://wiki.debian.org/PipeWire
# NOTE: If you don't have any audio coming from your system, it is possible that the hardware
# channels in your audio interface are muted. In that case, run alsamixer, press F6 to select
# your audio interface, locate your main monitor channel, then press M to unmute.
# You can then run sudo alsactl store to persist these changes.
# ---------------------------
notify "Install pipewire"
sudo apt install pipewire pipewire-alsa pipewire-audio pipewire-audio-client-libraries pipewire-jack pipewire-pulse libspa-0.2-jack wireplumber -y

# Tell all apps that use JACK to now use the Pipewire JACK
sudo cp /usr/share/doc/pipewire/examples/ld.so.conf.d/pipewire-jack-*.conf /etc/ld.so.conf.d/
sudo ldconfig

#sudo apt install qjackctl --no-install-recommends -y


# ---------------------------
# grub
# ---------------------------
notify "Modify GRUB options"
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet"/GRUB_CMDLINE_LINUX_DEFAULT="quiet threadirqs cpufreq.default_governor=performance"/g' /etc/default/grub
sudo update-grub


# ---------------------------
# limits
# See https://wiki.linuxaudio.org/wiki/system_configuration for more information.
# ---------------------------
notify "Modify limits.d/audio.conf"
echo '@audio - rtprio 90
@audio - memlock unlimited' | sudo tee -a /etc/security/limits.d/audio.conf


# ---------------------------
# sysctl.conf
# See https://wiki.linuxaudio.org/wiki/system_configuration for more information.
# ---------------------------
notify "Modify /etc/sysctl.conf"
echo 'vm.swappiness=10
fs.inotify.max_user_watches=600000' | sudo tee -a /etc/sysctl.conf


# ---------------------------
# Add the user to the audio group
# ---------------------------
notify "Add ourselves to the audio group"
sudo usermod -a -G audio $USER

notify "Install Ardour"

sudo apt install ardour -y




# ---------------------------
# Wine (staging)
# This is required for yabridge
# See https://wiki.winehq.org/Debian for additional information.
# ---------------------------
notify "Install Wine"
sudo dpkg --add-architecture i386
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/debian/dists/bookworm/winehq-bookworm.sources
sudo apt update
version=7.20
variant=staging
codename=$(shopt -s nullglob; awk '/^deb https:\/\/dl\.winehq\.org/ { print $3; exit 0 } END { exit 1 }' /etc/apt/sources.list /etc/apt/sources.list.d/*.list || awk '/^Suites:/ { print $2; exit }' /etc/apt/sources.list /etc/apt/sources.list.d/wine*.sources)
suffix=$(dpkg --compare-versions "$version" ge 6.1 && ((dpkg --compare-versions "$version" eq 6.17 && echo "-2") || echo "-1"))
sudo apt install --install-recommends {"winehq-$variant","wine-$variant","wine-$variant-amd64","wine-$variant-i386"}="$version~$codename$suffix"

# Winetricks
sudo apt install cabextract -y
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

# Create common VST paths
mkdir -p "$HOME/.wine/drive_c/Program Files/Steinberg/VstPlugins"
mkdir -p "$HOME/.wine/drive_c/Program Files/Common Files/VST2"
mkdir -p "$HOME/.wine/drive_c/Program Files/Common Files/VST3"

# Add them into yabridge
yabridgectl add "$HOME/.wine/drive_c/Program Files/Steinberg/VstPlugins"
yabridgectl add "$HOME/.wine/drive_c/Program Files/Common Files/VST2"
yabridgectl add "$HOME/.wine/drive_c/Program Files/Common Files/VST3"

notify "Install zynaddsubfx"
# Install required dependencies if needed
sudo apt-get install apt-transport-https gpgv wget

# Download package file
wget https://launchpad.net/~kxstudio-debian/+archive/kxstudio/+files/kxstudio-repos_11.1.0_all.deb

# Install it
sudo dpkg -i kxstudio-repos_11.1.0_all.deb

sudo apt install zynaddsubfx -y

notify "Install Surge XT"

wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.1/surge-xt-linux-x64-1.3.1.deb

sudo apt install xclip -y

sudo dpkg -i surge-xt-linux-x64-1.3.1.deb

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

notify "Installing x42 General Midi Synth"

wget -O gm.tar.gz "https://x42-plugins.com/x42/linux/x42-gmsynth-v0.6.0-x86_64.tar.gz"

tar xavf gm.tar.gz

cd x42-gmsynth/

sh install-lv2.sh

sudo apt install x42-plugins -y



notify "Installing Musescore"

sudo apt install musescore -y


notify "Installing Sox and bpm-tools find for tempo estimation LUA script"

sudo apt install sox bpm-tools -y

notify "download and installing  ardour config files"

sudo apt install git -y

git clone https://github.com/jmantra/LogicalArdour.git

cp -rf LogicalArdour/bookworm/ardour7 ~/.config/

rm -rf LogicalArdour/*


# ---------------------------
notify "Done - please reboot."

