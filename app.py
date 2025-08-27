from flask import Flask, request, jsonify
import requests
import base64
import time
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Set your Plant.id API key
PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY")
PLANT_ID_API_URL = "https://plant.id/api/v3/health_assessment"

MAX_RETRIES = 3  # Total attempts
RETRY_DELAY = 2  # Seconds between retries

@app.route('/detect_nutrient_deficiency', methods=['POST'])
def detect_nutrient_deficiency():
    if 'images' not in request.files:
        return jsonify({"error": "Please upload at least one image file under the key 'images'."}), 400

    uploaded_files = request.files.getlist('images')
    images_base64 = []

    # Convert uploaded files to base64
    for file in uploaded_files:
        file_content = file.read()
        encoded_string = base64.b64encode(file_content).decode('utf-8')
        images_base64.append(f"data:{file.content_type};base64,{encoded_string}")

    payload = {"images": images_base64}
    headers = {
        "Api-Key": PLANT_ID_API_KEY,
        "Content-Type": "application/json"
    }

    # Retry mechanism
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(PLANT_ID_API_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            break  # Successful request, exit loop
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)  # Wait before retrying
            else:
                return jsonify({"error": f"Failed after {MAX_RETRIES} attempts: {str(e)}"}), 500

    result = response.json()

    # Check for nutrient deficiency
    nutrient_deficiency_found = False
    suggestions = []

    for disease in result.get("diseases", []):
        for suggestion in disease.get("suggestions", []):
            if "nutrient deficiency" in suggestion.get("name", "").lower():
                nutrient_deficiency_found = True
                suggestions.append(suggestion.get("name"))

    return jsonify({
        "nutrient_deficiency": nutrient_deficiency_found,
        "details": suggestions
    })


if __name__ == "__main__":
    app.run(debug=True)
