import os
import time
import json
from typing import Any, Dict, List
import requests
from requests.exceptions import ConnectionError
import ssl
from urllib3.exceptions import MaxRetryError, ProtocolError
from random import shuffle, randint
from random_user_agent.user_agent import UserAgent
from adapters import TlsAdapter
import logging
import settings

logger = logging.getLogger("messagereport")


"""
TODO:
internal_id, data_source, url, version(int), price, currency, predicted_price, predicted_rental_price, created_at, updated_at, inserted_at
attributes tablosunda olacak ilave fieldlar: data_source(hepsiemlak, sahibinden), realty_type(daire, villa, müstakil ev vs.), type(sale/rental)
SELECT ARRAY(SELECT unnest(ARRAY[1,2,3,4,5]) EXCEPT SELECT id FROM houses);
"""

directory_name = "realty_results2" 
os.makedirs(directory_name, exist_ok=True)

single_house_url = "https://www.hepsiemlak.com/api/realties/2608-4401"
"https://www.hepsiemlak.com/api/realty-list?sortDirection=DESC&sortField=UPDATED_DATE&urlCriteria=satilik%2Ckonut&fillIntentUrls=true"
url = "https://www.hepsiemlak.com/api/realty-list/satilik?sortField=UPDATED_DATE&sortDirection=DESC&fillIntentUrls=true&size=200&page={page}"


# see "openssl ciphers" command for cipher names
# CIPHERS = "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384"
CIPHERS_ARR = [
   "AES128-SHA256",
   "AES256-SHA256",
   "AES128-GCM-SHA256",
   "AES256-GCM-SHA384",
   "DH-RSA-AES128-SHA256",
   "DH-RSA-AES256-SHA256",
   "DH-RSA-AES128-GCM-SHA256",
   "DH-RSA-AES256-GCM-SHA384",
   "DH-DSS-AES128-SHA256",
   "DH-DSS-AES256-SHA256",
   "DH-DSS-AES128-GCM-SHA256",
   "DH-DSS-AES256-GCM-SHA384",
   "DHE-RSA-AES128-SHA256",
   "DHE-RSA-AES256-SHA256",
   "DHE-RSA-AES128-GCM-SHA256",
   "DHE-RSA-AES256-GCM-SHA384",
   "DHE-DSS-AES128-SHA256",
   "DHE-DSS-AES256-SHA256",
   "DHE-DSS-AES128-GCM-SHA256",
   "DHE-DSS-AES256-GCM-SHA384",
   "ECDHE-RSA-AES128-SHA256",
   "ECDHE-RSA-AES256-SHA384",
   "ECDHE-RSA-AES128-GCM-SHA256",
   "ECDHE-RSA-AES256-GCM-SHA384",
   "ECDHE-ECDSA-AES128-SHA256",
   "ECDHE-ECDSA-AES256-SHA384",
   "ECDHE-ECDSA-AES128-GCM-SHA256",
   "ECDHE-ECDSA-AES256-GCM-SHA384",
   "ADH-AES128-SHA256",
   "ADH-AES256-SHA256",
   "ADH-AES128-GCM-SHA256",
   "ADH-AES256-GCM-SHA384",
   "AES128-CCM",
   "AES256-CCM",
   "DHE-RSA-AES128-CCM",
   "DHE-RSA-AES256-CCM",
   "AES128-CCM8",
   "AES256-CCM8",
   "DHE-RSA-AES128-CCM8",
   "DHE-RSA-AES256-CCM8",
   "ECDHE-ECDSA-AES128-CCM",
   "ECDHE-ECDSA-AES256-CCM",
   "ECDHE-ECDSA-AES128-CCM8",
   "ECDHE-ECDSA-AES256-CCM8",
   "DHE-RSA-AES128-GCM-SHA256",
   "ECDHE-ECDSA-AES256-SHA384",
   "ECDHE-RSA-AES256-SHA384"
]

# CIPHERS_ARR = [
#    "DHE-RSA-AES128-GCM-SHA256",
#    "ECDHE-ECDSA-AES256-SHA384",
#    "ECDHE-RSA-AES256-SHA384",
#    "DHE-RSA-AES256-SHA256"
# ]

