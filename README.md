# Camera (Timelapse)
Take timelapse photos with a Raspberry Pi camera and automatically generate an MP4 on a daily basis.  ~~Optionally upload the daily timelapse to YouTube.~~

---

## Getting Started

- Use [Raspberry Pi Imager](https://www.raspberrypi.com/software) to install Raspberry Pi OS 64-bit Lite *(Bookworm)* on a microSD card
- Use [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md) to:
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
+ _--exifFStop_ : Set the numeric F-Stop value in the image EXIF data *(default: Not specified)*
+ _--exifFocalLength_ : Set the numeric Focal Length value (mm) in the image EXIF data *(default: Not specified)*
+ _--exifFocalLengthEquivalent_ : Set the numeric 35mm Focal Length value (mm) in the image EXIF data *(default: Not specified)*
+ _--outputFolder_ : Set the folder where images will be saved     *(default: dcim/)*
+ _--retention_ : Set the number of days to locally retain the captured files    *(default: 7)*
+ _--waitUntilAnalysis_ : Set whether to perform an initial analysis.     *(default: False)*
+ _--renderVideo_ : Set whether a video is generated every 24 hours     *(default: True)*
+ _--uploadVideo_ : Set whether to automatically upload videos to YouTube    *(default: False)*
+ _--privacy_ : Set the privacy status of the YouTube video  *(default: public)*


### Example
```
camera.timelapse --rotate 180 -exifFStop 2.2 --exifFocalLength 2.75 --exifFocalLengthEquivalent --retention 14 --uploadVideo True
```

> [!TIP]
> The EXIF data shown above is completely optional but may prove useful when using captured images with third-party applications such as photogrammetry software.

---

## Automatic YouTube Upload

> [!IMPORTANT]
Due to restrictive changes in the YouTube authentication rules, the automatic YouTube upload feature is not currently operational.   We are actively researching alternative methods.


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

> [!NOTE]
> While IR cameras utilize "invisible" (outside the spectrum of the human eye) light, they can not magically see in the dark.   You will need to illuminate night scenes with one or more IR lights to take advantage of an Infrared Camera.

---

> [!IMPORTANT]
> *This application was developed using a Raspberry Pi V3 12MP (2023) camera and a Raspberry Pi Zero 2 W board.   This application should also work without issue with Raspberry Pi 5 boards, Raspberry Pi 4B boards and Raspberry Pi HQ (2020) cameras.   Issues may arise if you are using either third party or older hardware.*

