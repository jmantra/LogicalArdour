#!/bin/bash


while true; do
  read -p "Do you already have Ardour installed? If you say no Ardour will be installed for you (y/n): " choice
  case "$choice" in
    y|Y )
      # Replace the URL with the actual link to the file you want to download
   echo "Skipping Ardour install"

      break
      ;;
    n|N )
      echo "Installing Ardour from repos"
    sudo dnf install ardour -y
      break
      ;;
    * )
      echo "Invalid input. Please enter y or n."
      ;;
  esac
done

# Continue with the rest of your script here
echo "Continuing with the rest of the script..."


sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm -y

 sudo dnf install gstreamer1-plugins-{bad-\*,good-\*,base} gstreamer1-plugin-openh264 gstreamer1-libav --exclude=gstreamer1-plugins-bad-free-devel -y

sudo dnf install lame* --exclude=lame-devel -y


cd "$HOME/Downloads"


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



sudo dnf install yoshimi lv2-swh-plugins ladspa-tap-plugins calf lv2-x42-plugins







wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.4/surge-xt-x86_64-1.3.4.rpm

sudo dnf -y install surge-xt-x86_64-1.3.4.rpm



sudo dnf -y copr enable patrickl/libcurl-gnutls

sudo dnf -y install libcurl-gnutls --refresh







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

wget https://jmantra.blob.core.windows.net/data/key

sudo cp key /opt/LogicalArdour

sudo chmod 755 /opt/LogicalArdour/key

wget https://jmantra.blob.core.windows.net/data/newchord

sudo cp key /opt/LogicalArdour

sudo chmod 755 /opt/LogicalArdour/newchord

wget https://jmantra.blob.core.windows.net/data/bassline_generator

sudo cp bassline_generator /opt/LogicalArdour

sudo chmod 755 /opt/LogicalArdour/bassline_generator

wget https://jmantra.blob.core.windows.net/data/mscore

sudo cp mscore /opt/LogicalArdour

sudo chmod 755 /opt/LogicalArdour/mscore





sudo cp -rf mda.lv2/ /usr/lib/lv2

sudo cp -rf gx/* /usr/lib/lv2









folder="$HOME/.config/ardour8"
backup_or_create_folder "$folder"

folder="$HOME/.config/guitarix"
backup_or_create_folder "$folder"

cp -rf guitarix/*  $folder

cp -rf ardour8/*  $folder

folder="$HOME/.config/MuseScore"
backup_or_create_folder "$folder"

cp MuseScore3.ini $HOME/.config/MuseScore
cp MuseScore2.ini $HOME/.config/MuseScore

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






