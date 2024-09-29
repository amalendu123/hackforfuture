from flask import Flask, request, jsonify, render_template
import os
import pandas as pd
import google.generativeai as genai

app = Flask(__name__)

# Configure the Gemini API
os.environ["GOOGLE_API_KEY"] = "AIzaSyCQ0o6QCWeSn6czUrGu0kAGmtxKTV8oq8U"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Fine-tuning data for chatbot
fine_tuning_data = {
    "What is green certification?": "Green certification verifies eco-friendly building practices.",
}

# Dataset for material recommendations
materials = [
    {"MaterialName": "Recycled Steel", "BuildingType": "Commercial", "EnvironmentalImpact": 2, "Cost": 5000, "Rating": 4.5},
    {"MaterialName": "Bamboo Flooring", "BuildingType": "Residential", "EnvironmentalImpact": 1, "Cost": 3000, "Rating": 4.2},
    {"MaterialName": "Solar Glass", "BuildingType": "Commercial", "EnvironmentalImpact": 1, "Cost": 8000, "Rating": 4.8},
    {"MaterialName": "Recycled Plastic Lumber", "BuildingType": "Residential", "EnvironmentalImpact": 2, "Cost": 2000, "Rating": 3.9},
    {"MaterialName": "Cork Insulation", "BuildingType": "Residential", "EnvironmentalImpact": 1, "Cost": 1500, "Rating": 4.1},
    {"MaterialName": "Reclaimed Wood", "BuildingType": "Commercial", "EnvironmentalImpact": 1, "Cost": 4000, "Rating": 4.3},
    {"MaterialName": "Hempcrete", "BuildingType": "Residential", "EnvironmentalImpact": 1, "Cost": 3500, "Rating": 3.8},
    {"MaterialName": "Mycelium Insulation", "BuildingType": "Commercial", "EnvironmentalImpact": 1, "Cost": 2500, "Rating": 3.7},
    {"MaterialName": "Recycled Glass Countertops", "BuildingType": "Residential", "EnvironmentalImpact": 2, "Cost": 4500, "Rating": 4.0},
    {"MaterialName": "Straw Bale Insulation", "BuildingType": "Residential", "EnvironmentalImpact": 1, "Cost": 1000, "Rating": 3.5},
]
df = pd.DataFrame(materials)

# Chatbot response logic
def find_response(prompt):
    return fine_tuning_data.get(prompt)

def get_gemini_response(question):
    fine_tuned_response = find_response(question)
    if fine_tuned_response:
        return fine_tuned_response
    else:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(question)
        return response.text

# AI Image generation logic
def generate_prompt(description):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"Create a green building design prompt based on: {description}")
    return response.text.strip()

def generate_building_image():
    description = "generate an eco-friendly building design"
    prompt = generate_prompt(description)
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
    return url

# Material recommender logic
def generate_material_description(material_name):
    prompt = f"Provide a brief description of {material_name} and its use in green building."
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

@app.route('/')
def index():
    image_url = generate_building_image()
    return render_template('index.html', image_url=image_url)

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get('input')
    response = get_gemini_response(user_input)
    return jsonify({'response': response})

@app.route('/recommend', methods=['GET'])
def recommend_materials():
    budget = float(request.args.get('budget'))
    building_type = request.args.get('buildingType')

    filtered_df = df[(df['Cost'] <= budget) & (df['BuildingType'] == building_type)]

    if filtered_df.empty:
        return jsonify({"message": "No materials found matching your criteria"}), 404

    top_environmental = filtered_df.nlargest(3, 'EnvironmentalImpact')[['MaterialName', 'Cost', 'EnvironmentalImpact']]
    descriptions = [{"MaterialName": row['MaterialName'], 
                     "Description": generate_material_description(row['MaterialName'])}
                    for index, row in top_environmental.iterrows()]

    return jsonify({"recommendations": descriptions})

if __name__ == '__main__':
    app.run(debug=True)
