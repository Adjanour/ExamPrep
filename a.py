
import json
import ollama
from logger import CustomLogger

logger = CustomLogger(log_file="logs/a.log")

def categorize_question(question):
    prompt = f"""
    Categorize the following AWS exam question into one of these categories: 
    Cloud Concepts, Security and Compliance, Technology, Billing and Pricing.
    
    The response should be a valid JSON object with a "category" field, like so:
    {{
        "category": "<Category Name>"
    }}

    Question: {question['question_text']}
    """
    
    try:
        # Send the prompt to the Ollama model
        response = ollama.chat(model="llama3.2:1b", messages=[{"role": "user", "content": prompt}])
        logger.info(f"Response: {response}")

        # Parse the response as JSON
        response_json = json.loads(dict(response)["message"]["content"])
        # Extract the category from the JSON response
        category = response_json.get("category", "Uncategorized")
        
        return category
    except Exception as e:
        logger.error(f"Error categorizing question: {e}")
        return "Uncategorized"

def save_to_json(data, output_path):
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
        
categorized_questions = []
combined_questions = ""
with open ("questions.json","r") as f:
    data = json.load(f)
    combined_questions = data
    
for question in combined_questions:
    if not question["question_text"]:
        continue
    category = categorize_question(question)
    question["category"] = category
    categorized_questions.append(question)

# Save categorized questions to a new JSON file
categorized_output_path = "categorized_questions.json"
with open(categorized_output_path, 'w') as f:
    json.dump(categorized_questions, f, indent=4)