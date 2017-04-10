'''
Created on Jan 9, 2017

github-traffic-api - use the experimental traffic API to pull traffic info from github

@author:     Jim Lawson

@copyright:  2017 UC Berkeley. All rights reserved.

@license:    license

@contact:    ucbjrl@berkeley.edu
'''

import os
import re
import signal
import sys
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from citJenkins.monitorRepos import BaseRepo
from traffic_clones import traffic_clones
from json2csv import json_to_table, store_csv

__all__ = []
__version__ = 0.1
__date__ = '2017-01-09'
__updated__ = '2017-01-090'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

doExit = False
continueOnError = False

homeDir = os.getcwd()

def sigterm(signum, frame):
    global doExit
    print 'ghta: signal %d' % (signum)
    if signum == signal.SIGTERM:
        doExit = True

def doWork(path, verbose, period, save_csv=None):
    modName = __name__ + '.doWork'
    
    repo = BaseRepo(path)
    if repo is None:
        exit(1)
    
    ghc = repo.connect()
    if ghc is None:
        exit(1)

    ghRepo = repo.remoterepo
    traffic_response = traffic_clones(ghRepo, period)
    repoName = repo.remotereponame
    print(json_to_table(repoName, period, traffic_response))
    if not save_csv is None:
        store_csv(save_csv, repoName, period, traffic_response)

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Jim Lawson on %s.
  Copyright 2017 UC Berkeley. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    global continueOnError
    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-s', '--save_csv', dest='save_csv', default=None, metavar="path", help="save results in specified file [default: %(default)s]")
        parser.add_argument('-p', '--period', dest='period', choices=['day', 'week'], default='week', help="period for traffic statistics [default: %(default)s]")
        parser.add_argument(dest="paths", help="paths to github repositories (local directory or URL)", metavar="paths", nargs='+')

        # Process arguments
        args = parser.parse_args()

        paths = args.paths
        verbose = args.verbose

        if verbose > 0:
            print("Verbose mode on")

        # Install the signal handler to catch SIGTERM
        signal.signal(signal.SIGTERM, sigterm)
        for path in paths:
            doWork(path, verbose, args.period, args.save_csv)
        return 0
 
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'github-traffic-api.profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    main()
