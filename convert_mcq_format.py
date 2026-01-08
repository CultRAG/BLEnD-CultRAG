import csv
import json
import re

def extract_question(prompt):
    """Extract the main question from the prompt, removing instructions"""
    lines = prompt.strip().split('\n')
    question = lines[0].strip()
    return question

def convert_mcq_format(input_file, questions_output, answers_output):
    """
    Convert MCQ data from original format to two separate files:
    1. Questions file with id, question, and options
    2. Answers file with id and answer letter
    """

    questions_data = []
    answers_data = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            mcq_id = row['MCQID']

            # Extract question from prompt
            question = extract_question(row['prompt'])

            # Parse choices JSON
            choices = json.loads(row['choices'])

            # Get answer
            answer = row['answer_idx']

            # Prepare question row
            question_row = {
                'id': mcq_id,
                'question': question,
                'option_A': choices.get('A', ''),
                'option_B': choices.get('B', ''),
                'option_C': choices.get('C', ''),
                'option_D': choices.get('D', '')
            }
            questions_data.append(question_row)

            # Prepare answer row
            answer_row = {
                'id': mcq_id,
                'answer': answer
            }
            answers_data.append(answer_row)

    # Write questions file
    with open(questions_output, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['id', 'question', 'option_A', 'option_B', 'option_C', 'option_D']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(questions_data)

    # Write answers file
    with open(answers_output, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['id', 'answer']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(answers_data)

    return len(questions_data)

# Run the conversion
if __name__ == "__main__":
    input_file = 'new-data/mc_questions_file-1.tsv'  # Your input CSV file
    questions_output = 'questions.tsv'
    answers_output = 'answers.tsv'

    num_processed = convert_mcq_format(input_file, questions_output, answers_output)
    print(f"Successfully processed {num_processed} questions")
    print(f"Output files created: {questions_output}, {answers_output}")
