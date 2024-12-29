class IPAddress:
    def __init__(self, ip):
        self.ip = self.validate_ip(ip)
        self.octets = list(map(int, self.ip.split('.')))
    
    def validate_ip(self, ip):
        parts = ip.split('.')
        if len(parts) != 4 or not all(part.isdigit() for part in parts):
            raise ValueError(f"{ip} is not a valid IPv4 address: must have 4 octets.")
        if not all(0 <= int(part) < 256 for part in parts):
            raise ValueError(f"{ip} is not a valid IPv4 address: octets must be between 0 and 255.")
        
        first_octet = int(parts[0])
        if 1 <= first_octet <= 223:  # Class A, B, C
            return ip
        else:
            raise ValueError(f"{ip} is not a valid Class A, B, or C IP address.")

    def __str__(self):
        return self.ip

    def get_class(self):
        first_octet = int(self.octets[0])
        if 1 <= first_octet <= 126:
            return 'A'
        elif 128 <= first_octet <= 191:
            return 'B'
        elif 192 <= first_octet <= 223:
            return 'C'
        else:
            return 'Unknown'

    def is_private(self):
        """Check if the IP address is private (Class A, B, or C)."""
        first_octet = self.octets[0]
        second_octet = self.octets[1]
        
        # Class A Private IP (10.0.0.0 - 10.255.255.255)
        if first_octet == 10:
            return True
        # Class B Private IP (172.16.0.0 - 172.31.255.255)
        elif first_octet == 172 and 16 <= second_octet <= 31:
            return True
        # Class C Private IP (192.168.0.0 - 192.168.255.255)
        elif first_octet == 192 and second_octet == 168:
            return True
        else:
            return False

class Subnet:
    def __init__(self, ip, mask):
        self.network_ip = IPAddress(ip)
        self.mask = self.validate_mask(mask)
        self.network_address = self.calculate_network_address()
        self.broadcast_address = self.calculate_broadcast_address()
        self.num_addresses = 2 ** (32 - self.mask)
        self.ip_class = self.network_ip.get_class()
        self.ip_private = self.network_ip.is_private()

    def validate_mask(self, mask):
        if isinstance(mask, int):
            if not (0 <= mask <= 32):
                raise ValueError("Subnet mask must be between 0 and 32.")
            return mask
        elif isinstance(mask, str) and mask.isdigit():
            mask = int(mask)
            if 0 <= mask <= 32:
                return mask
            else:
                raise ValueError("Subnet mask must be between 0 and 32.")
        else:
            raise ValueError("Mask must be an integer or a string containing a number.")

    def ip_to_bin(self, ip):
        octets = list(map(int, ip.split('.')))
        return (octets[0] << 24) + (octets[1] << 16) + (octets[2] << 8) + octets[3]

    def bin_to_ip(self, binary):
        return f"{(binary >> 24) & 0xFF}.{(binary >> 16) & 0xFF}.{(binary >> 8) & 0xFF}.{binary & 0xFF}"

    def calculate_network_address(self):
        mask_bin = (1 << 32) - (1 << (32 - self.mask))
        ip_bin = self.ip_to_bin(self.network_ip.ip)
        network_bin = ip_bin & mask_bin
        return self.bin_to_ip(network_bin)

    def calculate_broadcast_address(self):
        mask_bin = (1 << (32 - self.mask)) - 1
        ip_bin = self.ip_to_bin(self.network_ip.ip)
        broadcast_bin = ip_bin | mask_bin
        return self.bin_to_ip(broadcast_bin)

    def get_usable_ips(self):
        if self.mask >= 31:  # No usable IPs for /31 or /32
            return []
        if self.mask < 16:
            return [
                ("Too Much Bro"),
                ("To Show")
            ]
        start = self.ip_to_bin(self.network_address) + 1
        end = self.ip_to_bin(self.broadcast_address) - 1
        return [self.bin_to_ip(i) for i in range(start, end + 1)]

    def __str__(self):
        usable_ips = self.get_usable_ips()
        return (f"Network: {self.network_address}, "
                f"Broadcast: {self.broadcast_address}, "
                f"Usable IPs: {len(usable_ips)}")
