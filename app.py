from flask import Flask, request, jsonify
import requests
import base64

app = Flask(__name__)

# Set your Plant.id API key
PLANT_ID_API_KEY = "3WlaILOu8TYnLImt2OtnqKfNFPK0ihKDeZGnjy2k1nF6wqu9Fp"
PLANT_ID_API_URL = "https://plant.id/api/v3/health_assessment"

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

    # Prepare request to Plant.id API
    payload = {"images": images_base64}
    headers = {
        "Api-Key": PLANT_ID_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(PLANT_ID_API_URL, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

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
