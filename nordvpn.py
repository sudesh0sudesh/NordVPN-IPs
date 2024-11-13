#!/usr/bin/python3
import dns.resolver
import re
import csv
from urllib.request import urlopen, Request

class NordVPNServerList:
    def __init__(self):
        self.url = "https://nordvpn.com/ovpn/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.servers = set()
        
        # Configure resolver to use Cloudflare DNS
        self.resolver = dns.resolver.Resolver(configure=False)
        self.resolver.nameservers = ['1.1.1.1', '1.0.0.1']
        self.resolver.port = 53

    def extract_hostnames(self):
        try:
            request = Request(self.url, headers=self.headers)
            print("Accessing NordVPN configurations page...")
            
            with urlopen(request) as response:
                html_content = response.read().decode('utf-8')
            
            # Single comprehensive pattern for all valid subdomain formats
            pattern = r'([a-z0-9][-a-z0-9]*?)\.nordvpn\.com'
            
            hostnames = set(re.findall(pattern, html_content, re.IGNORECASE))
            
            if not hostnames:
                print("No server hostnames found.")
                return False
            
            print(f"Found {len(hostnames)} unique server hostnames")
            return hostnames
            
        except Exception as e:
            print(f"Error accessing webpage: {str(e)}")
            return False

    def resolve_hostnames(self, hostnames):
        """Perform DNS lookups using Cloudflare DNS"""
        print("\nResolving server IPs using Cloudflare DNS (1.1.1.1)...")
        for hostname in sorted(hostnames):
            try:
                # Query A records for the hostname
                answers = self.resolver.resolve(f"{hostname}.nordvpn.com", 'A')
                for rdata in answers:
                    ip = rdata.to_text()
                    self.servers.add((f"{hostname}.nordvpn.com", ip))
            except dns.resolver.NXDOMAIN:
                print(f"Could not resolve {hostname}.nordvpn.com (NXDOMAIN)")
            except dns.resolver.NoAnswer:
                print(f"No A records found for {hostname}.nordvpn.com")
            except Exception as e:
                print(f"Error resolving {hostname}.nordvpn.com: {str(e)}")

    def save_servers(self, filename="nordvpn_servers.txt"):
        """Save server list to a file"""
        try:
            with open(filename, 'w') as f:
                for hostname, ip in sorted(self.servers):
                    f.write(f" {ip}\n")
            print(f"\nServer list saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving server list: {str(e)}")
            return False

def main():
    nord = NordVPNServerList()
    hostnames = nord.extract_hostnames()
    
    if hostnames:
        nord.resolve_hostnames(hostnames)
        nord.save_servers()

if __name__ == "__main__":
    main()