import requests

response = requests.post("http://127.0.0.1:5000/ad",
                        json={"title": "title_1", "description": "description_1", "owner": "owner_1"},
                        )
print(response.status_code)
print(response.json())


response = requests.get(
    "http://127.0.0.1:5000/ad/1/")
print(response.status_code)
print(response.json())


response = requests.delete(
    "http://127.0.0.1:5000/ad/1/")
print(response.status_code)
print(response.json())

