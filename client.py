import socket
import select
import struct
import fcntl
import os

# Create a TUN interface
TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

def create_tun():
#    tun = open('/dev/net/tun', 'r+b')
#    ifr = struct.pack('16sH', b'ark%d', IFF_TUN | IFF_NO_PI)
#    fcntl.ioctl(tun, TUNSETIFF, ifr)
#    return tun

    tun = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack('16sH', b'tun%d', IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    return tun


def main():
    SERVER_IP = '192.168.1.2'
    SERVER_PORT = 9091
    LOCAL_IP = '192.168.1.3'
    LOCAL_PORT = 7070

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCAL_IP, LOCAL_PORT))

    # Create TUN interface
    tun = create_tun()

    # Set up routing (you might need to run this script with sudo)
    #os.system(f'ip route add {SERVER_IP} via $(ip route | grep default | cut -d " " -f 3)')
    os.system(f'ip route add {SERVER_IP} via 192.168.1.1')
    os.system('ip route add default dev ark0')

    print(f"Client connected to {SERVER_IP}:{SERVER_PORT}")

    while True:
        readable, _, _ = select.select([sock, tun], [], [])

        for r in readable:
            if r is tun:
                # Read from TUN interface
                packet = tun.read(2048)
                # Send to the server
                sock.sendto(packet, (SERVER_IP, SERVER_PORT))
            if r is sock:
                # Receive data from the server
                data, _ = sock.recvfrom(2048)
                # Write to TUN interface
                tun.write(data)

if __name__ == "__main__":
    main()
