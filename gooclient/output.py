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

        if len(objs) == 0:
            print "No objects found"

        for obj in objs:
            for field in fields:
                title = field.keys()[0]
                size = field.values()[0]
                print str(obj[title]).ljust(size),
            print ""