headers = {
  'authority': 'www.hepsiemlak.com',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'en,tr-TR;q=0.9,tr;q=0.8',
  'cache-control': 'max-age=0',
  'cookie': '_gcl_au=1.1.1309856467.1675939768; _tt_enable_cookie=1; _ttp=KOMohDwGztYdv3U1NS8apE1E5bW; _fbp=fb.1.1675939771901.1121433740; visited_city=34; visited_city_url=istanbul; i18n_redirected=tr; visited_name=%C4%B0stanbul; showDate=2023-02-23; showCount=2; ShowUnlistedBanner=false; _gid=GA1.2.599585922.1678714802; _gcl_aw=GCL.1678746308.Cj0KCQjwk7ugBhDIARIsAGuvgPa4c2lYF0RsRtv_vc9yul6N0YtUQ2HeYzSRlZwfjQDaBLV3Bj8VFVUaAmtXEALw_wcB; xpid=dmFsdWUlM0QxNjc1OTQwMTM3OTA3LTI3NC0zMzQtdjEuNC44JTJDbHMlM0QxNjc4NzQ2MzA4ODIyJTJDcnQlM0Qx; _ga=GA1.2.719947095.1675939772; _gac_UA-5879168-1=1.1678746312.Cj0KCQjwk7ugBhDIARIsAGuvgPa4c2lYF0RsRtv_vc9yul6N0YtUQ2HeYzSRlZwfjQDaBLV3Bj8VFVUaAmtXEALw_wcB; cto_bundle=Kc-6-19Qc2gxM2JoNEgyTUlmYkF3JTJCMzl5MEpFZXAyQ2lvUllubTFuU1RNNVNSUEVrMmlIbjQyeE9kM2RQRWNKOGdsc2RnSjVTSFMxcktZRFdOTHJjOUhMQ1NnOXJTQyUyQlE3dU5Edmg5ZkxJUUZZdDNWRmExanlkY1VHTU5KZFZSTzBEJTJGNTVLZ1FvNEI5RTk5eWdPZyUyRnc0emVuUHc0STclMkJ0VGtsaEZZWmxBWGxVVDVtRW1LWG1YJTJGQm5ZayUyRmlIT0dkZ21HTzRuVHBldXNtVyUyQmFRdUVHOGtKMGdFTm1ZR3YyRmQ4UmR2OUdzc0R0VFVhOVVZOGNnQ1lHZiUyQlhKRzFxYUdqaDVFVWhKaGtnaDE1RjlNTFRpOE8zZTFhZzNtbiUyQkgyMnd0V0V5WFNOeTlBMlNJdFpwSXBld1M1bSUyQmNmUEFiVzklMkJqS3VWYSUyQnpVUGh3MDVrRUpISGs2NjdQb0slMkZoeiUyQndDbmtRNURlWDNobDZtSW8lM0Q; new_vp=1; _ga_1JXMT6R17H=GS1.1.1678746308.20.1.1678746356.0.0.0; cf_chl_2=aebf2e4bd7b38f4; cf_clearance=E6slt8nRle0jXKaOvAhFASkdvaudbVqDQZvx6RQOITs-1678779103-0-250',
  'if-none-match': 'W/"0bad6ef33c249b4157b7bcf31c1301a3f"',
  'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': UserAgent().get_random_user_agent()
}



def generate_session_with_unique_fingerprint(headers: Dict[Any, Any], ciphers: List[str]):
  # default = requests.get("https://tools.scrapfly.io/api/fp/ja3?extended=1").json()
  session = requests.session()
  session.headers.update(headers)
  shuffle(ciphers) 
  CIPHERS = ":".join(ciphers)
  adapter = TlsAdapter(ciphers = CIPHERS, ssl_options = ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)  # prioritize TLS 1.2 
  session.mount("https://", adapter)
  return session



while True:
  with open("last_page", "r+") as last_page_file:
    last_page = int(last_page_file.read())
  """TODO: Buradan aşağısını bir fonksiyon haline getir. 
  Bu fonksiyon parametre olarak last_page'i alsın.
  Bir satılık için bir kiralık için listeyi getirsin"""
  session = generate_session_with_unique_fingerprint(headers, CIPHERS_ARR)
  
  response = session.get(url.format(page=last_page))

  if response.raise_for_status():
    continue

  logger.info(f"Started page: {last_page}")

  list_result = response.json()
  realty_list = list_result["realtyList"]
  shuffle(realty_list)
  for index, reality in enumerate(realty_list):
    try:
      single_response = session.get(f"https://www.hepsiemlak.com/api/realties/{reality['id']}")
    except MaxRetryError as e:
      logger.warning(f"MaxRetryError: {e}")
      continue
    except ConnectionError as e:
      logger.warning(f"ConnectionError: {e}")
      continue
    except ProtocolError as e:
      logger.warning(f"ProtocolError: {e}")
      continue
    
    if single_response.raise_for_status():
      continue
        
    with open(f"{directory_name}/{str(reality['id'])}.json", "w") as file:
      json.dump(single_response.json(), file, indent=4, ensure_ascii=False)

    if index % 3 == 0:
      session = generate_session_with_unique_fingerprint(headers, CIPHERS_ARR)
      time.sleep(randint(0,10))


  with open("last_page", "w") as last_page_file:
    last_page_file.write(str(last_page-1))
    logger.info(f"Closed last_page file on page: {last_page}")