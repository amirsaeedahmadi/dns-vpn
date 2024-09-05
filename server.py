import socket
import select
import struct
import fcntl
import os
import sys

# Create a TUN interface
TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

def create_tun():
   # tun = open('/dev/net/tun', 'r+b')
   # ifr = struct.pack('16sH', b'ark%d', IFF_TUN | IFF_NO_PI)
   # fcntl.ioctl(tun, TUNSETIFF, ifr)
   # return tun
    tun = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack('16sH', b'tun%d', IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    return tun

def main():
    SERVER_IP = '192.168.1.2'
    SERVER_PORT = 9091
#    SUBNET = '172.16.0.0/24'
    SUBNET = '192.168.0.0/24'

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
       sock.bind((SERVER_IP, SERVER_PORT))

    except Exception as e:
       print(f"An error occurred: {e}", file=sys.stderr)
       raise

    # Create TUN interface
    tun = create_tun()

    # Set up IP forwarding and NAT (you might need to run this script with sudo)
    os.system('sysctl -w net.ipv4.ip_forward=1')
    os.system(f'iptables -t nat -A POSTROUTING -s {SUBNET} ! -d {SUBNET} -j MASQUERADE')

    print(f"Server running on {SERVER_IP}:{SERVER_PORT}")

    while True:
        readable, _, _ = select.select([sock, tun], [], [])

        for r in readable:
            if r is sock:
                # Receive data from the client
                data, addr = sock.recvfrom(2048)
                print(f"Received packet from {addr}")
                # Write to TUN interface
                tun.write(data)
            if r is tun:
                # Read from TUN interface
                packet = tun.read(2048)
                # Send to the client
                sock.sendto(packet, addr)

if __name__ == "__main__":
    main()
