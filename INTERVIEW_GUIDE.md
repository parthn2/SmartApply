# Interview Q&A Feature Documentation

## Overview

The Interview Q&A feature allows you to:
1. Generate interview questions using Gemini AI based on position and difficulty
2. Collect candidate answers
3. Evaluate answers automatically using Gemini AI
4. Receive detailed feedback and scoring

## Setup

### 1. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure the Backend

Update `main.py` with your Gemini API key:

```python
GEMINI_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
```

Or use environment variables (recommended):

```bash
# In .env file
GEMINI_API_KEY=your_actual_api_key_here
```

## API Endpoints

### 1. Generate Interview Questions

**POST** `/api/interview/generate-questions`

Generate customized interview questions based on position and requirements.

**Request Body:**
```json
{
  "position": "Software Engineer",
  "num_questions": 5,
  "difficulty": "medium",
  "categories": ["technical", "behavioral"]
}
```

**Parameters:**
- `position` (required): Job position
- `num_questions` (required): Number of questions to generate (1-10)
- `difficulty` (optional): "easy", "medium", or "hard" (default: "medium")
- `categories` (optional): Array of question types (default: ["technical", "behavioral", "situational"])

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/api/interview/generate-questions" \
  -H "Content-Type: application/json" \
  -d '{
    "position": "Software Engineer",
    "num_questions": 5,
    "difficulty": "medium"
  }'
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/api/interview/generate-questions"

data = {
    "position": "Software Engineer",
    "num_questions": 5,
    "difficulty": "medium",
    "categories": ["technical", "behavioral"]
}

response = requests.post(url, json=data)
result = response.json()

print(f"Session ID: {result['session_id']}")
for q in result['questions']:
    print(f"Q{q['question_id']}: {q['question']}")
```

**Response:**
```json
{
  "session_id": "SESSION-00001",
  "position": "Software Engineer",
  "questions": [
    {
      "question_id": 1,
      "question": "Explain the difference between REST and GraphQL APIs.",
      "category": "technical"
    },
    {
      "question_id": 2,
      "question": "Describe a time when you had to debug a complex issue.",
      "category": "behavioral"
    }
  ]
}
```

### 2. Evaluate Interview Answers

**POST** `/api/interview/evaluate`

Submit answers and receive AI-powered evaluation.

**Request Body:**
```json
{
  "application_id": "APP-00001",
  "position": "Software Engineer",
  "answers": [
    {
      "question_id": 1,
      "question": "Explain the difference between REST and GraphQL APIs.",
      "answer": "REST is an architectural style that uses standard HTTP methods..."
    }
  ]
}
```

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/api/interview/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-00001",
    "position": "Software Engineer",
    "answers": [
      {
        "question_id": 1,
        "question": "Explain REST vs GraphQL",
        "answer": "REST uses multiple endpoints while GraphQL uses a single endpoint..."
      }
    ]
  }'
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/api/interview/evaluate"

submission = {
    "application_id": "APP-00001",
    "position": "Software Engineer",
    "answers": [
        {
            "question_id": 1,
            "question": "Explain the difference between REST and GraphQL APIs.",
            "answer": "REST is an architectural style that uses standard HTTP methods and multiple endpoints. GraphQL uses a single endpoint and allows clients to request exactly what they need..."
        },
        {
            "question_id": 2,
            "question": "Describe a time when you debugged a complex issue.",
            "answer": "In my previous role, I encountered a race condition in our payment processing system..."
        }
    ]
}

response = requests.post(url, json=submission)
evaluation = response.json()

print(f"Overall Score: {evaluation['overall_score']}")
print(f"Recommendation: {evaluation['recommendation']}")
print(f"\nStrengths:")
for strength in evaluation['strengths']:
    print(f"  - {strength}")
```

**Response:**
```json
{
  "application_id": "APP-00001",
  "overall_score": 75.5,
  "detailed_scores": [
    {
      "question_id": 1,
      "score": 8.0,
      "feedback": "Strong technical understanding demonstrated. Good comparison of REST and GraphQL architectures."
    },
    {
      "question_id": 2,
      "score": 7.0,
      "feedback": "Good problem-solving approach. Could provide more details about the debugging process."
    }
  ],
  "strengths": [
    "Strong technical knowledge of API architectures",
    "Clear communication skills",
    "Practical debugging experience"
  ],
  "areas_for_improvement": [
    "Could elaborate more on edge cases",
    "Add more specific examples from past work"
  ],
  "recommendation": "hire",
  "summary": "Candidate shows solid technical foundation and problem-solving abilities. Communication is clear and concise. Recommended for next interview round."
}
```

### 3. Get Interview Session

**GET** `/api/interview/session/{session_id}`

Retrieve interview session details.

**Example:**
```bash
curl http://localhost:8000/api/interview/session/SESSION-00001
```

**Response:**
```json
{
  "position": "Software Engineer",
  "difficulty": "medium",
  "questions": [...],
  "created_at": "2025-11-08T10:30:00.123456",
  "evaluation": {...}
}
```

### 4. Get All Sessions

**GET** `/api/interview/sessions`

Get all interview sessions (admin endpoint).

**Example:**
```bash
curl http://localhost:8000/api/interview/sessions
```

## Complete Workflow Example

