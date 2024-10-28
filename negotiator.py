import cohere
import streamlit as st
import json
import ast

co = cohere.ClientV2("your_api_key")

# This function creates negotiation scenarios tailored to specific industries or situations.
def generate_negotiation_scenario(industry, difficulty, temperature):
    prompt = f"""
    Generate a {difficulty} negotiation scenario for the {industry} industry. Keep it brief—no more than 2 lines—and focus on dialogue-based scenarios that set the scene quickly. Seller makes a selling statement then stops for the buyer to respond.
    
    Example: Buyer and seller meet to negotiate the price of a used car. The seller wants $10,000. Both are willing to make concessions if the other party shows flexibility.
    """
    
    response = co.chat(
        messages=[{"role": "user", "content": prompt}],
        model="command-r-plus-08-2024",
        temperature=temperature
    )
    return response.message.content[0].text

import re

# This function evaluates the user’s response for tone, content, and negotiating skills.
def analyze_response(user_response, temperature):
    prompt = """
    Analyze the following negotiation response and provide feedback on tone, clarity, and effectiveness. 
    Please format your analysis as a Python dictionary object with the keys 'Tone', 'Clarity', and 'Negotiation Tactics'. 
    The values should be integers ranging from 0 to 100, reflecting the respective scores based on your analysis.

    Response: {user_response}

    Please provide the analysis in this format:
    analysis = {{
        'Tone': <score>,
        'Clarity': <score>,
        'Negotiation Tactics': <score>
    }}
    """.format(user_response=user_response)

    response = co.chat(
        messages=[{"role": "user", "content": prompt}],
        model="command-r-plus-08-2024",
        temperature=temperature
    )

    match = re.search(r"=\s*({.*?})", response.message.content[0].text, re.DOTALL)

    if match:
        dict_str = match.group(1)
        scores = ast.literal_eval(dict_str)
    else:
        scores = {}

    return response.message.content[0].text, scores

# Provides personalized feedback, suggesting ways to improve based on real-time analysis.
def generate_feedback(scenario, user_response, temperature):
    prompt = f"""
    Given the following negotiation scenario and user response, provide constructive feedback. Rate the user's tone, clarity, and negotiation tactics.

    Scenario: {scenario}
    User Response: {user_response}
    Feedback:"""
    
    response = co.chat(
        messages=[{"role": "user", "content": prompt}],
        model="command-r-plus-08-2024",
        temperature=temperature
    )
    return response.message.content

# Tracking function to save progress
def track_progress(user_id, feedback, scores):
    progress_data = {"user_id": user_id, "feedback": feedback, "scores": scores}
    with open("progress.json", "a") as f:
        json.dump(progress_data, f)
        f.write("\n")
    st.write("Your progress has been saved!")

# Streamlit App
st.title("🤝 AI Negotiation Simulator")

# Scenario settings
industry = st.selectbox("Choose Industry", ["Tech", "Real Estate", "Healthcare", "Finance"])
difficulty = st.selectbox("Choose Difficulty", ["Easy", "Intermediate", "Advanced"])
temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.6)

if st.button("Generate Scenario"):
    scenario = generate_negotiation_scenario(industry, difficulty, temperature)
    st.write("### Negotiation Scenario:")
    st.markdown(f"<div style='background-color:#000000;padding:10px;border-radius:5px;'>{scenario}</div>", unsafe_allow_html=True)

# User response input
user_response = st.text_area("Your Response", placeholder="Enter your negotiation response here...")

# Analyze and give feedback on the response
if st.button("Analyze Response"):
    feedback, scores = analyze_response(user_response, temperature)
    st.write("### Feedback:")
    st.markdown(f"<div style='background-color:#000000;padding:10px;border-radius:5px;'>{feedback}</div>", unsafe_allow_html=True)
    
    # Update dynamic negotiation stats based on scores
    st.sidebar.title("📊 Negotiation Stats")
    st.sidebar.write(f"Tone Quality: {scores['Tone']}%")
    st.sidebar.write(f"Clarity: {scores['Clarity']}%")
    st.sidebar.write(f"Negotiation Tactics: {scores['Negotiation Tactics']}%")
    
    # Track progress in a file
    track_progress(user_id="user_123", feedback=feedback, scores=scores)


