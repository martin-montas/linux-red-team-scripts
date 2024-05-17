#!          /usr/bin/python3

#                   Networking/return-https-headers.py
#                          by martin-montas 
#
#
#

import requests

url = "http://192.168.56.104"
response = requests.head(url)

# prints the entire header as a dictionary
print(response.headers) 

response.close()
