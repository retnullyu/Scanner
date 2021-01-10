import sys
import time

import pyfiglet

from lib.bcolors import Bcolors



def banner():
    ascii_banner = pyfiglet.figlet_format("Scanner")
    print(Bcolors.RED + ascii_banner + Bcolors.ENDC)


def start_out(hosts):
    sys.stdout.write(Bcolors.OKBLUE + "[*] https://github.com/retnull/Scanner\n" + Bcolors.ENDC)
    sys.stdout.write(Bcolors.OKBLUE + "[*] Scanning POC: " + Bcolors.ENDC)

    sys.stdout.write(Bcolors.OKBLUE + "[*] Threads: " + Bcolors.ENDC)

    sys.stdout.write(Bcolors.OKBLUE + "[*] Target quantity: " + Bcolors.ENDC)
    if type(hosts) == list:
        sys.stdout.write(Bcolors.OKBLUE + str(len(hosts)) + "\n" + Bcolors.ENDC)
    else:
        sys.stdout.write(Bcolors.OKBLUE + '1' + "\n" + Bcolors.ENDC)
    sys.stdout.write(Bcolors.OKBLUE + "[*] Scanning Dir: " + Bcolors.ENDC)

    sys.stdout.write(Bcolors.OKBLUE + "[*] Ping: " + Bcolors.ENDC)

    sys.stdout.write(Bcolors.OKBLUE + "[*] CHECK_DB: " + Bcolors.ENDC)

    sys.stdout.write(Bcolors.OKBLUE + "[*] Socks5 Proxy: " + Bcolors.ENDC)



def console(plugins, domain, text):
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    timestamp = Bcolors.OKBLUE + '[' + timestamp + ']' + Bcolors.ENDC
    plugins = Bcolors.RED + plugins + Bcolors.ENDC
    text = Bcolors.OKGREEN + text + Bcolors.ENDC
    sys.stdout.write(timestamp + ' - ' + plugins + ' - ' + domain + '    ' + text)
def printf(plugins,url,message):
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    timestamp = Bcolors.OKBLUE + '[' + timestamp + ']' + Bcolors.ENDC
    url = Bcolors.RED + url + Bcolors.ENDC
    message = Bcolors.OKGREEN + message + Bcolors.ENDC
    plugins = Bcolors.RED + plugins + Bcolors.ENDC
    sys.stdout.write(timestamp + ' - ' + plugins + ' - ' + url + '    ' + message)