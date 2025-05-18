import httpx,socket
import time,json
#JSON配置文件
"""
{
     "zone_id":"xxxxxx",
     "token":"xxxxxxx",
     "domain":"example.com"
}
"""
config = json.loads(open('config.json','r',encoding='utf-8').read())
print(config)
def get_ipv6():
    #获取本机ip
    addrs = socket.getaddrinfo(socket.gethostname(),None,socket.AF_INET6)
    ipv6_list = [addr[4][0] for addr in addrs]
    # 按优先级排序
    sorted_ips = sorted(ipv6_list, key=lambda ip: (
        0 if ip.startswith('2') or ip.startswith('3') else  # 优先 GUA
        1 if ip.startswith('fd') else  # 最后 ULA
        2  # 其他（如链路本地地址 fe80::/10）
    ))
    return sorted_ips[0] if sorted_ips else None
def cf_get_record_id():
    url = f'https://api.cloudflare.com/client/v4/zones/{config["zone_id"]}/dns_records'
    headers = {
        'Authorization': f'Bearer {config["token"]}',
        'Content-Type': 'application/json'
    }
    response = httpx.get(url, headers=headers)
    #在result中查找name=config["domain"]的id
    for result in response.json().get('result', []):
        if result['name'] == config["domain"]:
            return result['id']

def cf_ddns(ipv6):
    record_id = cf_get_record_id()
    if not record_id:#create dns
        url = f'https://api.cloudflare.com/client/v4/zones/{config["zone_id"]}/dns_records'
        headers = {
            'Authorization': f'Bearer {config["token"]}',
            'Content-Type': 'application/json'
        }
        data = {
            'type': 'AAAA',
            'name': config["domain"],
            'content': ipv6,
            'proxied': False,
            'ttl': 1
        }
        response = httpx.post(url, headers=headers, json=data)
        print(response)
        print("Create new dns:",config["domain"])
    else:#update dns
        url = f'https://api.cloudflare.com/client/v4/zones/{config["zone_id"]}/dns_records/{record_id}'
        headers = {
            'Authorization': f'Bearer {config["token"]}',
            'Content-Type': 'application/json'
        }
        data = {
            'type': 'AAAA',
            'name': config["domain"],
            'content': ipv6,
            'ttl': 1
        }
        response = httpx.patch(url, headers=headers, json=data)
        print(response)
        print("Update dns:",config["domain"])
def main():
    current_ip = None
    while True:
        try:
            ipv6 = get_ipv6()
            if ipv6 != current_ip:
                print(f"IP changed:{current_ip} -> {ipv6}")
                try:
                    cf_ddns(ipv6)
                    current_ip = ipv6
                    print("Updated CloudFlare DNS record successfully.")
                except Exception as e:
                    print("Failed to update CloudFlare DNS record:", e)
        except Exception as e:
            print(e)
        time.sleep(60)

if __name__ == "__main__":
    main()