import sys
from io import BytesIO
from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile

def get_image_data():
    io = BytesIO()
    size = (200,200)
    color = (255,0,0,0)
    image = Image.new("RGBA", size, color)
    image.save(io, format='JPEG')
    io.seek(0)
    return io

def get_image_in_memory_data():
    io = get_image_data()
    image_file = InMemoryUploadedFile(io, None, 'foo.jpg', 
                            'jpeg', sys.getsizeof(io), None)
    image_file.seek(0)
    return image_file

def create_image_file(name):
    io = get_image_data()
    with open(name, 'wb') as f:
        f.write(io.read())

def get_image_size(path):
    with Image.open(path) as img:
        return img.size
