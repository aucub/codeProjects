#!/bin/bash

curl icanhazip.com
curl -s https://warp-clash-api-vvzf.onrender.com >/dev/null
# 安装WireGuard
sudo apt-get update
sudo apt-get install -y wireguard resolvconf

# 下载并配置订阅文件
SUBSCRIPTION_URL="https://warp-clash-api-vvzf.onrender.com/api/wireguard?best=false&randomName=true&proxyFormat=full&ipv6=false"
wget $SUBSCRIPTION_URL -O ~/wg0.conf

# 获取默认网关和公网IP地址
GATEWAY_IP=$(ip route list table main default | awk '{print $3}')
PUBLIC_IP=$(ip -brief address show eth0 | awk '{print $3}' | cut -d '/' -f 1)

# 将IP地址和网关添加到配置文件
sed -i "/\[Interface\]/a PostUp = ip rule add table 200 from $PUBLIC_IP\nPostUp = ip route add table 200 default via $GATEWAY_IP\nPreDown = ip rule delete table 200 from $PUBLIC_IP\nPreDown = ip route delete table 200 default via $GATEWAY_IP" ~/wg0.conf

# 将配置文件移动到/etc/wireguard/目录
sudo mv ~/wg0.conf /etc/wireguard/

# 设置WireGuard在启动时自动运行
echo "[Unit]
Description=WireGuard via wg-quick(8) for wg0
After=network-online.target nss-lookup.target
Wants=network-online.target nss-lookup.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/wg-quick up wg0
ExecStop=/usr/bin/wg-quick down wg0
ExecReload=/usr/bin/wg-quick down wg0
ExecReload=/usr/bin/wg-quick up wg0

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/wg-quick@wg0.service

# 启动WireGuard服务
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0

curl icanhazip.com
