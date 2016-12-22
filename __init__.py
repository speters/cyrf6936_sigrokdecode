##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2016 Soenke J. Peters
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

'''
This decoder stacks on top of the 'spi' PD and decodes the protocol spoken
by the Cypress CYRF6936 2.4GHz transceiver chips.

Details:
http://www.cypress.com/file/136666/download#page=105
http://www.cypress.com/file/126466/download#page=15
'''

from .pd import Decoder
