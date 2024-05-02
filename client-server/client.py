def extract_features(packet_data):
  """
  Extracts features from a sample packet for PII detection.

  Args:
      packet_data: A dictionary containing packet information.

  Returns:
      A list of extracted features.
  """

  features = []

  # URL features
  uri = packet_data.get('uri')
  if uri:
    domain = uri.split('/')[0]  # Extract domain name
    path_components = uri.split('/')[1:]  # Extract path components (consider further processing)
    query_params = uri.split('?')[1:]  # Extract query parameters (consider parsing key-value pairs)
    features.extend([domain, len(path_components), len(query_params)])  # Add features

  # Header features
  headers = packet_data.get('headers')
  if headers:
    user_agent = headers.get('user-agent')
    if user_agent:
      # Consider using libraries like user-agents to parse user agent string for specific details
      features.append(user_agent)  # Add user-agent string (can be further processed)

  # Traffic features
  protocol = packet_data.get('protocol')
  if protocol:
    features.append(protocol)  # Add protocol type

  # Additional features (can be extended based on your needs)
  features.append(packet_data.get('method'))  # Add HTTP method (GET, POST)

  return features

# Example usage
packet = {
  "ts": "1489428862012",
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
  "uri": "/7/984/137298/v1/auth.akacast.akamaistream.net/iair-fl?deviceid=8c760ee1-a9f5-36c3-a97e-35cfd61552ec&clienttype=Android&carrier=Unknown&iheartradioversion=7.2.2&osversion=7.0&devicename=Nexus 6&host=android.mobile.us&callLetters=IAIR-HD&fbbroadcast=0&streamid=5163&terminalid=181&init_id=8169&at=0&profileid=353553736",
  "user_agent": None
}

features = extract_features(packet)
print(features)
