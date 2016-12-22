##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2014 Jens Steinhauser <jens.steinhauser@gmail.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
##

import sigrokdecode as srd
from .regs import *

class ChannelError(Exception):
    pass

class Decoder(srd.Decoder):
    api_version = 2
    id = 'cyrf6936'
    name = 'CYRF6936'
    longname = 'Cypress CYRF6936 WirelessUSB(TM) LP 2.4 GHz Radio SoC'
    desc = '2.4GHz transceiver chip.'
    license = 'gplv2+'
    inputs = ['spi']
    outputs = ['cyrf6936']
    annotations = (
        # Sent from the host to the chip.
        ('cmd', 'Commands sent to the device'),
        ('tx-data', 'Payload sent to the device'),

        # Returned by the chip.
        ('register', 'Registers read from the device'),
        ('rx-data', 'Payload read from the device'),

        ('warning', 'Warnings'),
    )
    ann_cmd = 0
    ann_tx = 1
    ann_reg = 2
    ann_rx = 3
    ann_warn = 4
    annotation_rows = (
        ('writes', 'Writes', (ann_cmd, ann_tx)),
        ('reads', 'Reads', (ann_reg, ann_rx)),
        ('warnings', 'Warnings', (ann_warn,)),
    )

    def __init__(self):
        self.next()
        self.requirements_met = True
        self.cs_was_released = False

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def warn(self, pos, msg):
        '''Put a warning message 'msg' at 'pos'.'''
        self.put(pos[0], pos[1], self.out_ann, [self.ann_warn, [msg]])

    def putp(self, pos, ann, msg):
        '''Put an annotation message 'msg' at 'pos'.'''
        self.put(pos[0], pos[1], self.out_ann, [ann, [msg]])

    def next(self):
        '''Resets the decoder after a complete command was decoded.'''
        # 'True' for the first byte after CS went low.
        self.first = True

        # The current command, and the minimum and maximum number
        # of data bytes to follow.
        self.cmd = None
        self.dir = 1 # Command direction: 1 = write, 0 = read
        self.inc = 0 # Command increment: 1 = auto address increment, 0 = same address
        self.min = 0
        self.max = 0

        # Used to collect the bytes after the command byte
        # (and the start/end sample number).
        self.mb = []
        self.mb_s = -1
        self.mb_e = -1

    def mosi_bytes(self):
        '''Returns the collected MOSI bytes of a multi byte command.'''
        return [b[0] for b in self.mb]

    def miso_bytes(self):
        '''Returns the collected MISO bytes of a multi byte command.'''
        return [b[1] for b in self.mb]

    def decode_command(self, pos, b):
        '''Decodes the command byte 'b' at position 'pos' and prepares
        the decoding of the following data bytes.'''
        c = self.parse_command(b)
        if c is None:
            self.warn(pos, 'unknown command')
            return

        self.cmd, self.dat, self.min, self.max = c

        if self.cmd in ('W_REGISTER'):
            # Don't output anything now, the command is merged with
            # the data bytes following it.
            self.mb_s = pos[0]
        else:
            self.putp(pos, self.ann_cmd, self.format_command())

    def format_command(self):
        '''Returns the label for the current command.'''
        if self.cmd == 'R_REGISTER':
            reg = regs[self.dat][0] if self.dat in regs else 'unknown register'
            return 'R_REGISTER "{}"'.format(reg)
        else:
            return 'Cmd {}'.format(self.cmd)

    def parse_command(self, b):
        '''Parses the command byte.

        Returns a tuple consisting of:
        - the name of the command / register
        - additional data needed to dissect the following bytes
        - minimum number of following bytes
        - maximum number of following bytes
        '''

        cmd_addr = (b & 0b111111)
        cmd_dir = (b & (1<<7))>>7  # 1 = write, 0 = read
        cmd_inc = (b & (1<<6))>>6  # 1 = auto address increment, 0 = keep address

        if cmd_addr in regs:
            c = 'R_REGISTER' if (cmd_dir == 0) else 'W_REGISTER'
            m = regs[cmd_addr][1]
            return (c, cmd_addr, 1, m)
        else:
            return None # addr unknown


    def decode_register(self, pos, ann, regid, data):
        '''Decodes a register.

        pos   -- start and end sample numbers of the register
        ann   -- is the annotation number that is used to output the register.
        regid -- may be either an integer used as a key for the 'regs'
                 dictionary, or a string directly containing a register name.'
        data  -- is the register content.
        '''

        if type(regid) == int:
            # Get the name of the register.
            if regid not in regs:
                self.warn(pos, 'unknown register')
                return
            name = regs[regid][0]
        else:
            name = regid

        # Multi byte register come LSByte first.
        # data = reversed(data)

        textdata = self.convert_mb_data(data, True)

        if self.cmd == 'W_REGISTER' and ann == self.ann_cmd:
            # The 'W_REGISTER' command is merged with the following byte(s).
            text = 'wr({}, "{}")'.format(name, textdata)
        else:
            text = 'rd({}) == "{}"'.format(name, textdata)

        self.putp(pos, ann, text)

    def convert_mb_data(self, data, always_hex):
        '''Converts the data bytes 'data' of a multibyte command to text.
        If 'always_hex' is True, all bytes are decoded as hex codes, otherwise only non
        printable characters are escaped.'''

        if always_hex:
            def escape(b):
                return '{:02X}'.format(b)
        else:
            def escape(b):
                c = chr(b)
                if not str.isprintable(c):
                    return '\\x{:02X}'.format(b)
                return c

        return ''.join([escape(b) for b in data])

    def finish_command(self, pos):
        '''Decodes the remaining data bytes at position 'pos'.'''

        if self.cmd == 'R_REGISTER':
            self.decode_register(pos, self.ann_reg,
                                 self.dat, self.miso_bytes())
        elif self.cmd == 'W_REGISTER':
            self.decode_register(pos, self.ann_cmd,
                                 self.dat, self.mosi_bytes())

    def decode(self, ss, es, data):
        if not self.requirements_met:
            return

        ptype, data1, data2 = data

        if ptype == 'CS-CHANGE':
            if data1 is None:
                if data2 is None:
                    self.requirements_met = False
                    raise ChannelError('CS# pin required.')
                elif data2 == 1:
                    self.cs_was_released = True

            if data1 == 0 and data2 == 1:
                # Rising edge, the complete command is transmitted, process
                # the bytes that were send after the command byte.
                if self.cmd:
                    # Check if we got the minimum number of data bytes
                    # after the command byte.
                    if len(self.mb) < self.min:
                        self.warn((ss, ss), 'missing data bytes')
                    elif self.mb:
                        self.finish_command((self.mb_s, self.mb_e))

                self.next()
                self.cs_was_released = True
        elif ptype == 'DATA' and self.cs_was_released:
            mosi, miso = data1, data2
            pos = (ss, es)

            if miso is None or mosi is None:
                self.requirements_met = False
                raise ChannelError('Both MISO and MOSI pins required.')

            if self.first:
                self.first = False
                # First MOSI byte is always the command.
                self.decode_command(pos, mosi)
                # First MISO byte is discarded
                if (miso != 0xff):
                    self.warn((ss, ss), 'unrequested data')
            else:
                if not self.cmd or len(self.mb) >= self.max:
                    self.warn(pos, 'excess byte')
                else:
                    # Collect the bytes after the command byte.
                    if self.mb_s == -1:
                        self.mb_s = ss
                    self.mb_e = es
                    self.mb.append((mosi, miso))
