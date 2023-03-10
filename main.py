import os
import json
import requests
import ssl
from random import shuffle
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util.ssl_ import create_urllib3_context

directory_name = "realty_results" 
os.makedirs(directory_name, exist_ok=True)

single_house_url = "https://www.hepsiemlak.com/api/realties/2608-4401"
"https://www.hepsiemlak.com/api/realty-list?sortDirection=DESC&sortField=UPDATED_DATE&urlCriteria=satilik%2Ckonut&fillIntentUrls=true"
url = "https://www.hepsiemlak.com/api/realty-list/satilik?sortField=UPDATED_DATE&sortDirection=DESC&fillIntentUrls=true&size=200&page={page}"


# see "openssl ciphers" command for cipher names
# CIPHERS = "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384"
CIPHERS_ARR = [
  "TLS_AES_256_GCM_SHA384",
  "TLS_CHACHA20_POLY1305_SHA256",
  "TLS_AES_128_GCM_SHA256",
  "TLS_RSA_WITH_AES_128_CBC_SHA",
  "ECDHE-ECDSA-AES256-GCM-SHA384",
  "TLS_RSA_WITH_AES_256_CBC_SHA"
  "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
  "TLS_RSA_WITH_AES_128_GCM_SHA256",
  "TLS_RSA_WITH_AES_256_GCM_SHA384",
  "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
  "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
  "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
  "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
  "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
  "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
  "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
  "TLS_AES_256_GCM_SHA384",
  "TLS_CHACHA20_POLY1305_SHA256",
  "TLS_AES_128_GCM_SHA256",
  "ECDHE-ECDSA-AES256-GCM-SHA384",
]

user_agent_rotator = UserAgent()
user_agent = user_agent_rotator.get_random_user_agent()

headers = {
  'authority': 'www.hepsiemlak.com',
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'tr',
  'cookie': '_gcl_au=1.1.1309856467.1675939768; _tt_enable_cookie=1; _ttp=KOMohDwGztYdv3U1NS8apE1E5bW; _fbp=fb.1.1675939771901.1121433740; visited_city=34; visited_city_url=istanbul; i18n_redirected=tr; visited_name=%C4%B0stanbul; showDate=2023-02-23; showCount=2; ShowUnlistedBanner=false; cf_chl_2=813374be605a1ae; cf_clearance=VNrXRrkLZlC9CckATy8ZyC9tRUcMFq0unz7JUSRLEyM-1678297892-0-150; xpid=dmFsdWUlM0QxNjc1OTQwMTM3OTA3LTI3NC0zMzQtdjEuNC44JTJDbHMlM0QxNjc4Mjk4ODU3ODExJTJDcnQlM0Qx; xsid=dmFsdWUlM0QxNjc4Mjk4ODU3ODEwLTkzLTI4OS12MS40LjglMkNzcyUzRDElMkNydCUzRDE=; AMP_TOKEN=%24NOT_FOUND; _gid=GA1.2.555106025.1678298862; _gat_UA-5879168-1=1; new_vp=1; _ga=GA1.2.719947095.1675939772; _ga_1JXMT6R17H=GS1.1.1678298857.15.1.1678299470.0.0.0; cto_bundle=RxdPNV9Qc2gxM2JoNEgyTUlmYkF3JTJCMzl5MEs5ZHJnYkl1endQNmh6WmF5cUk0b2kwUHRFZ3JJZmlyam9YOXNoRDUzSWUyM0RzakxVeGNoOVllVERJSFYlMkY2bXBuZlNleUxEeSUyQkxGSjFBUXM1NkpBYzA1ZEpreU5nVTlLMDdqb0NYRVlZOGpWU1JQanp0YTBieVh5c01pRGNQTG9sVmpTajIwa0N6eFdscmN1QUlrdWVnSDR0b293M2QlMkJDaGZBWGZjUmxuZ0hpVEY5elRYeEJxMCUyQkJFazdrdlhvc1hkVGpuRFhXMDZzRUdjRmdIZklmMyUyRldxc3FwNkNkQUtkbGNvV0JMV2F5RWE0VTMzT1M0T3hmWEVVNW9sOHd3cTVackNuSUFSRnFvU0wzeGswaUo4ZW5Da1hzcUwxaENWT3lkRzBqQkkxZWJCWE54QXY1YmxjRjBkU3dkJTJGc2NZazR4emJtSHl5NktqbDR5YWpSTnEyTSUzRA',
  'desktop2019': '1',
  'referer': 'https://www.hepsiemlak.com/satilik?sortField=UPDATED_DATE&sortDirection=DESC',
  # Commented out not to make contradiction with user-agent
  # 'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
  # 'sec-ch-ua-mobile': '?0',
  # 'sec-ch-ua-platform': '"Linux"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': user_agent
}

shuffle(CIPHERS_ARR) 

CIPHERS = ":".join(CIPHERS_ARR)

class TlsAdapter(HTTPAdapter):
    def __init__(self, ssl_options=0, **kwargs):
        self.ssl_options = ssl_options
        super(TlsAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ctx = create_urllib3_context(ciphers=CIPHERS, cert_reqs=ssl.CERT_REQUIRED, options=self.ssl_options)
        self.poolmanager = PoolManager(*pool_args, ssl_context=ctx, **pool_kwargs)


adapter = TlsAdapter(ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)  # prioritize TLS 1.2 
# default = requests.get("https://tools.scrapfly.io/api/fp/ja3?extended=1").json()
session = requests.session()
session.mount("https://", adapter)

with open("last_page", "r+") as last_page_file:
  last_page = int(last_page_file.read())

response = session.get(url.format(page=last_page))
if int(response.status_code) != 200:
  raise Exception(f"realty list response error. Http status code: {response.status_code}, URL: {url.format(page=last_page)}")
    
list_result = response.json()
realty_list = list_result["realtyList"]
shuffle(realty_list)
for reality in realty_list:
    single_response = session.get(f"https://www.hepsiemlak.com/api/realties/{reality['id']}")
    if int(single_response.status_code) != 200:
      raise Exception(f"single realty response error. Http status code: {single_response.status_code}")
        
    with open(f"{directory_name}/{str(reality['id'])}.json", "w") as file:
        json.dump(single_response.json(), file, indent=4)


with open("last_page", "w") as last_page_file:
  last_page_file.write(str(last_page-1))