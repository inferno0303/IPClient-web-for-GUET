# coding: utf-8

import socket


class SendPackage:

    @staticmethod
    def send_udp(host, port, package):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(True)  # 设置为阻塞模式，启用set_timeout功能
        s.settimeout(2.5)

        # 使用socket发送数据包，等待接收数据包
        try:
            print('[SOCKET_INFO][--sending--]', package.hex())
            s.sendto(package, (host, port))
            recv_package, address = s.recvfrom(1024)
            print('[SOCKET_INFO][--received--]', recv_package.hex(), address)
            s.close()
            return str(recv_package.hex())
        except Exception as e:
            print(e)
            return None
