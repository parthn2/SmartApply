"""
Script to access and query the in-memory storage
"""
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

class StorageViewer:
    """Class to interact with in-memory storage"""
    
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
    
    def get_all_storage(self):
        """Get complete view of all in-memory storage"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/storage")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    
    def get_applications(self):
        """Get all job applications"""
        try:
            response = requests.get(f"{self.base_url}/api/applications")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    
    def get_application(self, app_id):
        """Get specific application by ID"""
        try:
            response = requests.get(f"{self.base_url}/api/applications/{app_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    
    def get_all_sessions(self):
        """Get all interview sessions"""
        try:
            response = requests.get(f"{self.base_url}/api/interview/sessions")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    
    def get_session(self, session_id):
        """Get specific interview session"""
        try:
            response = requests.get(f"{self.base_url}/api/interview/session/{session_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    
    def download_resume(self, app_id, save_path=None):
        """Download resume file for an application"""
        try:
            response = requests.get(f"{self.base_url}/api/applications/{app_id}/resume")
            response.raise_for_status()
            
            # Get filename from Content-Disposition header
            content_disposition = response.headers.get('Content-Disposition', '')
            filename = app_id + "_resume.pdf"  # default
            
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            
            if not save_path:
                save_path = filename
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Resume downloaded: {save_path}")
            return save_path
        except requests.exceptions.RequestException as e:
            print(f"Error downloading resume: {e}")
            return None
    
    def list_all_resumes(self):
        """List all resume files"""
        try:
            response = requests.get(f"{self.base_url}/api/resumes")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    
    def reset_storage(self):
        """Clear all in-memory storage"""
        try:
            response = requests.delete(f"{self.base_url}/api/admin/storage/reset")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    
    def print_summary(self):
        """Print a summary of all storage"""
        print("\n" + "="*60)
        print("  IN-MEMORY STORAGE SUMMARY")
        print("="*60)
        
        storage = self.get_all_storage()
        if not storage:
            print("Failed to retrieve storage data")
            return
        
        print(f"\n📊 Statistics:")
        print(f"  Total Applications: {storage['summary']['total_applications']}")
        print(f"  Total Interview Sessions: {storage['summary']['total_interview_sessions']}")
        print(f"  Completed Evaluations: {storage['summary']['applications_with_evaluations']}")
        
        # Applications
        if storage['applications']['count'] > 0:
            print(f"\n📄 Applications:")
            for app in storage['applications']['data']:
                print(f"  • {app['application_id']}: {app['full_name']} - {app['position']}")
        
        # Sessions
        if storage['interview_sessions']['count'] > 0:
            print(f"\n🎤 Interview Sessions:")
            for session_id, session in storage['interview_sessions']['data'].items():
                status = "✓ Evaluated" if 'evaluation' in session else "⏳ Pending"
                print(f"  • {session_id}: {session['position']} - {status}")
    
    def print_application_details(self, app_id):
        """Print detailed information about an application"""
        app = self.get_application(app_id)
        if not app:
            print(f"Application {app_id} not found")
            return
        
        print("\n" + "="*60)
        print(f"  APPLICATION DETAILS: {app_id}")
        print("="*60)
        
        print(f"\nFull Name: {app['full_name']}")
        print(f"Email: {app['email']}")
        print(f"Phone: {app['phone']}")
        print(f"Position: {app['position']}")
        print(f"Resume: {app['resume_filename']} ({app['resume_size']} bytes)")
        print(f"Submitted: {app['submitted_at']}")
        
        if app.get('cover_letter'):
            print(f"\nCover Letter:\n{app['cover_letter']}")
    
    def print_session_details(self, session_id):
        """Print detailed information about an interview session"""
        session = self.get_session(session_id)
        if not session:
            print(f"Session {session_id} not found")
            return
        
        print("\n" + "="*60)
        print(f"  INTERVIEW SESSION: {session_id}")
        print("="*60)
        
        print(f"\nPosition: {session['position']}")
        print(f"Difficulty: {session.get('difficulty', 'N/A')}")
        print(f"Created: {session.get('created_at', 'N/A')}")
        
        if 'questions' in session:
            print(f"\nQuestions ({len(session['questions'])}):")
            for q in session['questions']:
                print(f"  Q{q['question_id']}: {q['question']}")
                if 'category' in q:
                    print(f"    Category: {q['category']}")
        
        if 'evaluation' in session:
            eval_data = session['evaluation']
            print(f"\n📊 EVALUATION RESULTS:")
            print(f"  Overall Score: {eval_data['overall_score']}/100")
            print(f"  Recommendation: {eval_data['recommendation'].upper()}")
            print(f"\n  Summary: {eval_data['summary']}")
            
            print(f"\n  💪 Strengths:")
            for strength in eval_data['strengths']:
                print(f"    • {strength}")
            
            print(f"\n  📈 Areas for Improvement:")
            for area in eval_data['areas_for_improvement']:
                print(f"    • {area}")
            
            print(f"\n  📝 Question Scores:")
            for score in eval_data['detailed_scores']:
                print(f"    Q{score['question_id']}: {score['score']}/10")
                print(f"      {score['feedback']}")
    
    def export_to_json(self, filename="storage_export.json"):
        """Export all storage to a JSON file"""
        storage = self.get_all_storage()
        if not storage:
            print("Failed to retrieve storage data")
            return
        
        with open(filename, 'w') as f:
            json.dump(storage, f, indent=2)
        
        print(f"✓ Storage exported to {filename}")
    
    def search_applications(self, keyword):
        """Search applications by keyword"""
        storage = self.get_all_storage()
        if not storage:
            return []
        
        results = []
        keyword_lower = keyword.lower()
        
        for app in storage['applications']['data']:
            if (keyword_lower in app['full_name'].lower() or
                keyword_lower in app['email'].lower() or
                keyword_lower in app['position'].lower()):
                results.append(app)
        
        return results

def main():
    """Interactive menu to access storage"""
    viewer = StorageViewer()
    
    while True:
        print("\n" + "="*60)
        print("  IN-MEMORY STORAGE VIEWER")
        print("="*60)
        print("\nOptions:")
        print("  1. View Summary")
        print("  2. List All Applications")
        print("  3. View Application Details")
        print("  4. List All Interview Sessions")
        print("  5. View Session Details")
        print("  6. View Raw JSON (All Storage)")
        print("  7. Export to JSON File")
        print("  8. Search Applications")
        print("  9. List All Resumes")
        print(" 10. Download Resume")
        print(" 11. Reset Storage (Clear All)")
        print("  0. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "1":
            viewer.print_summary()
        
        elif choice == "2":
            apps = viewer.get_applications()
            if apps and apps['total'] > 0:
                print(f"\n📄 Applications ({apps['total']}):")
                for app in apps['applications']:
                    print(f"  {app['application_id']}: {app['full_name']} - {app['position']}")
            else:
                print("\nNo applications found.")
        
        elif choice == "3":
            app_id = input("Enter Application ID: ").strip()
            viewer.print_application_details(app_id)
        
        elif choice == "4":
            sessions = viewer.get_all_sessions()
            if sessions and sessions['total'] > 0:
                print(f"\n🎤 Interview Sessions ({sessions['total']}):")
                for session_id in sessions['sessions'].keys():
                    session = sessions['sessions'][session_id]
                    status = "✓ Evaluated" if 'evaluation' in session else "⏳ Pending"
                    print(f"  {session_id}: {session['position']} - {status}")
            else:
                print("\nNo interview sessions found.")
        
        elif choice == "5":
            session_id = input("Enter Session ID: ").strip()
            viewer.print_session_details(session_id)
        
        elif choice == "6":
            storage = viewer.get_all_storage()
            if storage:
                print("\n" + "="*60)
                print("  RAW JSON DATA")
                print("="*60)
                print(json.dumps(storage, indent=2))
        
        elif choice == "7":
            filename = input("Enter filename (default: storage_export.json): ").strip()
            if not filename:
                filename = "storage_export.json"
            viewer.export_to_json(filename)
        
        elif choice == "8":
            keyword = input("Enter search keyword: ").strip()
            results = viewer.search_applications(keyword)
            if results:
                print(f"\n🔍 Found {len(results)} matching applications:")
                for app in results:
                    print(f"  {app['application_id']}: {app['full_name']} - {app['position']}")
            else:
                print("\nNo matching applications found.")
        
        elif choice == "9":
            resumes = viewer.list_all_resumes()
            if resumes and resumes['total'] > 0:
                print(f"\n📎 Resumes ({resumes['total']}):")
                for resume in resumes['resumes']:
                    status = "✓ Available" if resume['file_exists'] else "✗ Missing"
                    size_kb = resume['file_size'] / 1024
                    print(f"  {resume['application_id']}: {resume['applicant_name']}")
                    print(f"    File: {resume['filename']} ({size_kb:.1f} KB) - {status}")
            else:
                print("\nNo resumes found.")
        
        elif choice == "10":
            app_id = input("Enter Application ID: ").strip()
            save_path = input("Save as (press Enter for default): ").strip()
            if not save_path:
                save_path = None
            viewer.download_resume(app_id, save_path)
        
        elif choice == "11":
            confirm = input("Are you sure you want to clear all storage? (yes/no): ")
            if confirm.lower() == "yes":
                result = viewer.reset_storage()
                if result:
                    print(f"\n✓ Storage cleared!")
                    print(f"  Applications removed: {result['cleared']['applications']}")
                    print(f"  Sessions removed: {result['cleared']['sessions']}")
        
        elif choice == "0":
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
