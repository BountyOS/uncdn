# uncdn

**uncdn** is a simple, CLI-based Python tool that filters out IP addresses belonging to known CDN (Content Delivery Network) and WAF (Web Application Firewall) providers. It supports both plain IP lists and mixed outputs (like MassDNS or DNS scan results), and can be extended with custom CIDR lists or public IP feed URLs.

---

## ✨ Features

- 🔍 Filters out IPs that belong to Cloudflare, Akamai, Fastly, GCore, and more
- 🧠 Understands both plain IPs and embedded IPs (e.g. from MassDNS output)
- 📥 Automatically downloads CIDR lists from known or custom sources
- 🧩 Supports custom CIDR files and endpoints
- 🗃️ Reads from all `*-cidrs.txt` files inside the `cidr-db/` folder
- ⚡ Fast filtering using native Python libraries

---

## 📦 Installation

```bash
git clone https://github.com/BountyOS/uncdn.git
cd uncdn
python3 uncdn.py -h
usage: uncdn.py [-h] [--update] [-ipl INPUT_IP_LIST] [-o OUTPUT]

Remove CDN IPs based on CIDR lists.

options:
  -h, --help            show this help message and exit
  --update              Download and update latest CIDRs
  -ipl INPUT_IP_LIST, --input-ip-list INPUT_IP_LIST
                        Input file (plain IPs or lines with embedded IPs)
  -o OUTPUT, --output OUTPUT
                        Output file with lines/IPs not in any CDN CIDR
```

Example Usage
```bash
➜  uncdn python3 uncdn.py -ipl ips.txt -o cleanips.txt    
[+] Loaded 3471 CIDR ranges from cidr-db
[+] 4460 lines written to cleanips.txt (removed 540 lines with CDN IPs)
```
