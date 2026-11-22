# --------------------------------------------------------------------------
# ClipCut AI Studio
# Author: CM Studio (https://github.com/CM-Studio77)
# Repository: https://github.com/CM-Studio77/Clipcut
# Copyright (c) 2026 CM Studio. All rights reserved.
# Licensed under Apache License 2.0. See LICENSE for details.
# --------------------------------------------------------------------------
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
