# 8mm Film Scanner

The *8mm Film Scanner* is a project to build a scanner for digitising 8mm motion picture film in both the *Regular 8* and *Super 8* gauges by converting an old projector with the help of a [Raspberry Pi](https://www.raspberrypi.org) single board computer.

In this repository, I have collected all my materials on this project, including source code, information on the hardware and software design, instructions for using the software, a rundown of my scanning and editing workflow and many more.

<img src="icon.svg" align="right" width="25%"/>

### Table of contents
- [Introduction](#introduction)
- [Detailed technical description](#detailed-technical-description)
    - [Hardware design](#hardware-design)
        - [Projector conversion](#projector-conversion)
        - [Camera](#camera)
        - [Electrical systems and wiring](#electrical-systems-and-wiring)
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

![Three-quarter view render](resource/three_quarter_view.png)


## Introduction

I while ago, I found myself with over 800 rolls of 8mm film my grandfather had filmed throughout the 1960s, 70s and 80s. Having just digitised my grandparents' photo collection, naturally I wanted to know what was on these 8mm films and digitise them as well, so they would be safe from further deterioration and so we would actually watch them instead of always being too lazy to set up the projector.

The easiest way to get films like these digitised is the use of a digitisation service. But for the sheer amount of film I had, this would have cost me well over 10,000€ and with these services you never know whether you will actually receive a decent quality scan. The next option was to get out the old projector and use a video camera to record the films as they play. This is a perfectly valid option and super easy to do, but the resulting recordings usually suffer from image distortion, bad colours, a lack of sharpness and quite a bit of flicker. To do the true quality of these films justice, what was really needed was a frame-by-frame scanner that takes an image of every single frame of the film directly off of the film itself. You can actually buy these, but the ones available are either so expensive that they only make sense for professional users (e.g. scanners by [Filmfabriek](https://filmfabriek.nl)) or they leave a lot to be desired in terms of quality (like the famed [Wolverine](https://www.wolverinedata.com/products/MovieMaker_Pro)).

The solution is to build your own scanner, an idea that I got hooked on after finding a [video on the AACA Library's *Mike's Movie Machine*](https://www.youtube.com/watch?v=luGacxJMZI8), which is really just an incarnation of the absolutely amazing [*Kinograph*](https://www.kinograph.cc) project. The Kinograph project is accompanied by the [Kinograph Forums](https://forums.kinograph.cc), quite possibly the best community on motion picture film scanning you will find on the internet, hosting invaluable information and some incredible projects built by talented and passionate people. On scanner build project in particular that I would like to point out as they key inspiration for this project is [the build by Scott Schiller](https://youtube.com/playlist?list=PLIACRGgedheWF4xr1zxiASZ1QqJUfloQ2), who also produced an awesome video series about his scanner and his scanning workflow.

In the following, you will find a detailed description of my *8mm Film Scanner* as well as my scanning workflow, using a dual-gauge film projector and a [Raspberry Pi](https://www.raspberrypi.org) with a *HQ Camera*.

Below you find a photo of my scanner, a screenshot of its web interface as well as a sample scan.

![Photo of the scanner](images/three_quarter.jpeg)

TODO Scanning interface 

TODO Sample scan.

TODO Just an example video
<iframe width="560" height="315" src="https://www.youtube.com/embed/dQVIjNfx9Is" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

The rest of this README is intended as a documentation of every detail and lesson learned about my scanner. The goal here is to provide all the information and source code required to build another one.


## Detailed technical description

This section will go over every technical detail of the *8mm Film Scanner*. The goal is to document everything necessary to rebuild the scanner some day far in the future without having to redo all the research I did.


### Hardware design

TODO ...


#### Projector conversion

The scanner is built around a *Bolex 18-3 TC* dual gauge film projector. There is no is no particular reason why I used this projector other than that I was able to get it cheaply because it was sold as defective. I never tested the electrics of the projector but the film transport mechanism turned out to be in perfectly find condition, which is all I cared about for this project.

There do exist some almost identical models to this one by Bolex and Eumig, including the Bolex 18-3 Duo, Eumig 610 D, Eumig 605 D, Eumig 614 D and Revue Lux 3003.

In order to convert the projector, I removed the power supply and the motor/fan assembly. In its place, I mounted an acrylic plate

also remove lens

mount stepper motor, motor driver hall effect sensor and magnet on aperture wheel

![Projector internals](images/projector_internals.jpeg)

<img src="images/lamphousing_internals.jpeg" align="center" width="80%"/>

Replace lamp with MR16 LED and place plexiglas sheet in front of it for diffusion


#### Camera

The scanner uses a *Raspberry Pi HQ Camera* to capture the frames on the film. This model was chosen because it is easy to use on the Raspberry Pi, the image quality is more than adequate and the C-mount as well as its sensor size make it easy to adapt lenses and achieve the magnification required to have the small film frames fill the camera's sensor.

The lens used is a Schneider-Kreuznach Componon-S 50mm enlarger lens. Today, enlarger lenses are widely available on the used market and well-suited to macro imaging applications. Enlarger lenses also usually have a very flat image plane, helping us avoid focus vignetting. The Componon-S in particular is a very good quality model and a popular choice in the film scanning community, but other similar enlarger lenses are just as well suited.

The chosen lens has an M39 thread and needs to be adapted to the camera's C-mount. It also requires some distance to the sensor to achieve the enlargement required to make a Regular 8 or Super 8 frame fill the camera's sensor. As finding adapters directly from C-mount to M39 turned out to be rather difficult, I chose to adapt via M42-mount. This mount was widely used by Pentax in the 1960s and 70s, making adapters to other mounts as well as macro extension tubes very easy to find. The following components are used to adapt the enlarger lens to the HQ Camera (starting from the camera):

 - C-mount to M42 adapter
 - 19mm M42 extension tube
 - 26mm M42 extension tube
 - M42 to M39 adapter ring (screws into the inside of the M42 thread and is therefore not visible)

 The picture below shows the final camera assembly. Note that the M42-to-M39 adapter is not visible as it screws into the inside of the extension tube's thread before the lens is screwed in.

![Camera](images/camera.jpeg)
% TODO photo of entire camera assembly

Using the HQ Camera's tripod mount, the camera is mounted on a TODO macro slider that can be used to adjust focus. The macro slider itself is mounted to a wooden baseplate via a TODO screw. Four screws are used to mount the base plate to the main plate of the scanner. Using four pairs of nuts and washers, it is possible to adjust the height of the camera. The four wholes to mount the base plate are elongated in parallel to the film plane, allowing for horizontal adjustment of the camera position.


#### Electrical systems and wiring

Below you can see an overview of the scanner's electrical systems with red and black connections representing positive and negative power connections, and all other colours representing signal connections.

![Overview of electrical systems](images/schematic.png)

The scanner is powered by a fairly standard 45W [USB-C power supply](https://www.amazon.de/gp/product/B098P15D4N/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1). The power supply is connected via a USB-C cable with USB-C PD support to a ZY12PDN USB-C PD trigger board. This board is capable of negotiating with the power supply that it should deliver power as well as the USB-C PD mode that is used. Different modes differ primarily in the voltage delivered. The trigger board can be configured via a button on the board to negotiate a particular voltage. In our particular case, the trigger board is configured to negotiate the 15V mode, though 20V would work just as well. Note that the power supply must support the mode. If the power supply does not support the mode the trigger board asks for, USB-C PD will fall back to 5V. At this voltage the scanner will not work, but 5V will not damage it either.

A pair of LM2596S step down modules are then used to step the 15V from the power supply down to 5V required by the Raspberry Pi and 12V for the stepper motor and the LED light. While it would be possible to connect the Pi to the step down converter directly using jumper wires on its GPIO pins, the Micro USB end of an old USB cable is used instead. This keeps the Pi's fuses in circuit and protects the Pi in case of a problem with the power supply.

The stepper motor is driven by an A4988 stepper driver that sits on a [very practical PCB](https://www.amazon.de/gp/product/B07RGJQFSX/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1) that makes it easier to mount and connect the driver. The Pi controls the stepper motor direction via its GPIO 21 pin (white), enables the stepper via its GPIO 16 pin (orange) and steps the motor via its GPIO 20 pin (green). Using the switches on the PCB, the driver is configured to run the stepper motor in full-step mode. Note that this PCB also has additional positive and ground supply pins which are used to make the Pi's 3.3V available in the projector housing due the the location of the Pi in the wooden case.

The LED light is controlled by the Pi using a KF-301 relay module that can switch the 12V supply to the light. The relay receives its logic power from the 3.3V supply of the Pi and is controlled via the Pi's GPIO 6 pin (blue). Note that it is important that the relay is connected to the 3.3V supply and **NOT** the 5V supply, the the logic level is 3.3V and it will not trigger properly otherwise. The relay is connected to the LED light through through the original bulb's GU5.3 socket.

The hall effect sensor, too, is connected to the Pi's 3.3V rail through the stepper PCB. It's digital signal output is connected to the PI via the GPIO 26 pin (purple). Note that a potentiometer on the hall effect sensor module allows for setting the threshold of the digital trigger. This setting will likely need adjusting to make the scanner work properly.

The Pi also supplies a small case fan from its 3.3V supply.

Computations on energy usage


#### Base plate and case

![Drawing](images/engineering_drawing.png)

![Case internals](images/case_internals.jpeg)

Include construction drawings with measurements

Wooden frame and case from plywood to protect electronics and make easy to stow

wooden case with lid. cooling fan on "grill" keeps Pi cooler than it would be outside

PCBs mounted with double sided tape

Projector mounted using mounting holes for original feet, used paper to trace over, M6 screws, spacers to deal with tilt

Camera mounted on macro slider, on wooden plate for rough adjustments left and right and up and down

Case is painted in Edding clear coat


### Software design

The software for this project consists of two parts: the film scanning logic taking care of film advance and image capture, and the user interface logic serving a web interface to simplify and streamline the interaction with the scanner.


#### Scanning operations

something about the scanning, advancing, stepper motor driving and hall detection


#### Dashboard and other user experience

web interface for easy use, describe video streaming and message structures


### Scanning workflow

In this section I would like to briefly go over my current scanning workflow to illustrate how the scanner may be used to produce archivable digital copies of film reels. Note that this is just what my workflow looks like now and likely to change and evolve. It also certainly is not the only way to do it and there is better ways to get the results you are looking for.

Before starting the scan, I actually started by creating a list of all the film I have, giving every film a unique ID so I can identify them later. This allows be to easily track the progress of my scanning project over a long period of time and see which reels I have already scanning or what stage of post-processing I last left them in.

When it is time to scan a particular reel, I start by physically cleaning the film. To do this, I put the film on a film editing viewer. Then I put a few drops of TODO cleaning solution onto a lint-free cloth and spool the film onto another reel while grabbing the film with the soaked piece of cloth. It is advisable to swap the spot on the cloth every couple of meters and put on new cleaning solution as to avoid scratching the film with the dirt that came off. Once the film is completely wound over, I wind it back onto its original reel. Note that I only attach the end of the film to the original reel very loosely so it comes off the reel easily when scanning. For your average Super 8 reel this is easiest done by not putting the film into the "claw" that is supposed to hold it, but to gently place it in the slit that usually allows you the see how full the reel is. Then just wind and the film will stay in place.

I then thread the film onto the scanner and fast-forward to the first frame that is fully visible. I then use this frame to focus the camera onto the film grain. The *Zoom* view offered by the web interface is very useful for the final focus adjustment.

For the number of frames to scan, I usually estimate the number of frames on the reel based on its length and the pitch of the film type, and then add ca. 10% to be sure to capture the entire film in one go.

Rather than saving the scan on the Pi's SD card, I connect an external SSD via USB. It turns out this is significantly faster than using the SD card, so much so that with the SD card, the scan may be slowed down waiting for frames to save, which does not happen at all when using an external SSD. The path I select is `/media/pi/*pathtossd*/*rheelid*/frames`.




Scan to RAW, to SSD (because SSD faster than internal)

Convert raw bayer data to .dng files with script and RPiDNG

Adjust colour and crop, then export to tiff

From tiff files render into master video file (I use Apple Compressor to ProRes)

Import into Final cut, crop to 4:3 and use Neat Video to remove what I feel like might be digital noise but preserve film grain

Then use Neat and if required manual work to remove dust "that I find distracting".

Chose not to completely remove grain or stabilise to keep analog feel and not remove original handshake


### Cost

Put a table here of cost of everything


### Future features and fixes

Dashboard camera settings, mounting PCBs in case


## Run the software on your own scanner

Feel free to use this software on your own scanner

brief instructions

prerequisite is that electrical connections are the same

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
