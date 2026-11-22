import urllib.request
import re

req2 = urllib.request.Request('https://peakcut.haziqqasmi.com/', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req2) as r:
        html2 = r.read().decode('utf-8', errors='ignore')
        scripts2 = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"]', html2)
        print('Landing scripts:', scripts2)
        links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', html2)
        print('Landing links:', set(links))
except Exception as e:
    print('Error:', e)
