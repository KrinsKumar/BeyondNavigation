import re

from google.cloud import vision
from google.cloud.vision_v1 import AnnotateImageResponse


def __calculate_average_coordinates(response: AnnotateImageResponse):
    filtered_items = [item for item in response.text_annotations if re.match(r'^\d+$', item.description)]
    result = []

    for item in filtered_items:
        vertices = item.bounding_poly.vertices
        total_x = sum(vertex.x for vertex in vertices)
        total_y = sum(vertex.y for vertex in vertices)
        avg_x = total_x / len(vertices)
        avg_y = total_y / len(vertices)

        result.append({
            'description': item.description,
            'x': avg_x,
            'y': avg_y
        })

    return result


def invoke_vision_api(input_image_name: str):
    # Create a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file in your Google Cloud Storage bucket
    gcs_uri = f"https://storage.googleapis.com/hackwestern-bennyhawk/{input_image_name}"

    # Construct an image instance
    # image = vision.Image()
    # image.source.image_uri = gcs_uri
    #
    # # Features you want to extract
    # features = [{'type': vision.Feature.Type.TEXT_DETECTION}]
    #
    # # Build the request
    # request = {'image': image, 'features': features}

    req = {
        "image": {"source": {'image_uri': gcs_uri}}
    }

    # Call the Vision API
    response: AnnotateImageResponse = client.annotate_image(req)
    print(response)

    return __calculate_average_coordinates(response)
