'''
Created on Aug 3, 2015

@author: jrl
'''
import fileinput
import re

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

nbName = re.compile(r"""\s*(?P<name>\S.*\S)\s*$""")

def tableify(lines):
    contribs = {}
    for line in lines:
        fields = line.split("|")
        nbMatch = nbName.match(fields[1])
        if not nbMatch:
            raise CLIError("Bad line \"%s\"" % (line))
        name = nbMatch.group('name')
        (first, sep, last) = name.rpartition(' ')
        key = last.lower() + '_' + first.lower()
        nbMatch = nbName.match(fields[2])
        if not nbMatch:
            raise CLIError("Bad line \"%s\"" % (line))
        desc = nbMatch.group('name')
        contribs[key] = { 'name': name, 'desc': desc }
    for key in sorted(contribs.iterkeys()):
        name = contribs[key]['name']
        desc = contribs[key]['desc']
        if False:
            print '| %s | %s |' % (name, desc)
        else:
            print '  <tr>\n    <td>%s</td>\n    <td>%s</td>\n  </tr>' % (name, desc)

if __name__ == '__main__':
    tableify(fileinput.input())