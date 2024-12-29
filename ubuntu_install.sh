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
      sudo  cp -r "$folder" "${folder}_backup"
    else
        echo "Folder '$folder' does not exist. Creating folder..."
     sudo   mkdir -p "$folder"
    fi
}

cd "$HOME/Downloads"


while true; do
  read -p "Do you already have Ardour installed? If you say no Ardour will be compiled/installed for you (y/n): " choice
  case "$choice" in
    y|Y )
      # Replace the URL with the actual link to the file you want to download
   echo "Skipping Ardour install"

      break
      ;;
    n|N )
      echo "Compiling Ardour"
      cd $HOME
    sudo apt install build-essential git libboost-all-dev gcc g++ pkg-config libasound2-dev libgtk2.0-dev libglibmm-2.4-dev libsndfile1-dev libarchive-dev liblo-dev libtag1-dev vamp-plugin-sdk librubberband-dev libfftw3-dev libaubio-dev libxml2-dev libsamplerate0-dev lv2-dev libserd-dev libsord-dev libsratom-dev liblilv-dev libgtkmm-2.4-dev libjack-jackd2-dev libogg-dev libcppunit-dev libudev-dev libwebsockets-dev libusb-dev libsuil-dev libdbus-1-dev xjadeo libusb-1.0-0-dev libreadline-dev  libarchive-dev liblo-dev libtag1-dev libvamp-sdk2v5 librubberband-dev libaubio-dev libpangomm-1.4-dev libserd-dev libsord-dev libsratom-dev liblilv-dev libgtkmm-2.4-dev libsuil-dev libcppunit-dev python3 liblrdf0-dev libraptor2-dev python-is-python3 git -y

    git clone https://github.com/Ardour/ardour.git
    cd ardour
    git checkout 8.10

    ./waf configure --cxx11 --optimize
    ./waf -j `nproc`
    ./waf install

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

    sudo apt install libspa-0.2-jack -y

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
echo "jackd2 jackd/tweak_rt_limits boolean true" | sudo debconf-set-selections

sudo apt install yoshimi -y 


sudo apt install x42-plugins avldrums.lv2 swh-lv2 calf-plugins tap-plugins  guitarix-lv2  mda-lv2  -y




wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.1/surge-xt-linux-x64-1.3.1.deb

sudo apt install xclip -y

sudo apt install libxcb-cursor0 -y


sudo dpkg -i surge-xt-linux-x64-1.3.1.deb

#sudo apt upgrade -y
sudo apt install zam-plugins -y


sudo apt install samplv1 -y


sudo apt install git -y

git clone https://github.com/jmantra/LogicalArdour.git

cd LogicalArdour








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

folder="/usr/lib/ladspa"
 sudo_backup_or_create_folder "$folder"

sudo cp -rf ladspa-rubberband.cat $folder
sudo cp -rf ladspa-rubberband.so $folder






sudo mkdir -p /opt/LogicalArdour

sudo cp -rf samples/* /opt/LogicalArdour

sudo apt install libfuse3-3 libfuse3-dev libfuse2t64 -y
wget https://jmantra.blob.core.windows.net/data/mscore
sudo cp -rf mscore /opt/LogicalArdour
sudo chmod 755 /opt/LogicalArdour

folder="$HOME/.config/MuseScore"
backup_or_create_folder "$folder"

cp MuseScore3.ini $HOME/.config/MuseScore

if [ "$compiled" = true ]; then

  if [ "$pipewire" = true ]; then
    sudo cp pwardour.desktop /usr/share/applications/ardour.desktop
  else
    sudo cp ardour.desktop /usr/share/applications/ardour.desktop
  fi

else

  check_file_pattern() {
    local file_pattern="$1"  # Argument to the function
    # Check if any file matches the pattern
    if match=$(ls $file_pattern 2> /dev/null); then
      echo "Matching file(s):"
      echo "$match"
      desktop=$match
    else
      echo "No files matching '$file_pattern' were found."
    fi
  }

  check_file_pattern "/usr/share/applications/Ardour-Ardour_8.10.0.desktop"
 if [ -z "$desktop" ]; then
 check_file_pattern "/usr/share/applications/ardour.desktop"
else
  echo "Desktop file already exists. No action needed."
fi

  if [ "$pipewire" = true ]; then
    sudo cp pwregardour.desktop "$desktop"
  else
    sudo cp regardour.desktop "$desktop"
  fi

fi
for file in $HOME/.config/ardour8/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/[^/]+", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done
for file in $HOME/.config/ardour8/route_templates/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/[^/]+", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done
for file in $HOME/.config/MuseScore/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/[^/]+", home); print}' "$file" > tmp && mv tmp "$file"
    fi
    done



wget https://jmantra.blob.core.windows.net/data/key

sudo cp key /opt/LogicalArdour

sudo chmod 755 /opt/LogicalArdour/key

wget https://jmantra.blob.core.windows.net/data/newchord

sudo cp newchord /opt/LogicalArdour

sudo chmod 755 /opt/LogicalArdour/newchord


wget https://jmantra.blob.core.windows.net/data/bassline_generator

sudo cp bassline_generator /opt/LogicalArdour

sudo chmod 755 /opt/LogicalArdour/bassline_generator
sudo mkdir /usr/local/lib/vst3



folder="$HOME/.config/ardour8"
backup_or_create_folder "$folder"

cp -rf ardour8/*  $folder

folder="$HOME/.config/guitarix"
backup_or_create_folder "$folder"

cp -rf guitarix/*  $folder

for dir in "$HOME/.config/ardour8" "$HOME/.config/ardour8/route_templates" "$HOME/.config/MuseScore"; do
    for file in "$dir"/*; do
        if [ -f "$file" ]; then
            awk -v home="$HOME" '{gsub("/home/[^/]+", home); print}' "$file" > tmp && mv tmp "$file"
        fi
    done
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










