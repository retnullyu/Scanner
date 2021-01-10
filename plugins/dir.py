#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'LuoYu'

import requests
import threading
import os
import re
import argparse
import time
import queue
from plugins.ShowStatusBar import ShowStatusBar
from vul_scanner.vul import vul_scanner


class Scanner():
    def __init__(self, url, scan_file_url, scan_dict, output, timeout, http_status_code):
        print('web目录扫描器运行.')
        print(' ')

        # 队列任务当前进行进度
        self.queue_progress = 0
        # 队列任务总数
        self.queue_total_size = 0
        # 任务是否停止状态
        self.TASK_STOP = False

        self.timeout = timeout
        self.http_status_code = http_status_code
        self._loadUrl(url, scan_file_url)
        self._outputAddress(output)
        self._loadDict(scan_dict)
        self._loadHeaders()
        self._analysis404()
        

    # url加载
    def _loadUrl(self, url, scan_file_url):
        print('url加载.')
        if not url is None:
            scan_site = [self._urlVerify(url), ]
        elif not scan_file_url is None:
            scan_site = self._urlListVerify(scan_file_url)
        else:
            print('对不起,扫描域名不能为空')
            exit()
        self.scan_site = self.formattingHost(scan_site)
        print('url加载地址: %s' % self.scan_site)
        print('url加载完成.')
        print(' ')

    # url验证
    # :param url:  需要验证的url
    def _urlVerify(self, url):
        if url.find('://') == -1:
            url = '%s%s' % ('http://', url)
        else:
            http_protocol = {'http', 'https'}
            url_list = url.split('://')
            if url_list[0] not in http_protocol:
                url = '%s%s' % ('http://', url_list[1])
        return url

    # url批量验证
    def _urlListVerify(self, scan_file_url):
            # 批量扫描地址
            scan_file_url = './domain/' + scan_file_url

            # 允许访问的后缀
            license_type = {'txt'}
            if scan_file_url.split('.')[-1] not in license_type:
                print('对不起,批量扫描只允许加载后缀为%s类型的文件' % license_type)
                exit()

            try:
                url_list = []
                f = open(scan_file_url, encoding = 'gbk')
                for line in f:
                    if line.startswith('#') == False:
                        url_list.append(self._urlVerify(line.strip()))
                f.close()

                if url_list == []:
                    print('批量扫描文件: %s 为空,无法执行' % scan_file_url)
                    exit()

                return url_list
            except IOError:
                print('批量扫描文件: %s 无法访问' % scan_file_url)
                exit()

    # 扫描结果地址确定
    def _outputAddress(self, output):
        dirname = './results/'
        
        if os.path.exists(dirname) == False:
            os.makedirs(dirname)

        if not output is None:
            if re.search('^[\u4E00-\u9FA5a-zA-Z0-9_]*$', output) is None:
                print('对不起,扫描结果导出命名规则只允许[中英文+数字+_]')
                exit()

            file_url = dirname + output + '.html'
            f = open(file_url, 'w')
            f.close()
            
            file_output = file_url
        else:
            file_output = {}
            for site in self.scan_site:
                file_url = dirname + site.rstrip('/').replace('https://', '').replace('http://', '').replace('/', '-').replace(':', '-') + '.html'
                file_output[site] = file_url
                f = open(file_url, 'w')
            f.close()
        self.file_output = file_output
        print('扫描结果输出位置: %s' % self.file_output)
        print(' ')

    # 字典加载
    def _loadDict(self, scan_dict):
        print('字典加载中.')

        if scan_dict == '':
            print('字典不能为空')
            exit()

        # 创建队列
        self.q = queue.Queue()

        license_type = {'txt'}
        for dict_path in scan_dict.split(','):
            if dict_path.split('.')[-1] not in license_type:
                print('对不起\'%s\'字典不允许加载,只允许加载后缀为%s类型的文件' % (dict_path, license_type))
                exit()

            # 字典地址
            dict_path = './dict/' + dict_path
            try:
                # 打开字典文件
                f = open(dict_path, encoding = 'gbk')
                f.close()
            except IOError:
                print('字典: %s 无法访问,请修改' % dict_path)
                exit()

        for dict_path in scan_dict.split(','):
            # 字典地址
            dict_path = './dict/' + dict_path
            # 打开字典文件
            for host in self.scan_site:
                f = open(dict_path, encoding = 'gbk')
                for line in f:
                    if line.startswith('#') == False:
                        # 字典入队
                        data = {}

                        scan_dict = line.strip()
                        scan_dict = list(scan_dict)
                        if len(scan_dict) <= 0:
                            continue
                        if scan_dict[0] != '/':
                            scan_dict.insert(0,'/')
                        scan_dict = ''.join(scan_dict)

                        data['host'] = host
                        data['dict'] = scan_dict
                        self.q.put(data)
                # print('字典加载位置: %s' % dict_path)
                # print('字典加载完成.')
            f.close()
        print('字典加载完成.')
        print(' ')
        self.queue_total_size = self.q.qsize()

    # 添加headers头
    def _loadHeaders(self):
        self.headers = {
            'Accept': '*/*',
            'Referer': 'http://www.baidu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; rv:16.0) Gecko/20100101 Firefox/16.0',
            'Cache-Control': 'no-cache',
        }

    # 获取目标站点404状态
    def _analysis404(self):
        print('目标404页面获取.')
        page404 = {}
        for host in self.scan_site:
            try:
                url_result = requests.get(host + '/china/hello404.html', headers = self.headers, allow_redirects = False, timeout = self.timeout)
                page404[host] = url_result.text
            except requests.exceptions.ConnectionError:
                page404[host] = 'connection_error'
                print('%s域名 404页面连接错误' % host)
            except requests.exceptions.ReadTimeout:
                page404[host] = 'read_timeout_error'
                print('%s域名 404页面连接超时错误' % host)
            except:
                page404[host] = '404_error'
                print('%s域名 404页面获取时未知错误' % host)
        self.page404 = page404
        print('目标404页面完成.')
        print(' ')

    # 扫描
    def _scan(self, data):
        html_result = ''
        try:
            html_result = requests.get(data['host'] + data['dict'], headers = self.headers, allow_redirects = False, timeout = self.timeout)
            if html_result != '':
                if self.http_status_code.find(str(html_result.status_code)) != -1 and html_result.text != self.page404[data['host']]:
                    print('[%i]%s' % (html_result.status_code, html_result.url))
                    
                    result = {}
                    result['status_code'] = html_result.status_code
                    result['url'] = html_result.url
                    
                    if data['host'] not in self.file_output:
                        address = self.file_output
                    else:
                        address = self.file_output[data['host']]

                    self._writeOutput(address, result)

        except requests.exceptions.ConnectionError:
            # print('请求超时: %s' % data['host'] + data['dict'])
            pass
        except requests.exceptions.ReadTimeout:
            pass

        # 进度条
        self.queue_progress+=1
        ShowStatusBar().run(self.queue_progress, self.queue_total_size)

    # 主机头格式化
    def formattingHost(self, scan_site):
        host_list = []
        for host in scan_site:
            host = list(host)
            if host[-1] == '/':
                host.pop()
            host = ''.join(host)
            host_list.append(host)
        return host_list

    # 数据写入
    def _writeOutput(self, address, data):
        f = open(address, 'a+')
        f.write('<a href="' + data['url'] + '" target="_blank">' + '[' + str(data['status_code']) + '] ' + data['url'] + '</a>')
        f.write('\r\n</br>')
        f.close()

    def run(self):
        while not self.q.empty() and self.TASK_STOP == False:
            self._scan(self.q.get())

