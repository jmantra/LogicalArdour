#!/bin/bash






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

sudo mkidr /usr/local/lib/vst3

sudo cp -rf drumlabooh/drumlabooh.vst3/ /usr/lib/vst3

sudo cp -rf drumlabooh/drumlabooh-multi.vst3/ /usr/lib/vst3

sudo cp -rf drumlabooh-kits /usr/local/share







folder="$HOME/.config/ardour8"
backup_or_create_folder "$folder"

cp -rf ardour8/*  $folder

for file in $HOME/.config/ardour8/*; do
    if [ -f "$file" ]; then
        awk -v home="$HOME" '{gsub("/home/jman", home); print}' "$file" > tmp && mv tmp "$file"
    fi
done



#DIR=$(find /opt -maxdepth 1 -type d -name "Ardour-*" | sort -V | tail -n 1)




sudo cp -rf media/* /usr/share/ardour8/media


cd "$HOME/Downloads"


rm -rf LogicalArdour/*





ln -sf '/opt/LogicalArdour/soundfonts/Dance Drums.sf2' ~/.lv2/ACE_Fluid_Synth_Dance_Drums.lv2/'Dance Drums.sf2'

ln -sf '/opt/LogicalArdour/soundfonts/Power Drums.sf2' ~/.lv2/ACE_Fluid_Synth_Power_Drums.lv2/'Power Drums.sf2'

ln -sf '/opt/LogicalArdour/soundfonts/Power Drums.sf2' ~/.lv2/ACE_Fluid_Synth_Electronic_Drums.lv2/'Electronic Drums.sf2'


ln -sf '/opt/LogicalArdour/soundfonts/Room Drums.sf2' ~/.lv2/ACE_Fluid_Synth_Room_Drums.lv2/'Room Drums.sf2'

ln -sf '/opt/LogicalArdour/soundfonts/Standard 2 Drums.sf2' ~/.lv2/ACE_Fluid_Synth_Standard_2_Drums.lv2/'Standard 2 Drums.sf2'

ln -sf '/opt/LogicalArdour/soundfonts/Jazz Drums.sf2' ~/.lv2/ACE_Fluid_Synth_Jazz_Drums.lv2/'Jazz Drums.sf2'

ln -sf '/opt/LogicalArdour/soundfonts/Brush Drums.sf2' ~/.lv2/ACE_Fluid_Synth_Brush_Drums.lv2/'Brush Drums.sf2'

ln -sf '/opt/LogicalArdour/soundfonts/Orchestral Perc.sf2' ~/.lv2/ACE_Fluid_Synth_Orchestral_Perc.lv2/'Orchestral Perc.sf2'

ln -sf '/opt/LogicalArdour/soundfonts/808.sf2' ~/.lv2/ACE_Fluid_Synth_808.lv2/'808.sf2'









