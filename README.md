# gcde
GTK+ Console Desktop Environment, a desktop environment to give Linux a game-console look and feel.


## Goals

GCDE has a few different goals:

 - Make an easy-to-use, lightweight desktop environment
 - This DE must not only be lightweight and performant, but look aestheticly pleasing as well
 - Furthermore, this DE must _NATIVELY_ support game console controllers 
 - Finally, this DE must be usable on as many Linux, and ideally BSD, distros as possible
 
## Features

Currently working features:

 - Lightweight
 - Controller-optimized
 - Auto-scaling to the user's display resolution
   - this has been tested and is known working from 400x300, all the way up to 3840x1080
   - icons are the _ONLY_ thing not scaling right now, due to issues with GTK handling them
   - Testing this functionality in various resolutions above 1080p is needed.
   - Only _rectangular_ monitor geometries are supported due to limitations of the way GCDE is written
 
Still under development:

 - Built-in Controller support (this will be implemented as a Background Plugin, so it can be disabled if desired. (see Plugin Support below))
 - Aesthetically Pleasing (this won't get to a state that we like it in until GTK 4 comes out)
 - Plugin support (for info on how this is supposed to work, check out [this file](https://github.com/drauger-os-development/gcde/blob/master/usr/share/gcde/plugins/README.md))
 
## Building and Installing

Currently, GCDE is written entirely in Python. So, the only building necessary is to make the package for your distro! This is what the `BASH` scripting you see is used for.

### Debian, Ubuntu, Drauger OS, other Debian-based distros

 1. Clone this repository: </br></br> `git clone https://github.com/drauger-os-development/gcde` </br></br>
 
 2. `cd` into the GCDE directory: </br></br> `cd gcde` </br></br>
 
 3. Build it!: </br></br> `./build.sh` </br></br> This should take less than a second, and generate two (2) *.deb files in the parent directory. </br></br>
 
 4. From here, you can install the two *.deb files with your favorite package installer, or do it from the command line: </br></br> `cd ..; sudo apt install ./gcde-*.deb`
 
### Arch Linux, openSUSE, Fedora
 
 The necessary files to generate a *.rpm file for Arch Linux have not been made yet. Feel free to contribute to get this working!
 
 Ideally, the build for these distros would be equally as easy as it is for Debian-based distros
 
## Uninstalling

If you followed the instructions above for building and installing, then all you have to do is uninstall GCDE like you would any other application:

### Debian-based
`sudo apt uninstall gcde-desktop gcde-common`

### openSUSE
`sudo zypper remove gcde-desktop gcde-common`

### Fedora
`sudo dnf remove gcde-desktop gcde-common`

### Arch Linux
`sudo pacman -Rsc gcde-desktop gcde-common`

## Screenshots!!!!


Of course I gave y'all screenshots. I'm not gonna leave ya hanging like that. 

<img src="https://raw.githubusercontent.com/drauger-os-development/gcde/master/screenshots/screenshot_10-26-2020_22-37-33.png" style="width:540,height:360" alt="GCDE at 1080p">
</br>
</br>
<img src="https://raw.githubusercontent.com/drauger-os-development/gcde/master/screenshots/screenshot_10-26-2020_22-37-48.png" style="width:540,height:360" alt="GCDE Application Menu">
</br>
</br>
<img src="https://raw.githubusercontent.com/drauger-os-development/gcde/master/screenshots/screenshot_10-26-2020_22-38-04.png" style="width:540,height:360" alt="GCDE Settings Menu">
</br>
</br>
<img src="https://raw.githubusercontent.com/drauger-os-development/gcde/master/screenshots/screenshot_10-26-2020_22-39-06.png" style="width:540,height:360" alt="GCDE Idle Memory and CPU usage">