if __name__ == '__main__':
    logo1 = """
    /   _____/ ____ _____    ____   ____   ___________ 
     \_____  \_/ ___\\__  \  /    \ /    \_/ __ \_  __ \    Author: LuoYu
     /        \  \___ / __ \|   |  \   |  \  ___/|  | \/    Blog:www.retnull.top
    /_______  /\___  >____  /___|  /___|  /\___  >__|       Version:Scanner_v1
            \/     \/     \/     \/     \/     \/           Description:网络空间安全评估系统设计实践项目
            """
    print(logo1)
    parser = argparse.ArgumentParser()
    parser.description = '兼顾网站后台目录扫描和js敏感信息提取，具备一定主机和web漏扫的扫描器demo'
    parser.add_argument('-u', '--url', dest = 'url', help = '要扫描的url', type = str)
    parser.add_argument('-f', '--scan_file_url', dest = 'scan_file_url', help = '载入要扫描的url列表txt文件(每个域名换行-文件保存至domain目录)', type = str)
    parser.add_argument('-d', '--dict', dest = 'dict', help = '提供扫描的字典位置(多个文件请使用`,`分割)', type = str, default = '专业备份扫描.txt')
    parser.add_argument('-o', '--output', dest = 'output', help = '结果输出位置', type = str)
    parser.add_argument('-t', '--thread', dest = 'thread', help = '运行程序的线程数量', type = int, default = 50)
    parser.add_argument('--timeout', dest = 'timeout', help = '超时时间', type = int, default = 2)
    parser.add_argument('--http_status_code', dest = 'http_status_code', help = '代表扫描成功的http状态码', type = str, default = '200,403')
    parser.add_argument('--type',dest = 'type',help= '漏洞检测类型service or web',type= str)
    parser.add_argument('--target',dest= 'target' , help= '模糊匹配漏洞检测类型，如ssh、redis',type = str, default = 'all')

    args = parser.parse_args()
    if (args.type == 'web' or args.type =='service'):
        print("正在调用鲲鹏进行漏洞扫描")
        vul_scanner(args.type,args.target)
    else:
        scan = Scanner(args.url, args.scan_file_url, args.dict, args.output, args.timeout, args.http_status_code)
        for i in range(args.thread):
            t = threading.Thread(target=scan.run)
            t.setDaemon(True)
            t.start()
        while True:
            if threading.activeCount() <= 1:
                print('扫描完成!!!')
                break
            else:
                try:
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    scan.TASK_STOP = True
                    print(scan.TASK_STOP)
                    print('用户中止，等待所有从线程退出，当前(%i)' % threading.activeCount())

