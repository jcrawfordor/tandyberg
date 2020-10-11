import serial
import logging

log = logging.getLogger('controller')

class Controller(object):
    def __init__(self, interface):
        # Incidentally, all of the default pyserial options are correct for
        # the cameras. For reference, this is 9600 baud, 8N1, no flow control.
        self.s = serial.Serial(interface, timeout=5)
        # Might want to be able to change this in the future to support
        # multiple cameras. 0x81 means "from 0 to 1" due to some weird
        # fixed bits in the VISCA spec. Assumption is that controller (us)
        # is 0 and camera is 1, which is the case at camera bootup until it's
        # told otherwise.
        self.address = b'\x81'
        # Speeds
        self.panSpeed = b'\x01'
        self.tiltSpeed = b'\x01'
    
    def steer(self, direction):
        """Steer in a direction"""
        # The only reason "stop" isn't one of the options here is because the
        # manual isn't clear on whether or not the speed values for "stop" are
        # required to be pinned to 03 or not.
        # Could also have this function take a "horizontal" and "vertical"
        # argument, which matches the protocol better, but I find this more
        # ergonomic to use.
        lookup = {
            'up': b'\x03\x01',
            'down': b'\x03\x02',
            'left': b'\x01\x03',
            'right': b'\x02\x03',
            'upleft': b'\x01\x01',
            'upright': b'\x02\x01',
            'downleft': b'\x01\x02',
            'downright': b'\x02\x02'
        }

        cmd = b'\x01\x06\x01'
        cmd += self.panSpeed
        cmd += self.tiltSpeed
        cmd += lookup[direction]
        self.expectOK(cmd)
    
    def getSteerFunc(self, direction):
        """Encloses the steer function for easier use with Qt"""
        def do():
            self.steer(direction)
        return do
    
    def stopSteer(self):
        """Stops camera movement"""
        # This is the same as the steer commands except the manual says to use
        # 03 03 as the speed bytes. is this required???
        cmd = b'\x01\x06\x01'
        cmd += b'\x03\x03\x03\x03'
        self.expectOK(cmd)
    
    def center(self):
        """Centers camera, which also homes drive motors"""
        cmd = b'\x01\x06\x05'
        self.expectOK(cmd)

    def zoom(self, direction):
        """Zooms in or out"""
        lookup = {
            'in': b'\x2a',
            'out': b'\x3a'
        }

        cmd = b'\x01\x04\x07'
        cmd += lookup[direction]
        self.expectOK(cmd)
    
    def getZoomFunc(self, direction):
        """Encloses the zoom function for easier use with Qt"""
        def do():
            self.zoom(direction)
        return do
    
    def stopZoom(self):
        """Stops zooming."""
        # This is a separate method for consistency with stopSteer
        cmd = b'\x01\x04\x07\x00'
        self.expectOK(cmd)

    def getPos(self):
        """Returns a tuple of pan, tilt, zoom position for the camera. useful
        for saving presets."""
        zoomResp = self.getResponse(b'\x09\x04\x47')
        zoom = Controller.__fromVisca2b(zoomResp[1:4])
        panTiltResp = self.getResponse('\x09\x06\x12')
        pan = Controller.__fromVisca2b(panTiltResp[1:4])
        tilt = Controller.__fromVisca2b(panTiltResp[5:8])
        return (pan, tilt, zoom)
    
    def goToPos(self, pan, tilt, zoom):
        """Send camera directly to a P,T,Z position, useful for recalling
        presets."""
        # We need to use two different commands to set PT and zoom. Should
        # be okay to send these at once due to double-buffering, as long as
        # the user doesn't go wild with mashing buttons.
        cmd = b'\x01\x06\x02'
        cmd += self.panSpeed
        cmd += self.tiltSpeed
        cmd += Controller.__toVisca2b(pan)
        cmd += Controller.__toVisca2b(tilt)
        self.expectOK(cmd)
        cmd = b'\x01\x04\x47'
        cmd += Controller.__toVisca2b(zoom)
        self.expectOK(cmd)

    def getResponse(self, command):
        """Sends a command (in hex) to the camera and returns the result as bytes"""
        cmd = self.address
        cmd += command
        cmd += b'\xff'
        log.debug(f"Sending {cmd.hex()}")
        self.s.write(cmd)
        resp = b''
        b = None
        while b != b'\xff':
            b = self.s.read()
            resp += b
        # Strip off first byte (address) and last (terminator)
        # We leave the reponse as bytes instead of hex because we may need to
        # do binary arithmetic on it later, might as well not just have to
        # convert back to bytes.
        log.debug(f"Received {resp.hex()}")
        return resp[1:-1]

    def expectOK(self, command):
        """Sends a command to the camera and expects a "success" response"""
        resp = self.getResponse(command)
        # The manual is confusing on this point but the second nibble seems to
        # indicate whether the command is queued in the first or second buffer
        # (most camera models double-buffer commands). Either way is fine to
        # us.
        if resp != b'\x50' and resp != b'\x51':
            raise Exception(f'Received non-OK status response {resp.hex()}')

    @staticmethod
    def __toVisca2b(value):
        """Converts an integer to the weird VISCA 2-byte number representation, in hex for convenience."""
        # The VISCA format in question looks like 0i:0j:0k:0l where ijkl are
        # nibbles of the two-byte number.
        b = value.to_bytes(2, 'big')
        first_nibble = b[0] >> 4
        second_nibble = b[0] & 0x0f
        third_nibble = b[1] >> 4
        fourth_nibble = b[1] & 0x0f
        return bytes((first_nibble, second_nibble, third_nibble, fourth_nibble))

    @staticmethod
    def __fromVisca2b(value):
        """Converts the weird VISCA 2-byte number to an integer."""
        first_byte = (value[0] << 4) | value[1]
        second_byte = (value[2] << 4) | value[3]
        return (first_byte << 8) + second_byte