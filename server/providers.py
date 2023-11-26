import os

from infobip_channels.whatsapp.channel import WhatsAppChannel
from infobip_channels.whatsapp.models.body.image_message import ImageMessageBody

from dotenv import load_dotenv
from infobip_channels.whatsapp.models.body.text_message import TextMessageBody

load_dotenv()

channel = WhatsAppChannel.from_auth_params({
    "base_url": os.getenv("INFO_BIP_URL"),
    "api_key": os.getenv("INFO_BIP_API_KEY")
})


def create_n_send_image_message(to_number: str, media_url: str, caption: str):
    body = ImageMessageBody(**{
        "from_number": os.getenv("INFO_BIP_FROM_PHONE"),
        "to": to_number,
        "notify_url": os.getenv("DEBUG_WEB_SOCKET"),
        "content": {
            "media_url": media_url,
            "caption": "Here is your path!"
        }
    })

    response = channel.send_image_message(body)
    print(response)


def create_n_send_text_message(to_number: str, text_reply: str):
    body = TextMessageBody(**{
        "from_number": os.getenv("INFO_BIP_FROM_PHONE"),
        "to": to_number,
        "notify_url": os.getenv("DEBUG_WEB_SOCKET"),
        "content": {
            "text": text_reply
        }
    })

    response = channel.send_text_message(body)
    print(response)
