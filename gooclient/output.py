# This file is part of goo-client.
#
# Copyright (c) 2103-2014 by Nucleo de Computacao Cientifica, UNESP
#
# Authors:
#    Beraldo Leal <beraldo AT ncc DOT unesp DOT br>
#    Gabriel von. Winckler <winckler AT ncc DOT unesp DOT br>
#
# goo-client is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# goo-client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
import sys

class Output():
    def show(self, fields, objs):
        tot = 0
        for field in fields:
            title = field.keys()[0]
            size = field.values()[0]
            print str(title).ljust(size),
            tot = tot + size
        print ""
        print "-"*tot

        for obj in objs:
            for field in fields:
                title = field.keys()[0]
                size = field.values()[0]
                print str(obj[title]).ljust(size),
            print ""

        print "\n%d objects found" % len(objs)
