#!/bin/bash


sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

 sudo dnf install gstreamer1-plugins-{bad-\*,good-\*,base} gstreamer1-plugin-openh264 gstreamer1-libav --exclude=gstreamer1-plugins-bad-free-devel

sudo dnf install lame* --exclude=lame-devel








cd "$HOME/Downloads"

sudo dnf install ardour8







sudo dnf install musescore






# Key


wget https://jmantra.blob.core.windows.net/data/key



sudo cp key /usr/bin

sudo chmod 755 /usr/bin/key

#BPM

wget https://jmantra.blob.core.windows.net/data/bpmbin



sudo cp bpmbin /usr/bin

sudo chmod 755 /usr/bin/bpmbin



sudo dnf install zynaddsubfx lv2-zynadd-plugins lv2-swh-plugins ladspa-tap-plugins calf lv2-x42-plugins











wget https://github.com/surge-synthesizer/releases-xt/releases/download/1.3.4/surge-xt-x86_64-1.3.4.rpm

sudo dnf install surge-xt-x86_64-1.3.4.rpm











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

sudo cp -rf drumlabooh/drumlabooh.vst3/ /usr/lib/vst3

sudo cp -rf drumlabooh/drumlabooh-multi.vst3/ /usr/lib/vst3

sudo cp -rf drumlabooh-kits /usr/local/share

sudo cp -rf mda-lv2/ /usr/lib/lv2

sudo cp -rf gx/* /usr/lib/lv2









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





ln -sf '/opt/LogicalArdour/Power Drums/Power Drums.sfz' ~/.lv2/sfizz_Power_Drums.lv2/'Power Drums.sfz'

ln -sf '/opt/LogicalArdour/Dance Drums/Dance Drums.sfz' ~/.lv2/sfizz_Dance_Drums.lv2/'Dance Drums.sfz'

ln -sf '/opt/LogicalArdour/Electronic/Electronic Drums.sfz' ~/.lv2/sfizz_Electronic_Drums.lv2/'Electronic Drums.sfz'

ln -sf '/opt/LogicalArdour/Jazz Drums/Jazz Drums.sfz' ~/.lv2/sfizz_Jazz_Drums.lv2/'Jazz Drums.sfz'

ln -sf '/opt/LogicalArdour/Room Drums/Room Drums.sfz' ~/.lv2/sfizz_Room_Drums.lv2/'Room Drums.sfz'

ln -sf '/opt/LogicalArdour/Standard 2 Drums/Standard 2 Drums.sfz' ~/.lv2/sfizz_Standard_2_Drums.lv2/'Standard 2 Drums.sfz'

ln -sf '/opt/LogicalArdour/Brush Drums/Brush Drums.sfz' ~/.lv2/sfizz_Brush_Drums.lv2/'Brush Drums.sfz'

ln -sf '/opt/LogicalArdour/808 Drums/808_909 Drums.sfz' ~/.lv2/sfizz_808.lv2/'808_909 Drums.sfz'

ln -sf '/opt/LogicalArdour/Orchestral Perc/048_Orchestral Perc..sfz' ~/.lv2/sfizz_Orchestral_Perc.lv2/'048_Orchestral Perc..sfz'
