from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Set your Plant.id API key here
PLANT_ID_API_KEY = "3WlaILOu8TYnLImt2OtnqKfNFPK0ihKDeZGnjy2k1nF6wqu9Fp"
PLANT_ID_API_URL = "https://plant.id/api/v3/health_assessment"

@app.route('/detect_nutrient_deficiency', methods=['POST'])
def detect_nutrient_deficiency():
    data = request.get_json()

    if not data or "images" not in data:
        return jsonify({"error": "Please provide images as a list."}), 400

    images = data["images"]

    # Prepare request for Plant.id API
    payload = {
        "images": images
    }
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
    
    # Extract nutrient deficiency information
    nutrient_deficiency_found = False
    suggestions = []

    # Plant.id response structure: 'disease' -> 'suggestions'
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
    # Run Flask app
    app.run(debug=True)
