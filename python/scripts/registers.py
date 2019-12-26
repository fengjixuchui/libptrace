#!/usr/bin/env python
#
# Copyright (C) 2019, Cyxtera Cybersecurity, Inc.  All rights reserved.
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License version 2.1 as
# published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# version 2.1 for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# version 2.1 along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301,
# USA.
#
# THE CODE AND SCRIPTS POSTED ON THIS WEBSITE ARE PROVIDED ON AN "AS IS" BASIS
# AND YOUR USE OF SUCH CODE AND/OR SCRIPTS IS AT YOUR OWN RISK.  CYXTERA
# DISCLAIMS ALL EXPRESS AND IMPLIED WARRANTIES, EITHER IN FACT OR BY OPERATION
# OF LAW, STATUTORY OR OTHERWISE, INCLUDING, BUT NOT LIMITED TO, ALL
# WARRANTIES OF MERCHANTABILITY, TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# NON-INFRINGEMENT, ACCURACY, COMPLETENESS, COMPATABILITY OF SOFTWARE OR
# EQUIPMENT OR ANY RESULTS TO BE ACHIEVED THEREFROM.  CYXTERA DOES NOT WARRANT
# THAT SUCH CODE AND/OR SCRIPTS ARE OR WILL BE ERROR-FREE.  IN NO EVENT SHALL
# CYXTERA BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, RELIANCE,
# EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES, OR ANY LOSS OF GOODWILL, LOSS
# OF ANTICIPATED SAVINGS, COST OF PURCHASING REPLACEMENT SERVICES, LOSS OF
# PROFITS, REVENUE, DATA OR DATA USE, ARISING IN ANY WAY OUT OF THE USE AND/OR
# REDISTRIBUTION OF SUCH CODE AND/OR SCRIPTS, REGARDLESS OF THE LEGAL THEORY
# UNDER WHICH SUCH LIABILITY IS ASSERTED AND REGARDLESS OF WHETHER CYXTERA HAS
# BEEN ADVISED OF THE POSSIBILITY OF SUCH LIABILITY.
#
# registers.py
#
# Dedicated to Yuzuyu Arielle Huizer.
#
# Author: Ronald Huizer <ronald@immunityinc.com>
#
from __future__ import print_function
from six import iteritems
import sys
import signal
import _ptrace
import argparse

def attached_handler(process):
    for thread in process.threads:
        print("T{}".format(thread.id))
        for k, v in iteritems(thread.registers):
            print("{}: 0x{:x}".format(k, v))

def break_handler(signum, frame):
    _ptrace.quit();

def logger(cookie, string):
    print(string, end='')

parser = argparse.ArgumentParser(description='Dump registers of a process.')
parser.add_argument('file', nargs='?', metavar='filename', help='executable to dump.')
parser.add_argument('args', nargs='*', metavar='args', help='arguments.')
parser.add_argument('--debug', '-d', action='store_true')
parser.add_argument('--pid', '-p', type=int)
args = parser.parse_args(sys.argv[1:])

if (not args.file and not args.pid) or (args.file and args.pid):
    parser.print_help()
    sys.exit(1)

if hasattr(signal, "SIGBREAK"):
    signal.signal(signal.SIGBREAK, break_handler)

signal.signal(signal.SIGINT, break_handler)

if args.debug:
    _ptrace.log_hook_add(_ptrace.log_hook(logger))

handlers          = _ptrace.event_handlers()
handlers.attached = attached_handler

if args.pid:
    _ptrace.process_attach(args.pid, handlers, 0)

if args.file:
    _ptrace.execv(args.file, args.args, handlers, 0)

_ptrace.main()
