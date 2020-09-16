# Camera (Timelapse)
Take timelapse photos with a Raspberry Pi camera and automatically generate an MP4 on a daily basis

---
## Getting Started

- Use [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) to:
  - Set the Memory Split value to a value of at least 192MB
  - Enable the CSI camera interface
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
+ _--renderVideo_ : Set whether a video is generated every 24 hours     *(default: True)*
+ _--uploadVideo_ : Set whether to automatically upload videos to YouTube    *(default: False)*
+ _--privacy_ : Set the privacy status of the YouTube video  *(default: public)*

---

## Automatic YouTube Upload

To use the automatic YouTube upload feature, you will need to: 
+ Obtain an OAuth 2.0 client ID and client secret from the [Google Developers Console](https://console.developers.google.com/apis/credentials)
+ Add the appropriate values into a config.json file (see example file)

NOTE: These steps are _only_ required if you wish to use the automatic upload feature.
