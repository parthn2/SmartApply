from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
import requests
import io
import os
from datetime import datetime
import google.generativeai as genai
import json
from dotenv import load_dotenv
load_dotenv()


app = FastAPI(title="Job Application API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Pydantic Models
class TextToSpeechRequest(BaseModel):
    text: str
    voice_id: Optional[str] = "pNInz6obpgDQGcFmaJgB"
    stability: Optional[float] = 0.5
    similarity_boost: Optional[float] = 0.7

class JobApplicationResponse(BaseModel):
    message: str
    application_id: str
    submitted_at: str

class InterviewQuestion(BaseModel):
    question_id: int
    question: str
    category: Optional[str] = None

class GenerateQuestionsRequest(BaseModel):
    position: str
    num_questions: int
    difficulty: Optional[str] = "medium"  # easy, medium, hard
    categories: Optional[List[str]] = None  # e.g., ["technical", "behavioral", "situational"]

class QuestionAnswer(BaseModel):
    question_id: int
    question: str
    answer: str

class InterviewSubmission(BaseModel):
    application_id: str
    position: str
    answers: List[QuestionAnswer]

class EvaluationResponse(BaseModel):
    application_id: str
    overall_score: float
    detailed_scores: List[Dict]
    strengths: List[str]
    areas_for_improvement: List[str]
    recommendation: str
    summary: str

# In-memory storage (replace with database in production)
job_applications = []
interview_sessions = {}  # Store interview questions and answers

@app.get("/")
async def root():
    return {
        "message": "Job Application API",
        "endpoints": {
            "POST /api/job-application": "Submit job application with resume",
            "POST /api/text-to-speech": "Convert text to speech audio",
            "GET /api/applications": "Get all applications (admin)"
        }
    }

@app.post("/api/job-application", response_model=JobApplicationResponse)
async def submit_job_application(
    full_name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    cover_letter: Optional[str] = Form(None),
    resume: UploadFile = File(...)
):
    """
    Submit a job application with resume attachment
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_extension = os.path.splitext(resume.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Read resume content
        resume_content = await resume.read()
        
        # Generate application ID
        application_id = f"APP-{len(job_applications) + 1:05d}"
        submission_time = datetime.now().isoformat()
        
        # Create resumes directory if it doesn't exist
        resume_dir = "/tmp/resumes"
        os.makedirs(resume_dir, exist_ok=True)
        
        # Save resume file to disk with application ID in filename
        safe_filename = f"{application_id}_{resume.filename}"
        resume_path = os.path.join(resume_dir, safe_filename)
        
        with open(resume_path, "wb") as f:
            f.write(resume_content)
        
        # Store application data
        application_data = {
            "application_id": application_id,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "position": position,
            "cover_letter": cover_letter,
            "resume_filename": resume.filename,
            "resume_path": resume_path,
            "resume_size": len(resume_content),
            "submitted_at": submission_time
        }
        
        job_applications.append(application_data)
        
        return JobApplicationResponse(
            message="Application submitted successfully",
            application_id=application_id,
            submitted_at=submission_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech using ElevenLabs API
    Returns audio file stream
    """
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{request.voice_id}"
        
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": request.text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": request.stability,
                "similarity_boost": request.similarity_boost
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            # Return audio as streaming response
            audio_stream = io.BytesIO(response.content)
            return StreamingResponse(
                audio_stream,
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": "attachment; filename=speech.mp3"
                }
            )
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"ElevenLabs API error: {response.text}"
            )
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/applications")
async def get_applications():
    """
    Get all job applications (Admin endpoint - add authentication in production)
    """
    return {
        "total": len(job_applications),
        "applications": job_applications
    }

@app.get("/api/applications/{application_id}")
async def get_application(application_id: str):
    """
    Get specific application by ID
    """
    application = next(
        (app for app in job_applications if app["application_id"] == application_id),
        None
    )
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return application

@app.get("/api/applications/{application_id}/resume")
async def download_resume(application_id: str):
    """
    Download the resume file for a specific application
    """
    application = next(
        (app for app in job_applications if app["application_id"] == application_id),
        None
    )
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    resume_path = application.get("resume_path")
    
    if not resume_path or not os.path.exists(resume_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
    
    # Determine media type based on file extension
    file_extension = os.path.splitext(resume_path)[1].lower()
    media_types = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    media_type = media_types.get(file_extension, 'application/octet-stream')
    
    # Read and return the file
    with open(resume_path, "rb") as f:
        resume_content = f.read()
    
    return StreamingResponse(
        io.BytesIO(resume_content),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={application['resume_filename']}"
        }
    )

