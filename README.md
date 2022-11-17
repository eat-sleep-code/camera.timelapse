# Camera (Timelapse)
Take timelapse photos with a Raspberry Pi camera and automatically generate an MP4 on a daily basis.  Optionally upload the daily timelapse to YouTube.

---

## Getting Started

- Use [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) to:
  - Set the Memory Split value to a value of at least 192MB
  - Enable the CSI camera interface
  - Enable Legacy Camera Support (if applicable)
  - Set up your WiFi connection
- Connect the Raspberry Pi camera to your Raspberry Pi


## Installation

Installation of the program, as well as any software prerequisites, can be completed with the following two-line install script.

```
wget -q https://raw.githubusercontent.com/eat-sleep-code/camera.timelapse/master/install-camera.timelapse.sh -O ~/install-camera.timelapse.sh
sudo chmod +x ~/install-camera.timelapse.sh && ~/install-camera.timelapse.sh
```

---

## Usage
```
camera.timelapse <options>
```

### Options

+ _--interval_ : Set the timelapse interval    *(default: 10)*
+ _--framerate_ : Set the output framerate     *(default: 60)*
+ _--rotate_ : Rotate the camera in 90&deg; increments     *(default: 0)*
+ _--outputFolder_ : Set the folder where images will be saved     *(default: dcim/)*
+ _--retention_ : Set the number of days to locally retain the captured files    *(default: 7)*
+ _--waitUntilAnalysis_ : Set whether to perform an initial analysis.     *(default: False)*
+ _--renderVideo_ : Set whether a video is generated every 24 hours     *(default: True)*
+ _--uploadVideo_ : Set whether to automatically upload videos to YouTube    *(default: False)*
+ _--privacy_ : Set the privacy status of the YouTube video  *(default: public)*

---

## Automatic YouTube Upload

To use the automatic YouTube upload feature, you will need to: 
+ Obtain an OAuth 2.0 client ID and client secret from the [Google Developers Console](https://console.developers.google.com/apis/credentials)
+ Add the appropriate values into a config.json file (see example file)

NOTE: These steps are _only_ required if you wish to use the automatic upload feature.

---

## Autostart Timelapse Sequence
Want to start the timelapse sequence every time you boot your Raspberry Pi?  Here is how!

* Review `/etc/systemd/system/camera.timelapse.service`
   * If you would like to add any of aforementioned options you may do so by editing the service file.
* Run `~/camera.timelapse/install-camera.timelapse.service.sh`

---

## Infrared Cameras
If you are using an infrared (IR) camera, you will need to modify the Auto White Balance (AWB) mode at boot time.

This can be achieved by executing `sudo nano /boot/config.txt` and adding the following lines.

```
# Camera Settings 
awb_auto_is_greyworld=1
```

Also note, that while IR cameras utilize "invisible" (outside the spectrum of the human eye) light, they can not magically see in the dark.   You will need to illuminate night scenes with one or more to take advantage of an Infrared Camera.

---
:information_source: *This application was developed using a Raspberry Pi HQ (2020) camera and Raspberry Pi 3B+ and Raspberry Pi 4B boards. It has also been tested using v2.1 Raspberry Pi 8MP cameras and Pi Zero W boards.   Issues may arise if you are using either third party or older hardware.*
