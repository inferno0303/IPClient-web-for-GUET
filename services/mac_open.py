# coding: utf-8

import socket
import time
import struct


class MacOpener:

    def __init__(self):
        # 发往阿里云
        self.DEFAULT_SERVER = '120.78.63.182'
        print('欢迎使用去你大爷的出校器')

    @staticmethod
    def _checksum(data):
        cs = 0x4e67c6a7
        for b in data:
            cs &= 0xffffffff
            if cs < 0x80000000:
                cs ^= ((cs >> 2) + (cs << 5) + b) & 0xffffffff
            else:
                cs ^= (((cs >> 2) | 0xC0000000) + (cs << 5) + b) & 0xffffffff
                # print(bin(cs))
        return cs & 0x7fffffff

    def _make_packet(self, ip, mac, isp):
        packet = struct.pack('!1s 29x 4s 17s 3x 1s 1x', '1'.encode(), ip, mac, isp)
        print('[packet]', packet.hex())
        cs = self._checksum(packet)
        print('[checksum]', cs)
        return struct.pack('<56s I', packet, cs)

    def run(self, ip, mac, isp, campus):
        # 处理ip
        tmp = bytes()
        for i in ip.split('.'):
            tmp += int(i).to_bytes(1, 'little')
        ip = tmp
        print('[process_ip]', ip.hex())

        # 处理mac
        mac = mac.replace('-', ':').upper().strip()
        tmp = bytes()
        for i in mac:
            tmp += i.encode()
        mac = tmp
        print('[process_mac]', mac.hex())

        # 处理isp
        isp = int(isp).to_bytes(1, 'little')
        print('[process_isp]', isp.hex())

        # 生成数据包
        data = self._make_packet(ip, mac, isp)

        # 实例化socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(True)  # 设置为阻塞模式，启用settimeout功能
        s.settimeout(2.5)

        # 使用socket发送数据包
        try:
            print('[SOCKET_INFO][--sending--]', data.hex())
            if campus == '1':  # 花江
                s.sendto(data, (self.DEFAULT_SERVER, 20015))
            elif campus == '2':  # 东区
                s.sendto(data, (self.DEFAULT_SERVER, 20014))
            result, address = s.recvfrom(1024)
            print('[SOCKET_INFO][--received--]', result.hex())
        except Exception as e:
            print(e)
            result = 'False'.encode()

        # 关闭socket，判断服务器回应的str是否正确，返回True或False
        s.close()
        if str(result.hex()) == '0a153f9100':
            return True
        else:
            return False
