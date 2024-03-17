#!/bin/bash 

 

sudo su  

 

apt install wget -y 

 

 

sudo apt install gstreamer1.0-pipewire libpipewire-0.3-{0,dev,modules} libspa-0.2-{bluetooth,dev,jack,modules} pipewire{,-{audio-client-libraries,pulse,bin,jack,alsa,v4l2,tests}} -y  

systemctl --user --now enable pipewire{,-pulse}.{socket,service}  

systemctl --user --now enable wireplumber.service  

# After the set of commands above, you need to tell all apps that use JACK to now use the Pipewire JACK:  

sudo cp /usr/share/doc/pipewire/examples/ld.so.conf.d/pipewire-jack-*.conf /etc/ld.so.conf.d/  

sudo ldconfig  

 

 sudo apt install ardour -y 

 

sudo dpkg --add-architecture i386  

 

sudo mkdir -pm755 /etc/apt/keyrings 

 

sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key 
 

 

sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/mantic/winehq-mantic.sources 

 

sudo apt update 

 

sudo apt install winehq-staging=8.21~mantic-1 

 

sudo apt install cabextract –y 

 

mkdir -p ~/.local/share 

 

wget -O winetricks https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks 

 

mv winetricks ~/.local/share 

echo '# Audio: winetricks' >> ~/.bash_aliases 

echo 'export PATH="$PATH:$HOME/.local/share"' >> ~/.bash_aliases 

. ~/.bash_aliases 

 

winetricks corefonts 

 

cp -r ~/.wine ~/.wine-base 

 

wget -O yabridge.tar.gz https://github.com/robbert-vdh/yabridge/releases/download/5.1.0/yabridge-5.1.0.tar.gz 

 

mkdir -p ~/.local/share 

 

tar -C ~/.local/share -xavf yabridge.tar.gz 

 

rm yabridge.tar.gz 

 

echo '' >> ~/.bash_aliases 

 

echo '# Audio: yabridge path' >> ~/.bash_aliases 

 

echo 'export PATH="$PATH:$HOME/.local/share/yabridge"' >> ~/.bash_aliases 

 

sudo apt install libnotify-bin -y 

 

mkdir -p "$HOME/.wine/drive_c/Program Files/Steinberg/VstPlugins" 

 

mkdir -p "$HOME/.wine/drive_c/Program Files/Common Files/VST2" 

 

mkdir -p "$HOME/.wine/drive_c/Program Files/Common Files/VST2" 

 

 

 

yabridgectl add "$HOME/.wine/drive_c/Program Files/Steinberg/VstPlugins" 

yabridgectl add "$HOME/.wine/drive_c/Program Files/Common Files/VST2" 

yabridgectl add "$HOME/.wine/drive_c/Program Files/Common Files/VST3" 

 

 

wget -O mtpower.zip https://downloads.manda-audio.com/download76187/mtpdk2_free/2.1.2/MTPDK-2.1.2-VST2-64bit-Linux-with-Wine-FULL.zip 

 

Unzip mtpower.zip 

 

cp MT-Power*  "$HOME/.wine/drive_c/Program Files/Common Files/VST2" 

rm MT-Power*  

rm 'Info for Linux users.txt' 

 

rm mtpower.zip 

 

wget -O beatdrmr.zip http://studiodrive.de/upload/plugins/Beat_DRMR-Win.zip 

 

cp -r  Beat_DRMR-Win/VST64 "$HOME/.wine/drive_c/Program Files/Common Files/VST2"  

 

 

yabridgectl sync 

 

sudo apt install zynaddsubfx zynaddsubfx-vst 

 

wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.1/surge-xt-linux-x64-1.3.1.deb 

  

dpkg -i surge-xt-linux-x64-1.3.1.deb 

 

sudo apt --fix-broken install 

 

sudo apt install musescore  

 
