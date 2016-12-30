##
## Copyright (C) 2016 Soenke J. Peters
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.

# http://www.cypress.com/file/136666/download#page=105
# http://www.cypress.com/file/126466/download#page=15
regs = {
#   addr: ('name',               size, access,     default )
    0x00: ('CHANNEL_ADR',           1, '-bbbbbbb', '-1001000'),
    0x01: ('TX_LENGTH_ADR',         1, 'bbbbbbbb', '00000000'),
    0x02: ('TX_CTRL_ADR',           1, 'bbbbbbbb', '00000011'),
    0x03: ('TX_CFG_ADR',            1, '--bbbbbb', '--000101'),
    0x04: ('TX_IRQ_STATUS_ADR',     1, 'rrrrrrrr', '--------'),
    0x05: ('RX_CTRL_ADR',           1, 'bbbbbbbb', '00000111'),
    0x06: ('RX_CFG_ADR',            1, 'bbbbb-bb', '10010-10'),
    0x07: ('RX_IRQ_STATUS_ADR',     1, 'brrrrrrr', '--------'),
    0x08: ('RX_STATUS_ADR',         1, 'rrrrrrrr', '--------'),
    0x09: ('RX_COUNT_ADR',          1, 'rrrrrrrr', '00000000'),
    0x0A: ('RX_LENGTH_ADR',         1, 'rrrrrrrr', '00000000'),
    0x0B: ('PWR_CTRL_ADR',          1, 'bbb-bbbb', '10100000'),
    0x0C: ('XTAL_CTRL_ADR',         1, 'bbb--bbb', '000--100'),
    0x0D: ('IO_CFG_ADR',            1, 'bbbbbbbb', '00000000'),
    0x0E: ('GPIO_CTRL_ADR',         1, 'bbbbrrrr', '0000----'),
    0x0F: ('XACT_CFG_ADR',          1, 'b-bbbbbb', '1-000000'),
    0x10: ('FRAMING_CFG_ADR',       1, 'bbbbbbbb', '10100101'),
    0x11: ('DATA32_THOLD_ADR',      1, '----bbbb', '----0100'),
    0x12: ('DATA64_THOLD_ADR',      1, '---bbbbb', '---01010'),
    0x13: ('RSSI_ADR',              1, 'r-rrrrrr', '0-100000'),
    0x14: ('EOP_CTRL_ADR',          1, 'bbbbbbbb', '10100100'),
    0x15: ('CRC_SEED_LSB_ADR',      1, 'bbbbbbbb', '00000000'),
    0x16: ('CRC_SEED_MSB_ADR',      1, 'bbbbbbbb', '00000000'),
    0x17: ('TX_CRC_LSB_ADR',        1, 'rrrrrrrr', '--------'),
    0x18: ('TX_CRC_MSB_ADR',        1, 'rrrrrrrr', '--------'),
    0x19: ('RX_CRC_LSB_ADR',        1, 'rrrrrrrr', '11111111'),
    0x1A: ('RX_CRC_MSB_ADR',        1, 'rrrrrrrr', '11111111'),
    0x1B: ('TX_OFFSET_LSB_ADR',     1, 'bbbbbbbb', '00000000'),
    0x1C: ('TX_OFFSET_MSB_ADR',     1, '----bbbb', '----0000'),
    0x1D: ('MODE_OVERRIDE_ADR',     1, 'wwwww--w', '00000--0'),
    0x1E: ('RX_OVERRIDE_ADR',       1, 'bbbbbbb-', '0000000-'),
    0x1F: ('TX_OVERRIDE_ADR',       1, 'bbbbbbbb', '00000000'),
    0x26: ('XTAL_CFG_ADR',          1, 'wwwwwwww', '00000000'),
    0x27: ('CLK_OFFSET_ADR',        1, 'wwwwwwww', '00000000'),
    0x28: ('CLK_EN_ADR',            1, 'wwwwwwww', '00000000'),
    0x29: ('RX_ABORT_ADR',          1, 'wwwwwwww', '00000000'),
    0x32: ('AUTO_CAL_TIME_ADR',     1, 'wwwwwwww', '00000011'),
    0x35: ('AUTO_CAL_OFFSET_ADR',   1, 'wwwwwwww', '00000000'),
    0x39: ('ANALOG_CTRL_ADR',       1, 'wwwwwwww', '00000000'),
    0x20: ('TX_BUFFER_ADR',        16, 'WWWWWWWWWWWWWWWW', '----------------'),
    0x21: ('RX_BUFFER_ADR',        16, 'RRRRRRRRRRRRRRRR', '----------------'),
    0x22: ('SOP_CODE_ADR',          8, 'BBBBBBBB', 0x17FF9E213690C782),
    0x23: ('DATA_CODE_ADR',        16, 'BBBBBBBBBBBBBBBB', 0x02F9939702FA5CE3012BF1DB0132BE6F),
    0x24: ('PREAMBLE_ADR',          3, 'BBB', 0x333302),
    0x25: ('MFG_ID_ADR',            6, 'RRRRRR', '------')
}


class RegDecode():
    regs = {}
    regnames = {}
    decoderfuncs = {}

    def __init__(self, regs = {}):
        RegDecode.defs(regs)

    def defs(regs):
        RegDecode.regs = regs
        regnames = {}
        for reg, name in RegDecode.regs.items():
            regnames[name] = reg
        RegDecode.regnames = regnames

    def name(r):
        if r in RegDecode.regs:
            return RegDecode.regs[r][0]
        elif r in RegDecode.regnames:
            return r
        else:
            raise AttributeError('No such register "{}"'.format(r))

    def addr(r):
        try:
            r = int(r, 0)
        except TypeError:
            pass
        if r in RegDecode.regs:
            return r
        elif r in RegDecode.regnames:
            return RegDecode.regnames[r]
        else:
            raise AttributeError('No such register "{}"'.format(r))

    def add_decoderfunc(r, f):
        r = RegDecode.addr(r)
        if r is not None:
            RegDecode.decoderfuncs[r] = f

    def decode(r, val):
        try:
            val = int(val, 0)
        except TypeError:
            pass
        r = RegDecode.addr(r)
        if (r is not None):
            if (r in RegDecode.decoderfuncs):
                return RegDecode.decoderfuncs[r](val)
            else:
                return val
        else:
            return val

RegDecode(regs)

class RDecode(RegDecode):
    def __init__(self, f):
        regname = f.__name__.replace('reg_', '')
        self.f = f
        RegDecode.add_decoderfunc(regname, f)

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

@RDecode
def reg_0x00(v = 0x48):
    CHANNEL_MSK = 0x7F
    CHANNEL_MAX = 0x62
    CHANNEL_MIN = 0x00
    v = v & CHANNEL_MSK
    if (v >= CHANNEL_MIN) and (v <= CHANNEL_MAX):
        return "CHANNEL {} ({}GHz)".format(v, (200+(v * 98/CHANNEL_MAX))/100)
    else:
        return "{} (Warn: Check sane values)".format(v)

if __name__ == "__main__":
    print(RegDecode.decode('0x00', 0x48))
    print(reg_0x11(0xff))
    print()
