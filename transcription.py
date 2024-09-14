from anthropic import Anthropic
import base64
import pymupdf, fitz
from pathlib import Path
from PIL import Image
from io import BytesIO
import subprocess


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

def encode_pdf(source_fp: str, res_scale: int = 1) -> str:
    images = []
    with pymupdf.open(source_fp) as doc:
        for page in doc:
            if res_scale > 1:
                mat = fitz.Matrix(res_scale, res_scale)
                pix = page.get_pixmap(matrix=mat)
            else:
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

def notes_to_latex(client: Anthropic, fp: str) -> str:
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
    Center important equations and italicize key terms.
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

def get_youtube_queries(latex_document: str) -> str:
    yt_prompt = """Provide three youtube search queries that effectively recaps the content of this latex document.
    Provide each search query separated by newline characters. Do not include any other text in your response.
    Focus on section titles, key terms, and methods.
    Stick to one topic per youtube query.

    Some examples of good queries are: 
    - "completing the square to solve quadratic equations"
    - "how to choose the right cost function for neural networks"
    - "properties of alkaline metals"
    """

    message_list = [
        {
            "role": 'user',
            "content": [
                {"type": "text", "text": latex_document},
                {"type": "text", "text": yt_prompt}
            ]
        }
    ]

    MODEL_NAME = "claude-3-5-sonnet-20240620"
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2048,
        messages=message_list
    )
    return list(response.content[0].text.split("\n"))

def compile_latex(latex_document: str, latex_fp: str = "output.tex"):
    with open(latex_fp, "w") as file:
        file.write(latex_document)
    try:
        subprocess.run(["pdflatex", latex_fp], check=True)
        print(f"Successfully compiled tex file")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling tex file: {e}")


if __name__ == "__main__":
    client = create_client()
    response = notes_to_latex(client, "test_data/Lecture9.6-1 (2).pdf")
    compile_latex(response)
    encode_pdf("output.pdf", 2)
    # # print(response)
    # yt_query = get_youtube_query(response)
    # print(yt_query)