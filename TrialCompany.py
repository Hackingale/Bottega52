import requests

url = "https://crunchbase4.p.rapidapi.com/company"

payload = { "company_domain": "apple" }
headers = {
	"content-type": "application/json",
	"X-RapidAPI-Key": "f6bbea758cmsh3774b5b0d2d5f6ap15a8d5jsnf115573bd417",
	"X-RapidAPI-Host": "crunchbase4.p.rapidapi.com"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())