### Step 1: Submit Job Application
```python
import requests

# Submit application
url = "http://localhost:8000/api/job-application"

files = {'resume': open('resume.pdf', 'rb')}
data = {
    'full_name': 'John Doe',
    'email': 'john@example.com',
    'phone': '+1234567890',
    'position': 'Software Engineer',
    'cover_letter': 'I am interested in this position...'
}

response = requests.post(url, files=files, data=data)
application = response.json()
application_id = application['application_id']
print(f"Application ID: {application_id}")
```

### Step 2: Generate Interview Questions
```python
# Generate questions
url = "http://localhost:8000/api/interview/generate-questions"

data = {
    "position": "Software Engineer",
    "num_questions": 5,
    "difficulty": "medium"
}

response = requests.post(url, json=data)
interview = response.json()
session_id = interview['session_id']
questions = interview['questions']

print(f"\nInterview Questions (Session: {session_id}):")
for q in questions:
    print(f"{q['question_id']}. {q['question']}")
```

### Step 3: Collect and Submit Answers
```python
# Simulate candidate answering questions
answers = []
for q in questions:
    print(f"\n{q['question']}")
    answer = input("Your answer: ")
    answers.append({
        "question_id": q['question_id'],
        "question": q['question'],
        "answer": answer
    })

# Submit for evaluation
url = "http://localhost:8000/api/interview/evaluate"

submission = {
    "application_id": application_id,
    "position": "Software Engineer",
    "answers": answers
}

response = requests.post(url, json=submission)
evaluation = response.json()
```

### Step 4: Display Results
```python
print("\n" + "="*50)
print("INTERVIEW EVALUATION RESULTS")
print("="*50)
print(f"\nOverall Score: {evaluation['overall_score']}/100")
print(f"Recommendation: {evaluation['recommendation'].upper()}")
print(f"\nSummary: {evaluation['summary']}")

print("\nStrengths:")
for strength in evaluation['strengths']:
    print(f"  ✓ {strength}")

print("\nAreas for Improvement:")
for area in evaluation['areas_for_improvement']:
    print(f"  → {area}")

print("\nDetailed Scores:")
for score in evaluation['detailed_scores']:
    print(f"\nQuestion {score['question_id']}: {score['score']}/10")
    print(f"Feedback: {score['feedback']}")
```

## Using the Web Interface

1. **Open** `interview.html` in your browser
2. **Submit Application**: Fill out the job application form in the "Application" tab
3. **Generate Questions**: Go to "Interview" tab and generate questions
4. **Answer Questions**: Type your answers in the text areas
5. **Submit**: Click "Submit Interview Answers"
6. **View Results**: See detailed evaluation with scores and feedback

## Evaluation Criteria

The Gemini AI evaluates answers based on:

- **Technical Accuracy**: Correctness of technical concepts
- **Communication**: Clarity and structure of answers
- **Problem-Solving**: Logical approach and reasoning
- **Depth**: Level of detail and understanding
- **Relevance**: How well the answer addresses the question

## Scoring System

- **Overall Score**: 0-100 scale
- **Question Scores**: 0-10 scale per question
- **Recommendation**: hire / maybe / reject

### Score Interpretation
- **80-100**: Excellent - Strong hire recommendation
- **60-79**: Good - Positive recommendation
- **40-59**: Average - Conditional or "maybe"
- **0-39**: Below expectations - Not recommended

## Customization

### Custom Question Categories

Modify the categories in your request:

```python
data = {
    "position": "Data Scientist",
    "num_questions": 6,
    "difficulty": "hard",
    "categories": [
        "machine learning",
        "statistics",
        "coding",
        "data visualization"
    ]
}
```

### Custom Evaluation Criteria

Modify the evaluation prompt in `main.py` to add specific criteria:

```python
prompt = f"""Evaluate based on:
1. Technical depth (40%)
2. Communication clarity (30%)
3. Problem-solving approach (20%)
4. Cultural fit (10%)

Interview Answers:
{answers_text}
...
"""
```

## Best Practices

1. **Question Generation**:
   - Use 3-7 questions for optimal interview length
   - Mix technical and behavioral questions
   - Adjust difficulty based on role level

2. **Answer Collection**:
   - Give candidates adequate time to respond
   - Allow for follow-up questions if needed
   - Save answers immediately to prevent data loss

3. **Evaluation**:
   - Review AI evaluation as a guide, not absolute truth
   - Consider human review for final decisions
   - Look for patterns across multiple candidates

4. **Privacy**:
   - Store interview data securely
   - Implement proper access controls
   - Follow data retention policies

## Troubleshooting

### Common Issues

**Issue**: "Failed to generate questions"
- **Solution**: Check your Gemini API key is valid
- Ensure you have sufficient API quota

**Issue**: "Evaluation returns low scores for good answers"
- **Solution**: Questions may be too broad. Be more specific in question generation
- Consider adjusting difficulty level

**Issue**: "Response parsing error"
- **Solution**: Gemini sometimes returns markdown. The code handles this, but if issues persist, check the raw response

## Rate Limits

Gemini API free tier limits:
- 60 requests per minute
- Consider implementing rate limiting for production use

## Cost Considerations

- Gemini API is free for moderate use
- Each question generation: ~1 API call
- Each evaluation: ~1 API call
- Monitor usage at [Google AI Studio](https://makersuite.google.com/)

## Next Steps

1. Add authentication and authorization
2. Store interview data in database
3. Implement real-time progress tracking
4. Add video interview capabilities
5. Create recruiter dashboard
6. Generate interview reports
7. Integrate with ATS systems

## Support

For issues or questions:
- Check API documentation
- Review error messages in browser console
- Test with simple examples first
- Ensure all dependencies are installed
