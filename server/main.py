import os
import re
from tempfile import TemporaryDirectory
from uuid import uuid4
import logging

import requests
from flask import Flask, request, jsonify
from google.cloud import storage

from pathfinder import generate_img_with_path
from providers import create_n_send_text_message, create_n_send_image_message
from room_detector import invoke_vision_api

app = Flask(__name__)
storage_client = storage.Client()

logger = logging.getLogger()

bucket = storage_client.get_bucket("hackwestern-bennyhawk")


@app.route("/", methods=['POST'])
def hello_world():
    logger.info(request.get_json())
    print(request.get_json())
    data = request.get_json()['results']
    if data:
        data = data[0]
        from_number = data['from']
        try:
            message = data['message']
            if message['type'] == 'IMAGE':
                url = message['url']
                caption = message.get('caption', None)
                if caption is None:
                    create_n_send_text_message(to_number=from_number,
                                               text_reply="Seems like you have not included a caption! "
                                                          "Please resend the image with a caption")
                    return jsonify({}), 200

                regex = r".*?(\d{3}).*?(\d{3}).*"
                subst = "\\1-\\2"

                # You can manually specify the number of replacements by changing the 4th argument
                result = re.sub(regex, subst, caption, 0, re.MULTILINE)

                if not result:
                    logger.warning("Unable to parse the string")
                    return jsonify({}), 200

                from_loc, to_loc = result.split('-')

                headers = {
                    'Authorization': f'App {os.getenv("INFO_BIP_API_KEY")}',
                    'Accept': 'application/json'
                }

                response = requests.get(url=url, headers=headers)
                print(response)

                if response.status_code != 200:
                    logger.warning("Unable to retrieve the image")
                    return jsonify({}), 200

                with TemporaryDirectory() as temp_dir:
                    uuid_data = str(uuid4())
                    input_file = f"input_{uuid_data}.jpeg"
                    output_file = f"output_{uuid_data}.jpeg"

                    with open(f"{temp_dir}/{input_file}", "wb") as out_file:
                        out_file.write(response.content)

                    blob = bucket.blob(input_file)
                    blob.upload_from_filename(f"{temp_dir}/{input_file}")

                    output_json = invoke_vision_api(input_image_name=input_file)
                    print(output_json)

                    # from_loc = "109"
                    # to_loc = "159"

                    start_tuple = None
                    end_tuple = None

                    for i in output_json:
                        if i['description'] == from_loc:
                            start_tuple = (int(i['y']), int(i['x']))
                        if i['description'] == to_loc:
                            end_tuple = (int(i['y']), int(i['x']))

                    if start_tuple is None:
                        logger.warning(f"Start tuple {start_tuple} is none")
                        return jsonify({}), 200
                    if end_tuple is None:
                        logger.warning(f"End tuple {end_tuple} is none")
                        return jsonify({}), 200

                    generate_img_with_path(f"{temp_dir}/{input_file}",
                                           f"{temp_dir}/{output_file}",
                                           start_tuple=start_tuple,
                                           end_tuple=end_tuple)

                    blob = bucket.blob(output_file)
                    blob.upload_from_filename(f"{temp_dir}/{output_file}")

                    create_n_send_image_message(to_number=from_number,
                                                media_url=f"https://storage.googleapis.com/hackwestern-bennyhawk/{output_file}",
                                                caption="This is a test")
                return jsonify({}), 200

        except Exception as e:
            logger.exception("Exception!!!")
            create_n_send_text_message(to_number=from_number,
                                       text_reply=f"Oh no! Something went wrong! {str(e)}")
            return jsonify({}), 200
    else:
        return jsonify({}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
