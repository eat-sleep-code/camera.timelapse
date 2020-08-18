# camera.timelapse
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

+ _--interval_ : Set the timelapse interval    *(default: 60)*
+ _--framerate_ : Set the output framerate     *(default: 60)*
+ _--renderVideo_ : Set whether a video is generated every 24 hours     *(default: True)*
+ _--outputFolder_ : Set the folder where images will be saved     *(default: dcim/)* 
