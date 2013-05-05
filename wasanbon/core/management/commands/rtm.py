#!/usr/bin/env python

import wasanbon
from wasanbon.core.rtm import *

class Command(object):
    def __init__(self):
        pass

    def execute_with_argv(self, argv):
        if(argv[2] == 'install'):
            print 'Installing OpenRTM-aist'
            install_rtm.install_rtm()
        elif(argv[2] == 'status'):
            print 'OpenRTM-aist Status'
            ret = status.get_status()
            print ' - OpenRTM-aist C++    : %s' % ret['c++']
            print ' - OpenRTM-aist Python : %s' % ret['python']
            print ' - OpenRTM-aist Java   : %s' % ret['java']
                
