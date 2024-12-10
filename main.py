import pdfplumber
import json
import re

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
        print("Question number not found")

    try:
        question_type = question_type_pattern.search(text).group(1)
    except AttributeError:
        print("Question type not found")

    try:
        options_match = options_pattern.search(text)
        options = options_match.group(1).strip().split('\n')
        options = [opt.strip() for opt in options]
    except AttributeError:
        print("Options not found")

    try:
        answer = answer_pattern.search(text).group(1)
    except AttributeError:
        print("Answer not found")

    try:
        explanation = explanation_pattern.search(text).group(1).strip()
    except AttributeError:
        print("Explanation not found")

    try:
        question_text_pattern = re.compile(r"Question Type: .+\n((?:.|\n)+?)\nOptions:")
        question_text = question_text_pattern.search(text).group(1).strip()
    except AttributeError:
        print("Question text not found")

    # Return as a dictionary
    return {
        "question_number": question_number,
        "question_type": question_type,
        "question_text": question_text,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }

def extract_questions_from_pdf(pdf_path):
    questions = []  # List to store parsed questions
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                try:
                    question_data = extract_question_data(text)
                    questions.append(question_data)
                except Exception as e:
                    print(f"Failed to process page: {e}")
    return questions

def save_to_json(data, output_path):
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

# Example usage
pdf_path = "aws_questions.pdf"  # Replace with your file path
output_path = "questions.json"

try:
    questions = extract_questions_from_pdf(pdf_path)
    save_to_json(questions, output_path)
    print(f"Extracted {len(questions)} questions saved to {output_path}")
except Exception as e:
    print(f"An error occurred: {e}")
