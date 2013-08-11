import os, sys, time, subprocess, signal, yaml, getpass, threading
import wasanbon
from wasanbon.core import rtc
from wasanbon.core import system
from wasanbon.core.system import run
from wasanbon.core import project, nameserver

ev = threading.Event()

endflag = False

def signal_action(num, frame):
    print ' - SIGINT captured'
    ev.set()
    global endflag
    endflag = True
    pass

class Command(object):
    def __init__(self):
        pass

    def execute_with_argv(self, argv, clean, verbose, force):

        proj = project.Project(os.getcwd())

        if(argv[2] == 'install'):
            wasanbon.arg_check(argv, 4)
            sys.stdout.write(' @ Installing RTC.\n')
            if 'all' in argv[3:]:
                proj.install(proj.rtcs, verbose=verbose)

            for name in argv[3:]:
                try:
                    proj.install(proj.rtc(name), verbose=verbose)
                except Exception, ex:
                    print ex
                    sys.stdout.write(' - Installing RTC %s failed.\n' % name)


        elif(argv[2] == 'uninstall'):
            wasanbon.arg_check(argv, 4)
            sys.stdout.write(' @ Uninstalling RTC.\n')
            if 'all' in argv[3:]:
                proj.uninstall(proj.rtcs)

            for name in argv[3:]:
                try:
                    proj.uninstall(proj.rtc(name))
                except:
                    sys.stdout.write(' - Unnstalling RTC %s failed.\n' % name)


        elif(argv[2] == 'list'):
            sys.stdout.write(' @ Listing installed RTCs.\n')
            rtcs_map = proj.installed_rtcs()
            for lang, rtcs in rtcs_map.items():
                sys.stdout.write(' @ %s:\n' % lang)
                for rtc_ in rtcs:
                    sys.stdout.write('    @ %s\n' % rtc_.name) 

        elif(argv[2] == 'build'):
            print ' @ Building RTC System in Wasanbon'
            nss = [[fullpath.split(':')[0].strip(), fullpath.split(':')[1].strip()] for fullpath in proj.get_nameservers(verbose=verbose)]
            if verbose:
                sys.stdout.write(' @ Listing Nameservers:\n')
                for ns in nss:
                    sys.stdout.write('    - %s (port=%s)\n' % (ns[0], ns[1]))

            ns_process = None
            for ns in nss:
                if ns[0] == 'localhost' or ns[0] == '127.0.0.1':
                    if force or not nameserver.is_nameserver_running(ns[0] + ':' + ns[1], verbose=verbose):
                        sys.stdout.write(' - Starting Nameserver %s:%s. Please Wait 5 seconds.\n' % (ns[0], ns[1]))
                        ns_process = nameserver.launch_nameserver(verbose=verbose, force=force, port=ns[1])
                        time.sleep(5)

                if not nameserver.is_nameserver_running(ns[0] + ':' + ns[1], verbose=verbose):
                    sys.stdout.write(' - Nameserver %s:%s is not running\n' % (ns[0], ns[1]))
                    return
                else:
                    if verbose:
                        sys.stdout.write(' - Nameserver %s:%s is running.\n' % (ns[0], ns[1]))

            proj.launch_all_rtcd(verbose=verbose)

            for i in range(0, 5):
                sys.stdout.write('\r - Waiting (%s/%s)\n' % (i+1, 5))
                sys.stdout.flush()
                time.sleep(1)
            system.list_available_connections()
            system.list_available_configurations()
            system.save_all_system(['localhost'])

            proj.terminate_all_rtcd(verbose=verbose)
            if ns_process:
                ns_process.kill()

            return

        elif(argv[2] == 'run'):
            signal.signal(signal.SIGINT, signal_action)
            sys.stdout.write(' @ Starting RTC-daemons...\n')

            nss = [[fullpath.split(':')[0].strip(), fullpath.split(':')[1].strip()] for fullpath in proj.get_nameservers(verbose=verbose)]
            if verbose:
                sys.stdout.write(' @ Listing Nameservers:\n')
                for ns in nss:
                    sys.stdout.write('    - %s (port=%s)\n' % (ns[0], ns[1]))

            ns_process = None
            for ns in nss:
                if ns[0] == 'localhost' or ns[0] == '127.0.0.1':
                    if force or not nameserver.is_nameserver_running(ns[0] + ':' + ns[1], verbose=verbose):
                        sys.stdout.write(' - Starting Nameserver %s:%s. Please Wait 5 seconds.\n' % (ns[0], ns[1]))
                        ns_process = nameserver.launch_nameserver(verbose=verbose, force=force, port=ns[1])
                        time.sleep(5)

                if not nameserver.is_nameserver_running(ns[0] + ':' + ns[1], verbose=verbose):
                    sys.stdout.write(' - Nameserver %s:%s is not running\n' % (ns[0], ns[1]))
                    return
                else:
                    if verbose:
                        sys.stdout.write(' - Nameserver %s:%s is running.\n' % (ns[0], ns[1]))

            proj.launch_all_rtcd(verbose=verbose)
            proj.connect_and_configure(verbose=verbose)
            proj.activate(verbose=verbose)

            if sys.platform == 'win32':
                global endflag
                while not endflag:
                    time.sleep(0.1)
            else:
                signal.pause()

            proj.terminate_all_rtcd(verbose=verbose)

            if ns_process:
                ns_process.kill()
                #ns_process.send_signal(signal.CTRL_C_EVENT)
            pass

        elif(argv[2] == 'datalist'):
            system.list_rtcs_by_dataport()
                 
            pass

        elif(argv[2] == 'nameserver'):
            
            y = yaml.load(open('setting.yaml', 'r'))
            
            rtcconf_cpp = rtc.rtcconf.RTCConf(y['application']['conf.C++'])
            rtcconf_py = rtc.rtcconf.RTCConf(y['application']['conf.Python'])
            rtcconf_java = rtc.rtcconf.RTCConf(y['application']['conf.Java'])
            
            if len(argv) == 3:
                sys.stdout.write(' - Listing Nameservers\n')
                sys.stdout.write('rtcd(C++)    : "%s"\n' % rtcconf_cpp['corba.nameservers'])
                sys.stdout.write('rtcd(Python) : "%s"\n' % rtcconf_py['corba.nameservers'])
                sys.stdout.write('rtcd(Java)   : "%s"\n' % rtcconf_java['corba.nameservers'])
            elif len(argv) == 4:
                sys.stdout.write(' - Adding Nameservers\n')
                rtcconf_cpp['corba.nameservers'] = argv[3]
                rtcconf_py['corba.nameservers'] = argv[3]
                rtcconf_java['corba.nameservers'] = argv[3]
                rtcconf_cpp.sync()
                rtcconf_py.sync()
                rtcconf_java.sync()
                
            pass
            
