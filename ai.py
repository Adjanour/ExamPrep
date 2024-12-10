import pdfplumber
import json
import re
import ollama
from logger import CustomLogger

logger = CustomLogger(log_file="logs/app.log")

# AWS CLF-C02 Exam areas (unchanged)
categories = {
    "Cloud Concepts": "Questions about basic cloud concepts, benefits of cloud, and AWS Cloud architecture.",
    "Security and Compliance": "Questions about AWS security services, compliance, and the shared responsibility model.",
    "Technology": "Questions about core AWS services such as compute, storage, database, networking, etc.",
    "Billing and Pricing": "Questions related to cost management, pricing models, and billing resources in AWS."
}

def extract_question_data(text):
    # Define regex patterns
    question_number_pattern = re.compile(r"Question (\d+)")
    question_type_pattern = re.compile(r"Question Type: (.+)")
    options_pattern = re.compile(r"Options:\n((?:.|\n)+?)\nAnswer:")
    answer_pattern = re.compile(r"Answer:\n([A-Z])")
    explanation_pattern = re.compile(r"Explanation:\n((?:.|\n)+)")

    # Initialize variables
    question_number = question_type = question_text = answer = explanation = None
    options = []

    try:
        question_number = question_number_pattern.search(text).group(1)
    except AttributeError:
        logger.warning("Question number not found")

    try:
        question_type = question_type_pattern.search(text).group(1)
    except AttributeError:
        logger.warning("Question type not found")

    try:
        options_match = options_pattern.search(text)
        options = options_match.group(1).strip().split('\n')
        options = [opt.strip() for opt in options]
    except AttributeError:
        logger.warning("Options not found")

    try:
        answer = answer_pattern.search(text).group(1)
    except AttributeError:
        logger.warning("Answer not found")

    try:
        explanation = explanation_pattern.search(text).group(1).strip()
    except AttributeError:
        logger.warning("Explanation not found")

    try:
        question_text_pattern = re.compile(r"Question Type: .+\n((?:.|\n)+?)\nOptions:")
        question_text = question_text_pattern.search(text).group(1).strip()
    except AttributeError:
        logger.warning("Question text not found")

    # Return as a dictionary
    return {
        "question_number": question_number,
        "question_type": question_type,
        "question_text": question_text,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }

def split_text_into_questions(text):
    # Regex to split text by Question X or any indicator that marks the start of a question
    question_split_pattern = re.compile(r"(Question \d+)")
    
    # Split the text by this pattern
    questions_raw = question_split_pattern.split(text)

    # Remove empty strings and process each question chunk
    questions_raw = [q.strip() for q in questions_raw if q.strip()]
    
    # Reconstruct questions with their numbers (Question 1, Question 2, etc.)
    questions = []
    for i in range(0, len(questions_raw), 2):
        question_number = questions_raw[i]
        question_text = questions_raw[i + 1] if i + 1 < len(questions_raw) else ''
        questions.append(question_number + "\n" + question_text)

    return questions

def extract_questions_from_pdf(pdf_path):
    questions = []  # List to store parsed questions
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                try:
                    # Split the text into multiple questions
                    questions_on_page = split_text_into_questions(text)
                    for question_text in questions_on_page:
                        question_data = extract_question_data(question_text)
                        questions.append(question_data)
                        logger.info(question_text)
                        logger.info(question_data)
                except Exception as e:
                    logger.error(f"Failed to process page: {e}")
    return questions

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

# List of PDF files to process
pdf_files = [
    "aws (2).pdf", "aws (3).pdf", "aws (4).pdf", "aws (5).pdf", "aws (6).pdf"
]

combined_questions = []

# Extract questions from each PDF file
for pdf_file in pdf_files:
    try:
        questions = extract_questions_from_pdf(pdf_file)
        combined_questions.extend(questions)
        logger.info(f"Extracted {len(questions)} questions from {pdf_file}")
    except Exception as e:
        logger.error(f"Failed to process {pdf_file}: {e}")
save_to_json(combined_questions, "combined_questions.json")

# Categorize each question
categorized_questions = []
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

logger.info(f"Categorized questions saved to {categorized_output_path}")
print(f"Categorized questions saved to {categorized_output_path}")