@app.get("/api/resumes")
async def list_all_resumes():
    """
    List all resume files with download links
    """
    resumes = []
    
    for app in job_applications:
        resume_path = app.get("resume_path")
        file_exists = resume_path and os.path.exists(resume_path)
        
        resumes.append({
            "application_id": app["application_id"],
            "applicant_name": app["full_name"],
            "position": app["position"],
            "filename": app["resume_filename"],
            "file_size": app["resume_size"],
            "file_exists": file_exists,
            "download_url": f"/api/applications/{app['application_id']}/resume" if file_exists else None,
            "submitted_at": app["submitted_at"]
        })
    
    return {
        "total": len(resumes),
        "resumes": resumes
    }

@app.post("/api/interview/generate-questions")
async def generate_interview_questions(request: GenerateQuestionsRequest):
    """
    Generate interview questions using Gemini API based on position and requirements
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        
        # Build prompt for question generation
        categories_str = ", ".join(request.categories) if request.categories else "technical, behavioral, and situational"
        
        prompt = f"""Generate exactly {request.num_questions} interview questions for a {request.position} position.

Difficulty level: {request.difficulty}
Question categories: {categories_str}

Requirements:
1. Generate diverse questions covering different aspects of the role
2. Include a mix of: {categories_str}
3. Questions should be clear, professional, and relevant to {request.position}
4. Difficulty should be {request.difficulty}

Return the response in the following JSON format ONLY (no markdown, no extra text):
{{
    "questions": [
        {{
            "question_id": 1,
            "question": "Question text here",
            "category": "technical/behavioral/situational"
        }}
    ]
}}
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        questions_data = json.loads(response_text)
        
        # Create session ID
        session_id = f"SESSION-{len(interview_sessions) + 1:05d}"
        
        # Store questions in session
        interview_sessions[session_id] = {
            "position": request.position,
            "difficulty": request.difficulty,
            "questions": questions_data["questions"],
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "session_id": session_id,
            "position": request.position,
            "questions": questions_data["questions"]
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse Gemini response: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

@app.post("/api/interview/evaluate", response_model=EvaluationResponse)
async def evaluate_interview_answers(submission: InterviewSubmission):
    """
    Evaluate interview answers using Gemini API
    Returns detailed evaluation with scores and feedback
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Build evaluation prompt
        answers_text = "\n\n".join([
            f"Q{ans.question_id}: {ans.question}\nAnswer: {ans.answer}"
            for ans in submission.answers
        ])
        
        prompt = f"""You are an expert technical interviewer evaluating a candidate for a {submission.position} position.

Interview Answers:
{answers_text}

Please provide a comprehensive evaluation in the following JSON format ONLY (no markdown, no extra text):
{{
    "overall_score": 0.0,
    "detailed_scores": [
        {{
            "question_id": 1,
            "score": 0.0,
            "feedback": "Specific feedback for this answer"
        }}
    ],
    "strengths": ["List key strengths demonstrated"],
    "areas_for_improvement": ["List areas that need improvement"],
    "recommendation": "hire/maybe/reject with brief explanation",
    "summary": "Brief overall assessment of the candidate"
}}

Scoring Guidelines:
- overall_score: 0-100 scale
- question scores: 0-10 scale
- Be fair, objective, and constructive
- Consider technical accuracy, communication skills, problem-solving approach
- Provide specific, actionable feedback
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        evaluation_data = json.loads(response_text)
        
        # Store evaluation results
        if submission.application_id not in interview_sessions:
            interview_sessions[submission.application_id] = {}
        
        interview_sessions[submission.application_id]["evaluation"] = {
            **evaluation_data,
            "evaluated_at": datetime.now().isoformat()
        }
        
        return EvaluationResponse(
            application_id=submission.application_id,
            **evaluation_data
        )
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse evaluation response: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answers: {str(e)}")

@app.get("/api/interview/session/{session_id}")
async def get_interview_session(session_id: str):
    """
    Get interview session details including questions and evaluation if available
    """
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    return interview_sessions[session_id]

@app.get("/api/interview/sessions")
async def get_all_sessions():
    """
    Get all interview sessions (Admin endpoint)
    """
    return {
        "total": len(interview_sessions),
        "sessions": interview_sessions
    }

@app.get("/api/admin/storage")
async def get_all_storage():
    """
    Admin endpoint: Get complete view of all in-memory storage
    """
    return {
        "applications": {
            "count": len(job_applications),
            "data": job_applications
        },
        "interview_sessions": {
            "count": len(interview_sessions),
            "data": interview_sessions
        },
        "summary": {
            "total_applications": len(job_applications),
            "total_interview_sessions": len(interview_sessions),
            "applications_with_evaluations": sum(
                1 for session in interview_sessions.values() 
                if isinstance(session, dict) and "evaluation" in session
            )
        }
    }

@app.delete("/api/admin/storage/reset")
async def reset_storage():
    """
    Admin endpoint: Clear all in-memory storage (useful for testing)
    """
    global job_applications, interview_sessions
    
    old_app_count = len(job_applications)
    old_session_count = len(interview_sessions)
    
    job_applications.clear()
    interview_sessions.clear()
    
    return {
        "message": "Storage reset successfully",
        "cleared": {
            "applications": old_app_count,
            "sessions": old_session_count
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
