import os

from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="creds.json"

client = vision.ImageAnnotatorClient()
gcs_uri = f"https://storage.googleapis.com/hackwestern-bennyhawk/input_5397b9ef-b727-411a-9098-b651acb53afd.jpeg"
req = {
        "image": {"source": {'image_uri': gcs_uri}}
    }

# Call the Vision API
response = client.annotate_image(req)
print(response.text_annotations)