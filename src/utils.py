from PIL import Image
import os.path


def convert_to_webp(file_path):
    webp_file_path = file_path.with_suffix(".webp")

    image = Image.open(file_path)
    image.save(webp_file_path, format="webp")

    return webp_file_path


def save_file(file_path, file_content):
    with open(file_path, 'wb') as f:
        f.write(file_content)


def get_file_ext(filename):
    return os.path.splitext(filename)[1]


def filename_without_ext(filename):
    return filename[:-len(get_file_ext(filename))]
