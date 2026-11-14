#!/bin/bash
# ---------------------------
# This is a bash script for configuring Debian 13 (trixie) for pro audio.
# This is based on Brendan Ingram's Linux Audio Setup Scripts at https://github.com/brendaningram/linux-audio-setup-scripts
# ---------------------------


# Exit if any command fails
set -e

if [ -r /etc/os-release ]; then
  . /etc/os-release
fi
if [ "${VERSION_CODENAME:-}" != "trixie" ]; then
  echo "This script is for Debian 13 (trixie). This system is ${VERSION_CODENAME:-unknown}." >&2
  exit 1
fi

notify () {
  echo "--------------------------------------------------------------------"
  echo $1
  echo "--------------------------------------------------------------------"
}

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

chmod_opt_binaries() {
    sudo bash -c 'while IFS= read -r -d "" path; do
        sig=$(od -An -t x1 -N 4 "$path" 2>/dev/null | tr -d " \n" || true)
        if [ "$sig" = "7f454c46" ]; then
            chmod 755 "$path"
        fi
    done < <(find /opt/LogicalArdour -type f -print0)
    exit 0'
}


# ---------------------------
# Update our system
# ---------------------------
notify "Update the system"
sudo apt update && sudo apt upgrade -y


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

while true; do
  read -p "Do you already have Ardour installed? If you say no, Ardour 8 will be installed from the Debian repositories (y/n): " choice
  case "$choice" in
    y|Y )
      while true; do
        read -p "Which Ardour do you have installed? (8/9): " ardour_choice
        case "$ardour_choice" in
          8)
            ardour_major=8
            break
            ;;
          9)
            ardour_major=9
            break
            ;;
          *)
            echo "Please enter 8 or 9."
            ;;
        esac
      done
      echo "Using the Ardour ${ardour_major} configuration."
      break
      ;;
    n|N )
      echo "Installing Ardour 8"
      sudo apt install ardour -y
      ardour_major=8
      break
      ;;
    *)
      echo "Invalid input. Please enter y or n."
      ;;
  esac
done

sudo apt install wget -y

notify "Install zynaddsubfx"
# Install required dependencies if needed
sudo apt-get install apt-transport-https gpgv wget

# Download package file
wget https://launchpad.net/~kxstudio-debian/+archive/kxstudio/+files/kxstudio-repos_11.2.0_all.deb

# Install it
sudo dpkg -i kxstudio-repos_11.2.0_all.deb
sudo apt update

sudo apt install zynaddsubfx zynaddsubfx-lv2 zynaddsubfx-data -y

notify "Install Surge XT"

wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.1/surge-xt-linux-x64-1.3.1.deb

sudo apt install xclip -y

sudo dpkg -i surge-xt-linux-x64-1.3.1.deb

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

notify "Installing LogicalArdour"

sudo apt install git -y

git clone https://github.com/jmantra/LogicalArdour.git

cd LogicalArdour

sudo mkdir -p /opt/LogicalArdour

sudo cp LogicalArdour.sh /opt/LogicalArdour/LogicalArdour.sh
sudo chmod 755 /opt/LogicalArdour/LogicalArdour.sh
echo "$ardour_major" | sudo tee /opt/LogicalArdour/ardour-major >/dev/null

rm -f "$HOME/.local/share/applications/LogicalArdour.desktop"
sudo cp LogicalArdour.desktop /usr/share/applications/LogicalArdour.desktop
sudo chmod 644 /usr/share/applications/LogicalArdour.desktop
if command -v update-desktop-database >/dev/null 2>&1; then
  sudo update-desktop-database /usr/share/applications
fi

sudo cp -a resources/. /opt/LogicalArdour/
chmod_opt_binaries
sudo rm -rf /opt/LogicalArdour/mma
sudo cp -a mma /opt/LogicalArdour/mma

sudo cp minibpm /opt/LogicalArdour/minibpm
sudo chmod +x /opt/LogicalArdour/minibpm

folder="$HOME/.lv2"
backup_or_create_folder "$folder"
cp -rf lv2/* "$HOME/.lv2"

folder="$HOME/.local/share/Trackbout/Ripchord/Presets/"
backup_or_create_folder "$folder"
cp -rf Ripchord/* "$folder"

folder="$HOME/.vst3"
backup_or_create_folder "$folder"
cp -rf vst3/* "$HOME/.vst3"

folder="$HOME/.ladspa"
backup_or_create_folder "$folder"
cp -rf ladspa/* "$HOME/.ladspa"

sudo cp -rf samples/* /opt/LogicalArdour

folder="$HOME/.config/MuseScore"
backup_or_create_folder "$folder"
cp MuseScore3.ini "$HOME/.config/MuseScore"
cp MuseScore2.ini "$HOME/.config/MuseScore"

folder="$HOME/.config/guitarix"
backup_or_create_folder "$folder"
cp -rf guitarix/* "$folder"

sudo apt install -y libwebkit2gtk-4.1-dev libwebkit2gtk-4.1-0 cargo rustc pkg-config
if [ -f score-editor/Cargo.toml ]; then
  cargo build --release --no-default-features --manifest-path score-editor/Cargo.toml
  sudo cp score-editor/target/release/score-editor /opt/LogicalArdour/score-editor
  sudo chmod 755 /opt/LogicalArdour/score-editor
fi
chmod_opt_binaries

ardour_tree="ardour${ardour_major}"
folder="$HOME/.config/LogicalArdour/${ardour_tree}"
backup_or_create_folder "$folder"
cp -rf "${ardour_tree}"/* "$folder"

for file in "$HOME/.config/LogicalArdour/${ardour_tree}"/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/justin", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done
for file in "$HOME/.config/LogicalArdour/${ardour_tree}"/route_templates/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/justin", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done
for file in $HOME/.config/MuseScore/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/justin", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done

cd ..
rm -rf LogicalArdour


# ---------------------------
notify "Done - please reboot."

