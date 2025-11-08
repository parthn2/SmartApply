"""
Example script demonstrating the complete interview workflow
"""
import requests
import json
from pathlib import Path

API_BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def submit_application():
    """Step 1: Submit a job application"""
    print_section("STEP 1: Submit Job Application")
    
    url = f"{API_BASE_URL}/api/job-application"
    
    # For this example, create a dummy resume file if it doesn't exist
    resume_path = "sample_resume.pdf"
    if not Path(resume_path).exists():
        with open(resume_path, "wb") as f:
            f.write(b"%PDF-1.4 Sample Resume Content")
        print(f"Created sample resume: {resume_path}")
    
    files = {'resume': open(resume_path, 'rb')}
    data = {
        'full_name': 'Jane Smith',
        'email': 'jane.smith@example.com',
        'phone': '+1-555-0123',
        'position': 'Software Engineer',
        'cover_letter': 'I am passionate about software development and have 5 years of experience...'
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Application submitted successfully!")
        print(f"  Application ID: {result['application_id']}")
        print(f"  Submitted at: {result['submitted_at']}")
        
        return result['application_id']
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Error submitting application: {e}")
        return None

def generate_questions(position="Software Engineer", num_questions=5):
    """Step 2: Generate interview questions"""
    print_section("STEP 2: Generate Interview Questions")
    
    url = f"{API_BASE_URL}/api/interview/generate-questions"
    
    data = {
        "position": position,
        "num_questions": num_questions,
        "difficulty": "medium",
        "categories": ["technical", "behavioral", "problem-solving"]
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Generated {len(result['questions'])} questions")
        print(f"  Session ID: {result['session_id']}")
        print(f"  Position: {result['position']}")
        print("\nQuestions:")
        
        for q in result['questions']:
            print(f"\n  Q{q['question_id']}: {q['question']}")
            if 'category' in q:
                print(f"      Category: {q['category']}")
        
        return result['session_id'], result['questions']
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Error generating questions: {e}")
        return None, None

def collect_answers(questions):
    """Step 3: Collect sample answers (simulated)"""
    print_section("STEP 3: Collect Answers")
    
    # Sample answers for demonstration
    sample_answers = [
        "REST is an architectural style that uses HTTP methods and multiple endpoints. GraphQL provides a single endpoint and allows clients to specify exactly what data they need. REST can lead to over-fetching or under-fetching data, while GraphQL solves this with its flexible query language.",
        
        "In my previous role, we had a production issue where API response times increased significantly. I used APM tools to identify the bottleneck was in database queries. I optimized the queries by adding proper indexes and implementing caching, which reduced response time by 70%.",
        
        "I have strong experience with Python, JavaScript, and Java. For Python, I've built backend services using FastAPI and Django. In JavaScript, I'm proficient with React and Node.js. I've also worked with cloud platforms like AWS and containerization using Docker.",
        
        "I believe in writing clean, maintainable code. I follow SOLID principles, write comprehensive tests, and conduct thorough code reviews. I also prioritize documentation and believe in continuous learning to stay updated with best practices.",
        
        "In a team project, we had tight deadlines and differing opinions on implementation. I organized a meeting where everyone could voice concerns, then we evaluated pros and cons objectively. We reached consensus by focusing on what would deliver the best user value within our timeline."
    ]
    
    answers = []
    for i, q in enumerate(questions):
        answer_text = sample_answers[i] if i < len(sample_answers) else "This is a sample answer demonstrating my skills and experience."
        
        answers.append({
            "question_id": q['question_id'],
            "question": q['question'],
            "answer": answer_text
        })
        
        print(f"\n  Q{q['question_id']}: {q['question']}")
        print(f"  A: {answer_text[:100]}..." if len(answer_text) > 100 else f"  A: {answer_text}")
    
    return answers

def submit_evaluation(application_id, position, answers):
    """Step 4: Submit answers for evaluation"""
    print_section("STEP 4: Submit for Evaluation")
    
    url = f"{API_BASE_URL}/api/interview/evaluate"
    
    submission = {
        "application_id": application_id,
        "position": position,
        "answers": answers
    }
    
    try:
        print("Submitting answers for AI evaluation...")
        response = requests.post(url, json=submission)
        response.raise_for_status()
        result = response.json()
        
        print("✓ Evaluation completed!")
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Error evaluating answers: {e}")
        return None

def display_results(evaluation):
    """Step 5: Display evaluation results"""
    print_section("STEP 5: Evaluation Results")
    
    # Overall Score
    print(f"\n📊 OVERALL SCORE: {evaluation['overall_score']:.1f}/100")
    
    # Score interpretation
    score = evaluation['overall_score']
    if score >= 80:
        rating = "EXCELLENT ⭐⭐⭐⭐⭐"
    elif score >= 60:
        rating = "GOOD ⭐⭐⭐⭐"
    elif score >= 40:
        rating = "AVERAGE ⭐⭐⭐"
    else:
        rating = "NEEDS IMPROVEMENT ⭐⭐"
    
    print(f"   Rating: {rating}")
    print(f"   Recommendation: {evaluation['recommendation'].upper()}")
    
    # Summary
    print(f"\n📝 SUMMARY:")
    print(f"   {evaluation['summary']}")
    
    # Strengths
    print(f"\n💪 STRENGTHS:")
    for i, strength in enumerate(evaluation['strengths'], 1):
        print(f"   {i}. {strength}")
    
    # Areas for Improvement
    print(f"\n📈 AREAS FOR IMPROVEMENT:")
    for i, area in enumerate(evaluation['areas_for_improvement'], 1):
        print(f"   {i}. {area}")
    
    # Detailed Scores
    print(f"\n📋 DETAILED QUESTION SCORES:")
    for score_detail in evaluation['detailed_scores']:
        score_val = score_detail['score']
        score_emoji = "🟢" if score_val >= 8 else "🟡" if score_val >= 6 else "🟠" if score_val >= 4 else "🔴"
        
        print(f"\n   {score_emoji} Question {score_detail['question_id']}: {score_val}/10")
        print(f"      {score_detail['feedback']}")

def main():
    """Run the complete interview workflow"""
    print("\n" + "="*60)
    print("  AUTOMATED INTERVIEW SYSTEM - DEMO")
    print("="*60)
    print("\nThis script demonstrates the complete interview workflow:")
    print("1. Submit job application")
    print("2. Generate interview questions using AI")
    print("3. Collect candidate answers")
    print("4. Evaluate answers using AI")
    print("5. Display detailed results")
    
    input("\nPress Enter to start...")
    
    # Step 1: Submit Application
    application_id = submit_application()
    if not application_id:
        print("\n✗ Failed to submit application. Exiting.")
        return
    
    # Step 2: Generate Questions
    session_id, questions = generate_questions("Software Engineer", 5)
    if not questions:
        print("\n✗ Failed to generate questions. Exiting.")
        return
    
    # Step 3: Collect Answers
    answers = collect_answers(questions)
    
    # Step 4: Submit for Evaluation
    evaluation = submit_evaluation(application_id, "Software Engineer", answers)
    if not evaluation:
        print("\n✗ Failed to evaluate answers. Exiting.")
        return
    
    # Step 5: Display Results
    display_results(evaluation)
    
    print_section("WORKFLOW COMPLETE")
    print("\n✓ All steps completed successfully!")
    print(f"✓ Application ID: {application_id}")
    print(f"✓ Session ID: {session_id}")
    print(f"\nYou can view the full results in the web interface at:")
    print(f"  http://localhost:8000/api/interview/session/{session_id}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Script interrupted by user.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
