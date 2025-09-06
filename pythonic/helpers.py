

# Standard library imports
import os
import secrets

# PIL (Pillow) for image processing
from PIL import Image

# Flask application context
from flask import current_app


def save_picture(form_picture, path, output_size=None):
    """
    Save uploaded image file with optional resizing.
    
    Args:
        form_picture: FileStorage object from form
        path (str): Directory path to save the image
        output_size (tuple, optional): Target dimensions (width, height) for resizing
    
    Returns:
        str: Generated filename of the saved image
    
    This function generates a unique filename using cryptographic randomness,
    processes the image with PIL if resizing is requested, and saves it
    to the specified directory path.
    """
    # Generate cryptographically secure random hex for unique filename
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    
    # Construct full file path within application directory
    picture_path = os.path.join(current_app.root_path, path, picture_name)
    
    # Open and process image with PIL
    i = Image.open(form_picture)
    if output_size:   
        i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_name