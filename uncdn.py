#!/usr/bin/env python3

import os
import re
import sys
import json
import argparse
import ipaddress
import requests

CIDR_REGEX = r'\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b'
IP_REGEX = r'(?:\d{1,3}\.){3}\d{1,3}'
CIDR_DB_DIR = 'cidr-db'
CIDR_URL_FILE = os.path.join(CIDR_DB_DIR, 'cidr-urls.txt')
LATEST_CIDR_FILE = os.path.join(CIDR_DB_DIR, 'latest-cidrs.txt')


def download_and_extract_cidrs():
    os.makedirs(CIDR_DB_DIR, exist_ok=True)
    cidrs = set()

    if not os.path.exists(CIDR_URL_FILE):
        print(f'[-] URL list file not found: {CIDR_URL_FILE}')
        sys.exit(1)

    with open(CIDR_URL_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            matches = re.findall(CIDR_REGEX, resp.text)
            cidrs.update(matches)
            print(f'[+] {len(matches)} CIDRs extracted from {url}')
        except Exception as e:
            print(f'[-] Failed to download {url}: {e}')

    with open(LATEST_CIDR_FILE, 'w') as out:
        out.write('\n'.join(sorted(cidrs)))

    print(f'[+] Saved {len(cidrs)} unique CIDRs to {LATEST_CIDR_FILE}')


def load_all_cidrs():
    cidr_set = set()
    for fname in os.listdir(CIDR_DB_DIR):
        if 'cidrs' in fname.lower():
            path = os.path.join(CIDR_DB_DIR, fname)
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if re.fullmatch(CIDR_REGEX, line):
                        try:
                            cidr_set.add(ipaddress.ip_network(line, strict=False))
                        except ValueError:
                            continue
    print(f'[+] Loaded {len(cidr_set)} CIDR ranges from {CIDR_DB_DIR}')
    return cidr_set


def ip_in_cidrs(ip_str, cidrs):
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in cidr for cidr in cidrs)
    except ValueError:
        return False


def filter_ips_in_lines(input_file, output_file, cidr_ranges):
    with open(input_file) as f:
        lines = [line.rstrip() for line in f if line.strip()]

    output_lines = []
    removed = 0

    for line in lines:
        ips = re.findall(IP_REGEX, line)
        if any(ip_in_cidrs(ip, cidr_ranges) for ip in ips):
            removed += 1
            continue
        output_lines.append(line)

    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines) + '\n')

    print(f'[+] {len(output_lines)} lines written to {output_file} (removed {removed} lines with CDN IPs)')


def prompt_download_if_missing():
    if not os.path.exists(LATEST_CIDR_FILE):
        print(f'[!] Warning: {LATEST_CIDR_FILE} does not exist.')
        answer = input('[?] Do you want to download CIDR lists now? (y/n): ').strip().lower()
        if answer == 'y':
            download_and_extract_cidrs()
        else:
            print('[-] Aborting: latest CIDR file is required.')
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Remove CDN IPs based on CIDR lists.')
    parser.add_argument('--update', action='store_true', help='Download and update latest CIDRs')
    parser.add_argument('-ipl', '--input-ip-list', help='Input file (plain IPs or lines with embedded IPs)')
    parser.add_argument('-o', '--output', help='Output file with lines/IPs not in any CDN CIDR')

    args = parser.parse_args()

    if args.update:
        download_and_extract_cidrs()

    if args.input_ip_list and args.output:
        prompt_download_if_missing()
        cidrs = load_all_cidrs()
        filter_ips_in_lines(args.input_ip_list, args.output, cidrs)


if __name__ == '__main__':
    main()
