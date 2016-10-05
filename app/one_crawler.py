# -*- coding: utf-8 -*-

import requests
from lxml import html
import socket
import ssl

class Model(object):
    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{0} = ({1})'.format(k, v) for k, v in self.__dict__.items())
        return '\n<{0}:\n  {1}\n>'.format(self.titulo, '\n  '.join(properties))


class One(Model):
    def __init__(self):
        super(One, self).__init__()
        self.image = ''
        self.leyenda = ''
        self.cita= ''
        self.pubdate = 0
        self.titulo = 0

    def json(self):
        d = {k: v for k, v in self.__dict__.items()}
        return d

def parsed_url(url):
    """
    解析 url 返回 (protocol host port path)
    有的时候有的函数, 它本身就美不起来, 你要做的就是老老实实写
    """
    # 检查协议
    protocol = 'http'
    if url[:7] == 'http://':
        u = url.split('://')[1]
    elif url[:8] == 'https://':
        protocol = 'https'
        u = url.split('://')[1]
    else:
        # '://' 定位 然后取第一个 / 的位置来切片
        u = url

    # 检查默认 path
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    # 检查端口
    port_dict = {
        'http': 80,
        'https': 443,
    }
    # 默认端口
    port = port_dict[protocol]
    if host.find(':') != -1:
        h = host.split(':')
        host = h[0]
        port = int(h[1])

    return protocol, host, port, path


def socket_by_protocol(protocol):
    """
    根据协议返回一个 socket 实例
    """
    if protocol == 'http':
        s = socket.socket()
    else:
        # HTTPS 协议需要使用 ssl.wrap_socket 包装一下原始的 socket
        # 除此之外无其他差别
        s = ssl.wrap_socket(socket.socket())
    return s

def response_by_socket(s):
    """
    参数是一个 socket 实例
    返回这个 socket 读取的所有数据
    """
    response = b''
    buffer_size = 1024
    while True:
        r = s.recv(buffer_size)
        if len(r) == 0:
            break
        response += r
    return response


def parsed_response(r):
    """
    把 response 解析出 状态码 headers body 返回
    状态码是 int
    headers 是 dict
    body 是 str
    """
    header, body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    status_code = h[0].split()[1]
    status_code = int(status_code)
    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v
    return status_code, headers, body

def get(url):
    """
    用 GET 请求 url 并返回响应
    """
    protocol, host, port, path = parsed_url(url)
    s = socket_by_protocol(protocol)
    s.connect((host, port))
    request = 'GET {} HTTP/1.1\r\nhost: {}\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36\r\nConnection: close\r\n\r\n'.format(path, host)
    encoding = 'utf-8'
    s.send(request.encode(encoding))
    response = response_by_socket(s)
    r = response.decode(encoding)
    status_code, headers, body = parsed_response(r)
    if status_code == 301:
        url = headers['Location']
        return get(url)
    return status_code, headers, body


def one_from_div(div):
    one = One()
    one.image = div.xpath('.//div[@class="one-imagen"]//@src')[0]
    one.leyenda = div.xpath('.//div[@class="one-imagen-leyenda"]')[0].text.strip()
    one.cita = div.xpath('.//div[@class="one-cita"]')[0].text.strip()
    one.pubdate = div.xpath('.//div[@class="one-pubdate"]//p')[0].text \
                    + ' ' + div.xpath('.//div[@class="one-pubdate"]//p')[1].text
    one.titulo = div.xpath('.//div[@class="one-titulo"]')[0].text.strip()
    return one


def ones_from_url(url):
    _, _, page = get(url)
    root = html.fromstring(page)
    div = root.xpath('//div[@class="tab-content"]')
    if div == []:
        ones = One()
    else:
        div = root.xpath('//div[@class="tab-content"]')[0]
        ones = one_from_div(div)
    return ones

def get_url(start,end):
    if start < 14:
        start = 14
    n = (n for n in range(start, end))
    url = ('http://wufazhuce.com/one/{}'.format(i) for i in n)
    return url

def get_ones():
    urls = get_url(240,1484)
    for url in urls:
        ones = ones_from_url(url)
        yield ones


from pymongo import MongoClient

def db_init():
    client = MongoClient()
    db = client.ones
    collection = db.one
    return collection

coll = db_init()



def run():
    ones = get_ones()
    for one in ones:
        one = one.json()
        coll.insert_one(one)
        print "现在是",one

if __name__ == '__main__':
    run()