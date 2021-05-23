# coding: utf-8

import socket
import struct


class MakePackage:

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

    def do(self, ip, mac, isp):
        try:
            # 处理ip
            byte_array = bytes()
            for i in ip.split('.'):
                byte_array += int(i).to_bytes(1, 'little')
            ip = byte_array
            print('[process_ip]', ip.hex())

            # 处理mac
            byte_array = bytes()
            mac = mac.replace('-', ':').upper().strip()
            for i in mac:  # 取每一个字符，转换为bytes
                byte_array += i.encode()
            mac = byte_array
            print('[process_mac]', mac.hex())

            # 处理isp
            isp = int(isp).to_bytes(1, 'little')
            print('[process_isp]', isp.hex())

            # 生成数据包
            package = self._make_packet(ip, mac, isp)
            return package
        except Exception as e:
            print(e)
            return None
