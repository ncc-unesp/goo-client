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
