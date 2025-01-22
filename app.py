import os
from flask import Flask, render_template, request
import base64
import requests
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Get Hugging Face API key from the environment
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
def generate_caption(image_path):
    """Generate a caption using Hugging Face API."""
    url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

    # Read the image
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # Send the image to the Hugging Face API
    response = requests.post(url, headers=headers, files={"file": image_data})

    # Check if the response is successful
    if response.status_code == 200:
        # Extract the caption from the API response
        return response.json()['generated_text']
    else:
        # Print error details to the console for debugging
        print(f"Error: {response.status_code}")
        print(f"Response Text: {response.text}")
        return "Error generating caption"



@app.route('/', methods=['GET', 'POST'])
def index():
    base64_image = None
    hashtags = None  # Initialize hashtags to None
    if request.method == 'POST':
        image = request.files['image']
        image_path = "uploaded_image.jpg"
        image.save(image_path)

        base64_image = encode_image(image_path)

        # Generate a caption for the uploaded image
        caption = generate_caption(image_path)

        # Simple tag extraction from the caption (split by spaces and select the first 30 words)
        hashtags = caption.split()[:30]

        # Return a JSON response with the image data and hashtags
        response_data = {
            'image_data': f"data:image/jpeg;base64,{base64_image}",  # Send base64 image data
            'hashtags': hashtags
        }

        return response_data  # Flask automatically converts this to JSON response

    return render_template('index.html', hashtags=None)


if __name__ == '__main__':
    app.run(debug=True)
