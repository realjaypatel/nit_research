k = {
        "domain": "", 
        "dst_ip": "173.245.199.56", 
        "dst_port": 80, 
        "headers": {
            "accept-encoding": "gzip", 
            "connection": "Keep-Alive", 
            "host": "iair-fl.akacast.iheart.com", 
            "icy-metadata": "1", 
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 7.0; Nexus 6 Build/NBD91Y)"
        }, 
        "host": "iair-fl.akacast.iheart.com", 
        "is_foreground": False, 
        "is_host_ip": 0, 
        "label": 0, 
        "md5": None, 
        "method": "GET", 
        "package_name": "com.clearchannel.iheartradio.controller", 
        "package_version": "7.2.2", 
        "pii_types": None, 
        "platform": "android", 
        "post_body": None, 
        "protocol": "HTTP", 
        "referrer": None, 
        "scr_port": 41264, 
        "src_ip": "192.168.0.2", 
        "tk_flag": None, 
        "ts": "1489428862012", 
        "uri": "/7/984/137298/v1/auth.akacast.akamaistream.net/iair-fl?deviceid=8c760ee1-a9f5-36c3-a97e-35cfd61552ec&clienttype=Android&carrier=Unknown&iheartradioversion=7.2.2&osversion=7.0&devicename=Nexus 6&host=android.mobile.us&callLetters=IAIR-HD&fbbroadcast=0&streamid=5163&terminalid=181&init_id=8169&at=0&profileid=353553736", 
        "user_agent": None
    }

ans = []
for x,y in k.items():
    # print(x)
    ans.append(x)
print(ans)