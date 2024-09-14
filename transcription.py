from anthropic import Anthropic
import base64
import fitz
from pathlib import Path
from PIL import Image
from io import BytesIO


def create_client():
    return Anthropic(
        api_key="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"
    )


def concat_images(images) -> Image:
    if len(images) == 1:
        return images[0]
    else:
        dst = Image.new('RGB', (max(im.width for im in images), sum(im.height for im in images)))
        cur_height = 0
        for im in images:
            dst.paste(im, (0, cur_height))
            cur_height += im.height
        return dst

def encode_pdf(source_fp: str) -> str:
    images = []
    with fitz.open(source_fp) as doc:
        for page in doc:
            # fitz.Matrix(2, 2)
            pix = page.get_pixmap()
            images.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))

    image = concat_images(images)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    img_str = img_str.decode('utf-8')
    return img_str

def encode_image(fp: str) -> str:
    with open(fp, "rb") as image_file:
        binary_data = image_file.read()
        base_64_encoded_data = base64.b64encode(binary_data)
        base64_string = base_64_encoded_data.decode('utf-8')
    return base64_string


def get_response(client: Anthropic, fp: str) -> str:
    file_path = Path(fp)
    ftype = file_path.suffix

    if ftype == ".pdf":
        img_str = encode_pdf(fp)
    elif ftype == ".jpeg":
        img_str = encode_image(fp)
    else:
        return "Unsupported image type."

    LATEX_PROMPT = """
    Convert these lecture notes to latex.
    Add headers and sections, so that the notes are easy to read.
    Don't indent the first line of each paragraph.
    Reduce margins.
    Return just the latex code, nothing else.
    """

    message_list = [
        {
            "role": 'user',
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_str}},
                {"type": "text", "text": LATEX_PROMPT}
            ]
        }
    ]

    MODEL_NAME = "claude-3-5-sonnet-20240620"
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2048,
        messages=message_list
    )
    return response.content[0].text


if __name__ == "__main__":
    client = create_client()
    response = get_response(client, "test_data/Lecture9.6-1 (2).pdf")
    print(response)