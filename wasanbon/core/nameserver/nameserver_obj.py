import os, sys, subprocess, time, signal
from wasanbon.core.nameserver.rtc_ref import *
from ctypes import *
import rtctree
import omniORB

SIGSET_NWORDS = 1024 / (8 * sizeof(c_ulong))

class SIGSET(Structure):
    _fields_ = [
        ('val', c_ulong * SIGSET_NWORDS)
    ]

sigs = (c_ulong * SIGSET_NWORDS)()
sigs[0] = 2 ** (signal.SIGINT - 1)
mask = SIGSET(sigs)

if sys.platform == 'darwin':
    libc = CDLL('libc.dylib')
elif sys.platform == 'linux2':
    libc = CDLL('libc.so.6')

def handle(sig, _):
    if sig == signal.SIGINT:
        pass

def disable_sig():
    '''Mask the SIGINT in the child process'''
    SIG_BLOCK = 0
    libc.sigprocmask(SIG_BLOCK, pointer(mask), 0)




class NameService(object):

    def __init__(self, path):
        if path.find(':') < 0:
            path = path.strip() + ':2809'
        if path.strip().startswith('/'):
            path = path.strip()[1:]
        self._path = path
        self._process = None
        self._rtcs = None

    @property
    def path(self):
        return self._path

    @property
    def address(self):
        return self._path.split(':')[0].strip()

    @property
    def port(self):
        return self._path.split(':')[1].strip()

    def check_and_launch(self,verbose=False, force=False):
        if self.address != 'localhost' or self.address != '127.0.0.1':
            if not self.is_running(verbose=verbose) or force:
                self.launch(verbose=verbose, force=force)
                for i in range(0, 5):
                    if verbose:
                        sys.stdout.write(' - Starting Nameserver %s. Please Wait %s seconds.\n' % (self.path, 4-i))
                    time.sleep(1)
        return self.is_running(verbose=verbose)

    def is_running(self, verbose=False, try_count=3):
        for i in range(0, try_count):
            try:
                if verbose:
                    sys.stdout.write(' - Checking Nameservice(%s) is running\n' % self.path)
                path, port = rtctree.path.parse_path('/' + self.path)
                tree = rtctree.tree.RTCTree(paths=path, filter=[path])
                dir_node = tree.get_node(path)
                if verbose:
                    sys.stdout.write(' - Nameservice(%s) is found.\n' % self.path)
                return True
            except rtctree.exceptions.InvalidServiceError, e:
                continue
            except omniORB.CORBA.OBJECT_NOT_EXIST, e:
                continue
        if verbose:
            sys.stdout.write(' - Nameservice not found.\n')
        return False
            

    def launch(self, verbose=False, force=False):
        if self.address != 'localhost' and self.address != '127.0.0.1':
            return False

        if verbose:
            sys.stdout.write(' - Starting Nameserver \n')
            pass
    
        pstdout = None if verbose else subprocess.PIPE 
        pstderr = None if verbose else subprocess.PIPE
        pstdin = subprocess.PIPE
        if sys.platform == 'win32':
            path = os.path.join(os.environ['RTM_ROOT'], 'bin', 'rtm-naming.bat')
            cmd = [path, self.port]
            creationflag = 512
            preexec_fn = None
            pass
        else:
            cmd = ['rtm-naming', self.port]
            creationflag = 0
            preexec_fn = disable_sig
            pass
        if verbose:
            print ' - Command = %s' % cmd
            pass
        self._process = subprocess.Popen(cmd, creationflags=creationflag, stdout=pstdout, stdin=pstdin, stderr=pstderr, preexec_fn=preexec_fn)
        if force:
            self._process.stdin.write('y\n')
            pass
        return
    
    def kill(self):
        if self._process:
            self._process.kill()

    @property
    def rtcs(self):
        path, port = rtctree.path.parse_path('/' + self.path)
        self.tree = rtctree.tree.RTCTree(paths=path, filter=[path])
        dir_node = self.tree.get_node(path)

        rtcs = []
        def func(node, rtcs):
            rtcs.append(node)
            
        def filter_func(node):
            if node.is_component and not node.parent.is_manager:
                return True
            return False

        dir_node.iterate(func, rtcs, [filter_func])
        return rtcs
    
    @property
    def port_types(self):
        pass

    @property
    def ports(self, type="any", direction=['in', 'out']):
        path, port = rtctree.path.parse_path('/' + self.path)
        self.tree = rtctree.tree.RTCTree(paths=path, filter=[path])
        dir_node = self.tree.get_node(path)

        ports = []
        def func(node, ports, type=type, direction=direction):
            ports__ = []
            if 'DataInPort' in direction:
                ports__ = ports__ + node.inports
            if 'DataOutPort' in direction:
                ports__ = ports__ + node.outports
            if 'CorbaPort' in direction:
                ports__ = ports__ + node.svcports
            if type == 'any':
                ports = ports + ports__

            for port in ports__:
                
                self._inports.append(
            
        def filter_func(node):
            if node.is_component and not node.parent.is_manager:
                return True
            return False

        self.private_rtcs = []
        dir_node.iterate(func, self, [filter_func])
        return self.private_rtcs
        