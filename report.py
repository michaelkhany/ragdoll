import streamlit as st
import base64
import warnings
import numpy as np
import json
from core.rag_compliance import analyze_compliance
import pandas as pd
import re
import requests



def format_dict(data):
    return [f"Question: {entry['Question']}  Answer: {entry['Answer']}" for entry in data.values()]
    #Question: {entry['Question']}

def get_summary(content, retries=3):
    prompt = (
        f"Analyze the following content and sumurize it in a paragraph"   
        f"Do not mention the lenght of the content\n\n"
        f"Content: {content}\n\n"
    )
    data = {
        "access_id": "trial_version",
        "service_name": "meta_llama70b",
        "query": prompt
    }

    for attempt in range(retries):
        try:
            response = requests.post(
                "https://synchange.com/sync.php",
                headers={"Content-Type": "application/json"},
                data=json.dumps(data),
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("response", "No valid response from API")
            else:
                logging.error(f"API returned status code {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"API call attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                logging.info("Retrying API call...")
    return "Error: API call failed after multiple attempts"


def show_results():
        output = ""
        query = "\n".join(entry.strip() for entry in format_dict(st.session_state.QA))
        if not query:
            return

        # Call RAG Compliance
        try:
            #st.write("Processing...\n")

            # Debug: Ensure the query being sent is correct
            print(f"Query Sent to Backend:\n{query}\n")

            results = analyze_compliance(query, documents_directory="core/documents", top_k=5)

            # Debug: Ensure results are received from the backend
            print(f"Results from Backend:\n{results}\n")

            if not results:
                print("No results returned from the analysis.")
                return

            if "error" in results:
                print(results["error"])
                return

            for doc, res in results.items():
                output += f"Article: {doc}\nResult: {res}\n\n"

            #st.write(output)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        return output




def extract_non_compliant_entries(text_output):
    entries = text_output.lower().strip().split("\n\n")
    data = []
    text_results = ""
    for entry in entries:
        if "does not comply" in entry:
            lines = entry.split("\n")
            doc_name = lines[0].split(": ")[1].strip().title().split(".")[0]
            compliance = "Does Not Comply"
            reason_match = re.search(r'"reason": "(.*?)"', entry)
            reason = reason_match.group(1).title() if reason_match else "Reason Not Found"
            text_output = f"Document: {doc_name}\nCompliance: {compliance}\nReason: {reason}"
            text_results += text_output + "\n\n"	
            data.append([doc_name, compliance, reason])

    
    df = pd.DataFrame(data, columns=["Document", "Compliance", "Reason"])
    return df, text_results

















def save_json():
    with open('Data/answers.json', 'w') as f:
        json.dump(st.session_state.QA, f, indent=4)

def display_risk(risk_level):
    risk_levels= [
    "unacceptable",
    "high",
    "limited",
    "minimal"
    ]
    risk_level= risk_level.lower()
    switch
    #st.success('Minimal Risk', icon="✅")
    #st.warning('Limited Risk', icon="⚠️")
    #st.error('High Risk', icon="❌")
    #st.error('Unacceptable Risk', icon="❌")
    
