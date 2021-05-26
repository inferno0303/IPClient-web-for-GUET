# 桂电宽带预拨号

## 项目介绍

桂电宽带预拨号 IPClient-web-for-GUET，解决了学生在宿舍无法用路由器的难题。

桂林电子科技大学「IPClient出校器」网页版，提供「代理预拨号服务」，让所有宿舍可方便使用路由器PPPOE拨号至运营商。

**因学校更换新的 Dr.com 认证系统，IPClient项目已停止维护。**🥰

*在桂电，折腾校园网是必经之路。😄* 

## 软件架构

1. 后端 Python Flask + 前端 JS Native；

2. 搭建UDP Reverse Tunnel：通过 Frp 反向代理，将校园网内 OpenWRT 路由器的20015映射到公网服务器（如：阿里云）的20015端口；

3. 配置双栈：同时连接运营商网络+校园网，运营商网络负责frp，校园网负责转发数据包；

4. 新增iptables记录：将路由器20015的udp数据包转发至桂电校园网172.16.1.1:20015，广西师大的ip是202.193.160.123。

   ```iptables -t nat -I PREROUTING -p udp --dport 20015 -j DNAT --to 172.16.1.1```

## 文件目录

config：配置文件，包含数据库配置、数据包转发主机配置；

model：数据库；

services：生成数据包、校验、发送到公网机器；

static：网页；

app.py：后端程序入口。



## 运行效果

<img src="https://cdn.jsdelivr.net/gh/yangxu770409504/assets@main/20210527/桂电预拨号主界面.3g259kk2g8g0.png" alt="主界面" style="zoom: 50%;" />

## 本软件解决了什么

一句话：解决了学生在宿舍无法用路由器的难题。

### 先了解PPPOE原理

PPP协议使用3种类型的LCP帧来完成每个PPP链路建立维护终止阶段的工作。在阅读这段内容之前，假设读者已有一定的计算机网络基础知识。

1. 链路建立帧（Configure-Request、Configure-Ack、Configure-Nak和Configure-Reject）用于建立和配置链路。
2. 链路维护帧（Code-Reject、Protocol-Reject、Echo-Request、Echo-Reply和Discard-Request）用于管理和调试链路。
3. 链路终止帧（Terminate-Request和Terminate-Ack）用于终止链路。

### 为什么需要预拨号

首先，PPP协议发现阶段，PPP-Client向以太网广播一个数据帧，该帧为PPP-LCP类型的以太网广播帧，包含Configure-Request内容请求，用于确定PPP-Server，但是因为桂电存在三家运营商，故如果同时向三家运营商以太网接口同时广播Configure-Request帧，将会收到来自三家运营商的Configure-Ack帧，这将产生冲突。

因此，在拨号之前，需要使用出校控制器向网络中心发出请求，确定某mac地址的设备，期望连接到的哪家运营商，然后学校网络中心会修改三层交换机的ACL（Access Control List），接通该mac地址设备与运营商的二层数据链路，故运营商将会收到该mac地址设备广播的Configure-Request帧，就可以完成PPPOE链路的建立。如果不发送请求报文，网络中心不会接通任何一家运营商的二层链路。此时拨号就会显示“服务器未响应”。 如果你输错了MAC地址，也会导致这样的情况。

简而言之，出校控制器软件的作用是：向【学校网络中心服务器】发送一个请求，告诉网络中心，【某台设备的期望与xx运营商】建立二层链路，然后网络中心会【修改交换机的ACL】，接通该设备与运营商的【二层链路】。

经实测，网络中心交换机有可能会删除该MAC地址的ACL记录，具体时间间隔约为2小时，因此每次设备PPPOE拨号前，可能要再次使用出校控制器发送请求，但也有不少ACL记录永久生效的案例，具体触发条件未知。

### 本站提供了什么

本网站提供的服务，就是模拟出校控制器向网络中心发送请求。因此需要收集设备的运营商信息，设备MAC地址，以及一个强壮的内网proxy。注意，东区与花江校区的网络中心出口交换机不同，拥有两份独立的ACL。

宿舍区每天05:59通电，06:06分通网，不同宿舍区可能有所不同，但大部分路由器在通电后就会尝试拨号，超过3次则不再尝试，建议重启路由器让路由器再次进入拨号状态。

关于心跳包，每栋楼通网时间不统一，如果你在通网之前通电了，则路由器会一直拨号失败，直到三次失败后不再尝试，故心跳包意义不大，且会加重proxy负担。手动心跳包是可行的，保存好MAC地址到备忘录，需要的时候复制粘贴就行了。

