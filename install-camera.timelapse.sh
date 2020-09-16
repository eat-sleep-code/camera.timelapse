# This script will install the camera and any required prerequisites.
cd ~
echo -e ''
echo -e '\033[32mCamera [Installation Script] \033[0m'
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e ''
echo -e '\033[93mUpdating package repositories... \033[0m'
sudo apt update

echo ''
echo -e '\033[93mInstalling prerequisites... \033[0m'
sudo apt install -y git python3 python3-pip python3-picamera ffmpeg
sudo pip3 install ffmpeg-python google-api-python-client oauth2client 


echo ''
echo -e '\033[93mInstalling Camera... \033[0m'
cd ~
sudo rm -Rf ~/camera.timelapse
sudo git clone https://github.com/eat-sleep-code/camera.timelapse
sudo chown -R $USER:$USER camera.timelapse
cd camera.timelapse
sudo chmod +x camera.timelapse.py
sudo chmod +x camera.timelapse.upload.py

echo ''
echo -e '\033[93mCreating Service... \033[0m'
sudo mv camera.timelapse.service /etc/systemd/system/camera.timelapse.service
sudo chown root:root /etc/systemd/system/camera.timelapse.service
sudo chmod +x *.sh 

cd ~
echo ''
echo -e '\033[93mSetting up aliases... \033[0m'
sudo touch ~/.bash_aliases
sudo sed -i '/\b\(function camera.timelapse\)\b/d' ~/.bash_aliases
sudo sed -i '$ a function camera.timelapse { sudo python3 ~/camera.timelapse/camera.timelapse.py "$@"; }' ~/.bash_aliases
echo -e 'You may use \e[1mcamera.timelapse <options>\e[0m to launch the program.'
echo ''
echo 'To use the automatic YouTube upload feature, you will need to update the config.json.'
echo 'Please see the README file for more information.'
echo ''
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e '\033[32mInstallation completed. \033[0m'
echo ''
bash
