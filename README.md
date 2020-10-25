# Tandyberg

This is a simple GUI program to control a Cisco/Tandberg Precision HD camera.
While originally very expensive, I was able to get one of these for peanuts
at a government surplus auction and it makes a pretty swell (if very
oversized) webcam if you go through the hassle of getting it to work with
normal equipment. Coronavirus, however, has made a commercial-grade
teleconferencing setup rather tempting for the home. Pick up an old Precision
HD camera and dig a boundary microphone and audio interface out of your shed
and you've basically got a Zoom Room but both jankier and somehow more
reliable.

To be clear, I'm talking about the Precision HD cameras with remote
PTZ/exposure control that are intended for use with a Cisco/Tandberg IP/ISDN
video conferencing codec, not the newer USB cameras that confusingly have the
same name. If you're in the market, watch for a Tandberg Edge or MXP series
system, which usually includes one or more of these cameras.

The Tandberg Precision HD cameras speak a control protocol that "resembles"
the quasi-standard Sony VISCA, according to the manual. However, I have not
been able to get any off-the-shelf VISCA software to work with mine - most
off-the-shelf packages seem to query the camera for its identity and explode
if it doesn't respond with a known Sony model number. Also, most
off-the-shelf VISCA software is extremely bad, even compared to this minimal
effort.

This should work with any Tandberg or Cisco-branded Precision HD camera with
serial control, but I only have the oldest 720p version to test with.
Confusingly, the "Precision HD 1080p-720p Camera User Guide," which is in
general a technical writing trainwreck, says that the section on VISCA
control does not apply to the 720p, but then says that some of the listed
commands only apply to the 720p. Experimentally, it all seems to work fine
with the 720p, and the manual promises that the same control protocol will
work with the newer 1080p models as well.

# Development Wishlist

* [X] Move camera left/right/up/down
* [X] Zoom camera in/out
* [ ] Get configuration from file instead of hardcoded
* [ ] Set movement speed
* [ ] Autofocus on/off and manual focus control
* [ ] Autoexposure on/off and manual exposure controls (iris, backlight mode, gain, gamma, white balance)
* [ ] Set and recall preset positions
* [ ] Reconfigure/reconnect through GUI
* [ ] Enable/disable IR command push and local IR commands
* [ ] Turn prompt light on/off, maybe with some IPC method or something to do this from external programs
* [ ] Detect camera capabilities and enable/disable buttons (e.g. 720p model refuses to pan diagonal)
* [ ] Global keyboard shortcuts
* [ ] Simple network API for remote control, at least preset recall
* [ ] OBS plugin???

# Interfacing with a Precision HD Camera

I only have a 720p, but it's also the strangest model of these cameras. The
newer ones are a lot more standards-compliant.

## Video

You will need to use the HDMI output, unless you have a desire to reverse
engineer the proprietary LVDS video protocol the 720p camera is intended to
use with an Edge series codec. Fortunately the 720p camera seems to enable
its HDMI output unless some LVDS handshake with the codec succeeds, so this
isn't an issue - don't be scared off by the 720p manual talking about a
proprietary video cable, there is an HDMI output on the back of it and it
works fine. The other models just only use HDMI to begin with. I'm using a
very cheap HDMI capture card off of AliExpress but any HDMI frame grabber
should work.

## Control

The newer models just have a bog-standard DE9 serial port. The 720p, however,
has a "proprietary single video/control/power connector." Careful reading of
the manual will reveal that the included RJ45 to DE9 connector includes the
serial RXD/TXD/GND pins in the normal place, so it works fine with a normal USB
serial controller. If you don't have the original cable, the manual gives the
pinout for the RJ45 connector so you can make your own - unfortunately it
doesn't seem to match the common DE9-RJ45 cables for the console port on Cisco
network equipment.

One hangup you're likely to hit is that the included cable has a male DE9
connector when female would be more normal. But what's more, I was pretty
confused about the manual's description of whether the camera was DCE or
DTE from an RS-232 perspective. I tried a null modem cable because that's
what I had lying around with the right genders and... it worked. So I'll
assert that if you have the original cable, what you need to use it is a
female null modem connection. Not sure about the newer models.

Remember that we're then only using that connection for control, so you'll
need to use separate HDMI and 12v power supply. The camera returns 12V power
on the DE9 connector so if you were crafty you could probably power an SBC
off the camera for dedicated control.

# Limitations

Right now this software is pretty lame. It only supports a single camera (the
protocol allows daisy-chaining up to 7) and requires the port be configured
in a text file. It should work on either Windows or Linux fine though, just
use the correct way of describing a serial port on your platform in the config
file - COM5 or /dev/ttyUSB0 for example. There's also a bunch of commands
related to system management that aren't supported.

Also it looks like garbage because I have no idea what I'm doing with GUIs.