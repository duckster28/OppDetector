import requests
import json
import os

# Ensure the directories exist
# os.makedirs("cuhacking6", exist_ok=True)


API_KEY = "gsk-3yYJ9wr3nF6j63UY8fT3idTc96jxjK4A"
API_ENDPOINT = "https://toronto-mans--development.gadget.app/api/graphql"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer gsk-3yYJ9wr3nF6j63UY8fT3idTc96jxjK4A"
}


test_query = """
{
  gngs {
    edges {
      node {
        id
        name
        image {
          url
        }
      }
    }
  }
}
"""

def download_image(image_url, save_path):
    img_response = requests.get(image_url)
    if img_response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(img_response.content)
    else:
        print(f"Failed to download image from {image_url}")

response = requests.post(
    API_ENDPOINT,
    headers=headers,
    json={"query": test_query}
)

if response.status_code == 200:
    data = response.json()
    images = data.get("data", {}).get("gngs", {}).get("edges", [])
    for idx, edge in enumerate(images):
        image_url = edge["node"]["image"]["url"]
        save_path = os.path.join(os.getcwd(), f"image_{idx}.jpg")
        download_image(image_url, save_path)
else:
    print(f"Query failed with status code {response.status_code}")

response = requests.post(
    API_ENDPOINT,
    headers=headers,
    json={"query": test_query}
)

print(f"Status code: {response.status_code}")
print(json.dumps(response.json(), indent=2))