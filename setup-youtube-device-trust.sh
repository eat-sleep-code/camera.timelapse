# This script will initiate the YouTube device trust.
cd ~
echo -e ''
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e ''

echo -e '\033[93mCreating temporary file... \033[0m'
sudo touch ~/dcim/youtube-device-trust.mp4

echo -e '\033[93mStarting verifcation process... \033[0m'
python3 ~/camera.timelapse/camera.timelapse.upload.py --file ~/dcim/youtube-device-trust.mp4 --noauth_local_webserver

echo -e '\033[93mRemove temporary file... \033[0m'
sudo rm ~/dcim/youtube-device-trust.mp4
echo ''
