# 🚀 Quick Start Guide - Job Application System with AI Interview

## Overview

This system provides:
1. **Job Application Submission** with resume upload
2. **AI-Powered Interview** with automatic question generation
3. **AI Evaluation** of candidate answers using Gemini
4. **Text-to-Speech** for question narration using ElevenLabs

## 📋 Prerequisites

- Python 3.8+
- Gemini API Key (free from Google AI Studio)
- ElevenLabs API Key (included in the code, or use your own)

## ⚡ Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

**Get Gemini API Key:**
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy your key

**Update main.py:**
```python
# Line 22 in main.py
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Replace with your actual key
```

**Optional: Use Environment Variables**
```bash
cp .env.example .env
# Edit .env file with your keys
```

### 3. Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 4. Access the Application

Open your browser and visit:
- **Interactive Docs**: http://localhost:8000/docs
- **Web Interface**: Open `interview.html` in your browser

## 🎯 Usage Workflows

### Workflow 1: Web Interface (Easiest)

1. Open `interview.html` in your browser
2. **Application Tab**: Submit job application with resume
3. **Interview Tab**: 
   - Generate questions (select position, number, difficulty)
   - Answer each question
   - Submit for evaluation
4. View detailed results with scores and feedback

### Workflow 2: Python Script (Automated)

```bash
python test_interview.py
```

This script demonstrates the complete workflow automatically.

### Workflow 3: API Calls (For Integration)

#### Submit Application
```bash
curl -X POST "http://localhost:8000/api/job-application" \
  -F "full_name=John Doe" \
  -F "email=john@example.com" \
  -F "phone=+1234567890" \
  -F "position=Software Engineer" \
  -F "resume=@resume.pdf"
```

#### Generate Questions
```bash
curl -X POST "http://localhost:8000/api/interview/generate-questions" \
  -H "Content-Type: application/json" \
  -d '{
    "position": "Software Engineer",
    "num_questions": 5,
    "difficulty": "medium"
  }'
```

#### Submit Answers for Evaluation
```bash
curl -X POST "http://localhost:8000/api/interview/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": "APP-00001",
    "position": "Software Engineer",
    "answers": [
      {
        "question_id": 1,
        "question": "Your question here",
        "answer": "Your answer here"
      }
    ]
  }'
```

## 📚 Available Endpoints

### Job Application
- `POST /api/job-application` - Submit application with resume
- `GET /api/applications` - Get all applications
- `GET /api/applications/{id}` - Get specific application

### Interview Q&A
- `POST /api/interview/generate-questions` - Generate interview questions
- `POST /api/interview/evaluate` - Evaluate candidate answers
- `GET /api/interview/session/{session_id}` - Get interview session
- `GET /api/interview/sessions` - Get all sessions

### Text-to-Speech
- `POST /api/text-to-speech` - Convert text to audio

## 🎨 Customization

### Adjust Question Difficulty
```python
# In web interface or API call
{
    "position": "Software Engineer",
    "num_questions": 7,
    "difficulty": "hard"  # easy, medium, hard
}
```

### Custom Question Categories
```python
{
    "position": "Data Scientist",
    "num_questions": 6,
    "categories": ["machine learning", "statistics", "coding"]
}
```

### Change Evaluation Criteria
Edit the evaluation prompt in `main.py` around line 170 to customize scoring criteria.

## 📊 Understanding Results

### Overall Score
- **80-100**: Excellent candidate - Strong hire
- **60-79**: Good candidate - Recommended
- **40-59**: Average - Consider for next round
- **0-39**: Below expectations

### Detailed Feedback
- **Strengths**: What the candidate did well
- **Areas for Improvement**: Constructive feedback
- **Question Scores**: 0-10 per question
- **Recommendation**: hire / maybe / reject

## 🔧 Troubleshooting

### "Module not found" Error
```bash
pip install -r requirements.txt --break-system-packages
```

### "Invalid API Key" Error
- Verify your Gemini API key is correct
- Check you've activated the API at Google AI Studio
- Ensure no extra spaces in the key

### "Port already in use"
```bash
# Change port in main.py (last line)
uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed from 8000
```

### Questions Not Generating
- Check internet connection
- Verify Gemini API quota hasn't been exceeded
- Try with fewer questions first (num_questions: 3)

### Evaluation Taking Too Long
- This is normal - AI evaluation takes 10-30 seconds
- Reduce number of questions for faster processing
- Check network connection

## 🎓 Examples

### Example 1: Technical Interview
```python
import requests

# Generate technical questions
response = requests.post("http://localhost:8000/api/interview/generate-questions", 
    json={
        "position": "Backend Developer",
        "num_questions": 5,
        "difficulty": "hard",
        "categories": ["system design", "databases", "algorithms"]
    })

questions = response.json()['questions']
```

### Example 2: Behavioral Interview
```python
# Generate behavioral questions
response = requests.post("http://localhost:8000/api/interview/generate-questions", 
    json={
        "position": "Product Manager",
        "num_questions": 4,
        "difficulty": "medium",
        "categories": ["leadership", "communication", "product strategy"]
    })
```

### Example 3: Mixed Interview
```python
# Generate mixed questions
response = requests.post("http://localhost:8000/api/interview/generate-questions", 
    json={
        "position": "Full Stack Developer",
        "num_questions": 6,
        "difficulty": "medium",
        "categories": ["technical", "behavioral", "problem-solving"]
    })
```

## 🔐 Security Notes (For Production)

⚠️ This is a development setup. For production:

1. **Add Authentication**: Implement JWT or OAuth
2. **Secure API Keys**: Use environment variables
3. **Add Rate Limiting**: Prevent API abuse
4. **Use HTTPS**: Enable SSL/TLS
5. **Database**: Replace in-memory storage with PostgreSQL/MongoDB
6. **File Storage**: Use AWS S3 or similar
7. **Input Validation**: Enhanced validation and sanitization
8. **CORS**: Restrict to specific domains

## 📖 Further Reading

- **Full Documentation**: See `README.md`
- **Interview Guide**: See `INTERVIEW_GUIDE.md`
- **API Docs**: http://localhost:8000/docs (when server is running)

## 💡 Tips for Best Results

1. **Question Generation**:
   - Use 3-7 questions for optimal interview length
   - Mix different question types
   - Match difficulty to role level

2. **Answer Collection**:
   - Encourage detailed, specific answers
   - Provide examples when possible
   - Take time to think through responses

3. **Evaluation**:
   - Use as guidance, not absolute truth
   - Combine with human review for final decisions
   - Look for consistent patterns

## 🆘 Getting Help

1. Check the error message in terminal/console
2. Review the documentation
3. Test with the example script first
4. Verify API keys are correct
5. Check API quotas haven't been exceeded

## 🎉 Success Checklist

- [ ] Installed dependencies
- [ ] Configured Gemini API key
- [ ] Server starts without errors
- [ ] Can access http://localhost:8000/docs
- [ ] Can submit job application
- [ ] Can generate interview questions
- [ ] Can submit and evaluate answers
- [ ] Receive evaluation results

## Next Steps

Once everything works:
1. Customize questions for your needs
2. Adjust evaluation criteria
3. Integrate with your existing systems
4. Add more features (video, scheduling, etc.)
5. Deploy to production with proper security

---

**Ready to start?** Run `python main.py` and open `interview.html`! 🚀
