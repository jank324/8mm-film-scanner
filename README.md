# 8mm Film Scanner

The *8mm Film Scanner* is a project to build a scanner for digitising motion picture film in both the *Regular 8* and *Super 8* gauges by converting an old projector with the help of a [Raspberry Pi](https://www.raspberrypi.org) single board computer.

In this repository, I have collected all my materials on this project, including source code, information on the hardware and software design, instructions for using the software, a rundown of my scanning and editing workflow, and many more.

<img src="icon.svg" align="right" width="25%"/>

### Table of contents
- [Introduction](#introduction)
- [Detailed technical description](#detailed-technical-description)
    - [Hardware design](#hardware-design)
        - [Projector conversion](#projector-conversion)
        - [Camera](#camera)
        - [Electrical systems](#electrical-systems)
        - [Base plate and case](#base-plate-and-case)
    - [Software design](#software-design)
        - [Scanning operations](#scanning-operations)
        - [Dashboard and other user experience](#dashboard-and-other-user-experience)
    - [Scanning workflow](#scanning-workflow)
    - [Cost](#cost)
    - [Future features and fixes](#future-features-and-fixes)
- [Run the software on your own scanner](#run-the-software-on-your-own-scanner)
    - [Installation](#installation)
    - [How to use](#how-to-use)
- [Contributing](#contributing)
- [Acknowledgements](#acknowledgements)

<img src="resource/three_quarter_view.png" align="center" width="100%"/>


## Introduction

I while ago, I found myself with over 800 rolls of 8mm film my grandfather had filmed throughout the 1960s, 70s and 80s. Having just digitised my grandparents' photo collection, naturally I wanted to know what was on these 8mm films and digitise them as well, so they would be safe from further deterioration and so we would actually watch them instead of always being too lazy to set up the projector.

Now, the easiest way to get films like these digitised is the use of a digitisation service. But for the sheer amount of film I had, this would have cost me well over 10,000€ and with these services you never know whether you will actually get a decent quality scan. The next option was to just get out the old projector and use a video camera to record the films as they play. This is a perfectly valid option and super easy to do, but the resulting recordings usually suffer from distortion, bad colours, a lack of sharpness and quite a bit of flicker. To do the true quality of these films justice, what was really needed was a frame-by-frame scanner. You can actually buy these but the ones available are either so expensive that they only make sense for professional users (e.g. scanners by [Filmfabriek](https://filmfabriek.nl)) or they leave a lot to be desired in terms of quality (like the famed [Wolverine](https://www.wolverinedata.com/products/MovieMaker_Pro)).

The solution is to build your own scanner, an idea that got hooked on after finding a [video on the AACA Library's *Mike's Movie Machine*](https://www.youtube.com/watch?v=luGacxJMZI8), which is really just an incarnation of the absolutely amazing [*Kinograph*](https://www.kinograph.cc) project. TODO [Kinograph Forums](https://forums.kinograph.cc)

In the following, you will find a detailed description of my *8mm Film Scanner* and the workflow around it. The scanner is built around an old dual-gauge film projector and a [Raspberry Pi](https://www.raspberrypi.org) single board computer.

Below you find a photo of my scanner, a screenshot of its web interface as well as a sample scan.

TODO Insert photo, screenshot and sample scan.

<img src="https://www.bonanza.org/globalassets/photos/homepage-hero/leone4.jpg" align="center" width="100%"/>

The rest of this README is intended as a documentation of every detail and lesson learned about my scanner. The goal here is to provide all the information and source code necessary to build another one.


## Detailed technical description

This section will go over every technical detail of the *8mm Film Scanner*. The goal is to document everything necessary to rebuild the scanner some day far in the future without having to redo all the research I did.


### Hardware design

Lorem ipsum ...


#### Projector conversion

The scanner is built around a *Bolex 18-3 TC* dual gauge film projector. There is no is no particular reason why I used this projector other than that I was able to get it cheaply because it was sold as defective. I never tested the electrics of the projector but the film transport mechanism turned out to be in perfectly find condition, which is all I cared about for this project.

There do exist some almost identical models to this one by Bolex and Eumig, inclduing the Bolex 18-3 Duo, Eumig 610 D, Eumig 605 D and Eumig 614 D.

In order to convert the projector, I removed the power supply and the motor/fan assembly. In its place, I mounted an acrylic plate

also remove lens

mount stepper motor, motor driver hall effect sensor and magnet on aperture wheel

Replace lamp with MR16 LED and place plexiglas sheet in front of it for diffusion


#### Camera

Raspberry Pi HQ camera for quality and replicability of lens on C-Mount

Mount to Schneider-Kreuznach Componon-S 50mm for flat image plane

using some adapters and distance thingies to enlarger the image macro

leave just enough space around the image to have wiggle room but also give high resolution

sharpness falls off quickly when changing aperture always use aperture f4 (?)

macro slider for fine focus adjustment


#### Electrical systems

<img src="schematic.svg" align="center" width="100%"/>

Everything powered via a USB-C power supply

USB-C PD trigger board set to 15V

two step down converters to give 5V supply and 12V supply

5V to Raspberry Pi via USB cable to keep safety in circuit

12V to power LED and stepper motor

LED connected via old GU5.3 Fassung

Stepper motor via A4988 driver on practical PCB

Computations on energy usage


#### Base plate and case

Include constructionszeichnungen mit Maßen

Wooden frame and case from plywood to protect electronics and make easy to stow

wooden case with lid. cooling fan on "grill" keeps Pi cooler than it would be outside

PCBs mounted with double sided tape

Projector mounted using mounting holes for original feet, used paper to trace over, M6 screws, spacers to deal with tilt

Camera mounted on macro slider, on wooden plate for rough adjustments left and right and up and down

Case is painted in edding clear coat


### Software design

Two parts

server handling scanning and web interface


#### Scanning operations

something about the scanning, advancing, stepper motor driving and hall detection


#### Dashboard and other user experience

web interface for easy use, describe video streaming and message structures


### Scanning workflow

Note that this is not the only way to do it and in particular the particular softwares I use can be replaced with others easily

Scan to RAW, to SSD (because SSD faster than internal)

Convert raw bayer data to .dng files with script and RPiDNG

Adjust colour and crop, then export to tiff

From tiff files render into master video file (I use Apple Compressor to ProRes)

Import into Final cut, crop to 4:3 and use Neat Video to remove what I feel like might be digital noise but preserve film grain

Then use Neat and if required manual work to remove dust "that I find distracting".

Chose not to completely degrain or stabilise to keep analog feel and not outstabilise original handshake


### Cost

Put a table here of cost of everythin


### Future features and fixes

Dashboard camera settings, mounting PCBs in case


## Run the software on your own scanner

Feel free to use this software on your own scanner

brief instrictions

prerequestie is that electrical connections are the same

advance routine might need adjusting as timed to this scanner


### Installation

Not tested because I have only one piece of hardware

Ensure same connections as those described above as well as Raspberry Pi with Raspberry Pi OS installed as normal

Clone repository (`Desktop`).

```sh
git clone https://github.com/jank324/8mm-film-scanner.git
```

Install python packages

```sh
sudo python3 -m pip install -r requirements.txt
```

Need *npm* installed.

`cd` to `frontend` directory.

```sh
cd frontend
```

install packages

```sh
npm install
```

then build frontend via

```sh
npm run build
```

`cd` back to the project root (`..`) then you can start the server by running

```sh
sudo python3 server.py
```

You probably want to run the server on boot of the Pi ...

This repository provides a *systemd* service `8mmfilmscanner.service` that runs the 8mm Film Scanner's server on boot. To set up the service, copy the `.service` file to `/etc/systemd/system` by running

```bash
sudo cp 8mmfilmscanner.service /etc/systemd/system/
```

and then enable it via

```bash
systemctl enable 8mmfilmscanner
```

then to send email notifications on finished scans

create mail account of your choice

create file `notification_config.yaml` in project root directory

Fill in the following with the details of your mail account and the mail address you want e-mails to be sent to

```yaml
user: scanners@mail.com         # Address of the scanner's account
password: scannerspassword123   # Password of the scanner's account
to: your@mail.com               # Address notifications are sent to (presumably your own)
```

Please remember to **NEVER** commit `notification_config.yaml` as it contains the password to the scanner's mail account which should remain secret. Under normal circumstances, this repository's `.gitignore` should already take care of this.

### How to use

Type in path, click here to start scan or turn on light etc. ...


# Contributing

basically say please feel free to use and contribute by issues and pull requests


# Acknowledgements

Kinograph forum (and Matthew Aepler)
