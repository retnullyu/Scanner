import os
import re
import sys
import threading
import time

from lib.bcolors import Bcolors
from lib.cli_output import console, printf
from lib.iscdn import iscdn
import argparse
from lib.url import parse_ip
from lib.verify import verify_https
from lib.vuln import Vuln
from lib.web_info import web_info
from plugins.dir import Scanner
from plugins.port_scan import ScanPort
from vul_scanner.vul import vul_scanner

os.chdir(sys.path[0])
def start(target):

    host = parse_ip(target)
    url = verify_https(target)
    if url:
        isopen = True
    else:
        isopen = False
    if isopen:
        data, apps, title = web_info(url)
    else:
        data = ''
        apps = {}
    if iscdn(host):
        open_port = ScanPort(url).pool()
    else:
        open_port = ['CDN:0']
def logo():
    asciii_art = """
            /   _____/ ____ _____    ____   ____   ___________ 
             \_____  \_/ ___\\__  \  /    \ /    \_/ __ \_  __ \     Author: LuoYu
             /        \  \___ / __ \|   |  \   |  \  ___/|  | \/    Blog:www.retnull.top
            /_______  /\___  >____  /___|  /___|  /\___  >__|       Version:Scanner_v1
                    \/     \/     \/     \/     \/     \/           Description:网络空间安全评估系统设计实践项目
                    """
    asciii_art = Bcolors.OKBLUE+asciii_art+Bcolors.ENDC
    print(asciii_art)
    parser = argparse.ArgumentParser()
    parser.description = '具备端口扫描、目录扫描、web信息收集，同时还具备一定主机和web漏扫的扫描器demo'
    parser.add_argument('-u', '--url', dest='url', help='要扫描的url', type=str)
    parser.add_argument('-f', '--scan_file_url', dest='scan_file_url', help='载入要扫描的url列表txt文件(每个域名换行-文件保存至domain目录)',
                        type=str)
    parser.add_argument('-d', '--dict', dest='dict', help='提供扫描的字典位置(多个文件请使用`,`分割)', type=str, default='专业备份扫描.txt')
    parser.add_argument('-o', '--output', dest='output', help='结果输出位置', type=str)
    parser.add_argument('-t', '--thread', dest='thread', help='运行程序的线程数量', type=int, default=50)
    parser.add_argument('--timeout', dest='timeout', help='超时时间', type=int, default=2)
    parser.add_argument('--http_status_code', dest='http_status_code', help='代表扫描成功的http状态码', type=str,
                        default='200,403')
    parser.add_argument('--type', dest='type', help='漏洞检测类型service or web', type=str)
    parser.add_argument('--target', dest='target', help='模糊匹配漏洞检测类型，如ssh、redis', type=str, default='all')

    args = parser.parse_args()
    return args

def dirscanThread(thread):
    for i in range(args.thread):
        t = threading.Thread(target=scan.run)
        t.setDaemon(True)
        t.start()
    while True:
        if threading.activeCount() <= 1:
            console('目录扫描',args.url,'线程结束扫描终止')
            break
        else:
            try:
                time.sleep(0.5)
            except KeyboardInterrupt:
                scan.TASK_STOP = True
                print(scan.TASK_STOP)
                print('用户中止，等待所有从线程退出，当前(%i)' % threading.activeCount())

if __name__ == "__main__":

    args = logo()
    if (args.type == 'web' or args.type == 'service'):  # 进行漏洞扫描
        console('漏洞扫描中',str(args.url),'扫描类型'+'['+args.type+']')
        vul_scanner(args.type, args.target)
    elif args.url: # 进行信息收集探测
        start(args.url)  #端口、os 探测
        scan = Scanner(args.url, args.scan_file_url, args.dict, args.output, args.timeout, args.http_status_code) #目录扫描
        dirscanThread(args.thread)



