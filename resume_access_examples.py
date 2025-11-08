"""
Example: How to Access Resume Files
Demonstrates all methods to download and access resumes
"""
import requests
import os

API_BASE_URL = "http://localhost:8000"

def example_1_download_single_resume():
    """Example 1: Download a single resume by Application ID"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Download Single Resume")
    print("="*60)
    
    app_id = "APP-00001"
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/applications/{app_id}/resume")
        
        if response.status_code == 200:
            # Get filename from Content-Disposition header
            content_disposition = response.headers.get('Content-Disposition', '')
            filename = f"{app_id}_resume.pdf"
            
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            
            # Save the file
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Resume downloaded: {filename}")
            print(f"  Size: {len(response.content) / 1024:.1f} KB")
            print(f"  Type: {response.headers.get('Content-Type')}")
        else:
            print(f"✗ Failed: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
    
    except Exception as e:
        print(f"✗ Error: {e}")

def example_2_list_all_resumes():
    """Example 2: List all available resumes"""
    print("\n" + "="*60)
    print("EXAMPLE 2: List All Resumes")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/resumes")
        data = response.json()
        
        print(f"\nFound {data['total']} resume(s):\n")
        
        for resume in data['resumes']:
            status = "✓ Available" if resume['file_exists'] else "✗ Missing"
            size_kb = resume['file_size'] / 1024
            
            print(f"Application: {resume['application_id']}")
            print(f"  Applicant: {resume['applicant_name']}")
            print(f"  Position: {resume['position']}")
            print(f"  Filename: {resume['filename']}")
            print(f"  Size: {size_kb:.1f} KB")
            print(f"  Status: {status}")
            print(f"  Download URL: {API_BASE_URL}{resume['download_url']}")
            print()
    
    except Exception as e:
        print(f"✗ Error: {e}")

def example_3_download_all_resumes():
    """Example 3: Download all resumes to a directory"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Download All Resumes")
    print("="*60)
    
    output_dir = "downloaded_resumes"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Get list of all resumes
        response = requests.get(f"{API_BASE_URL}/api/resumes")
        data = response.json()
        
        print(f"\nDownloading {data['total']} resume(s) to '{output_dir}/'...\n")
        
        for resume in data['resumes']:
            if not resume['file_exists']:
                print(f"⚠️  Skipping {resume['application_id']} - file not found")
                continue
            
            app_id = resume['application_id']
            applicant = resume['applicant_name'].replace(' ', '_')
            filename = f"{app_id}_{applicant}_{resume['filename']}"
            filepath = os.path.join(output_dir, filename)
            
            # Download resume
            response = requests.get(f"{API_BASE_URL}/api/applications/{app_id}/resume")
            
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                size_kb = len(response.content) / 1024
                print(f"✓ {filename} ({size_kb:.1f} KB)")
            else:
                print(f"✗ Failed to download {app_id}")
        
        print(f"\n✓ All resumes downloaded to: {output_dir}/")
    
    except Exception as e:
        print(f"✗ Error: {e}")

def example_4_get_application_with_resume():
    """Example 4: Get application details including resume info"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Get Application with Resume Info")
    print("="*60)
    
    app_id = "APP-00001"
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/applications/{app_id}")
        
        if response.status_code == 200:
            app = response.json()
            
            print(f"\nApplication Details:")
            print(f"  ID: {app['application_id']}")
            print(f"  Name: {app['full_name']}")
            print(f"  Email: {app['email']}")
            print(f"  Position: {app['position']}")
            print(f"\nResume Information:")
            print(f"  Filename: {app['resume_filename']}")
            print(f"  File Path: {app.get('resume_path', 'N/A')}")
            print(f"  File Size: {app['resume_size'] / 1024:.1f} KB")
            print(f"  Download: {API_BASE_URL}/api/applications/{app_id}/resume")
        else:
            print(f"✗ Application not found: {app_id}")
    
    except Exception as e:
        print(f"✗ Error: {e}")

def example_5_browser_download():
    """Example 5: Open resume in browser"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Browser Download")
    print("="*60)
    
    app_id = "APP-00001"
    download_url = f"{API_BASE_URL}/api/applications/{app_id}/resume"
    
    print(f"\nTo download in browser, visit:")
    print(f"  {download_url}")
    print(f"\nOr click this link in the admin dashboard!")

def example_6_verify_resume_exists():
    """Example 6: Check if resume exists before downloading"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Verify Resume Exists")
    print("="*60)
    
    app_id = "APP-00001"
    
    try:
        # First, get application details
        response = requests.get(f"{API_BASE_URL}/api/applications/{app_id}")
        
        if response.status_code == 200:
            app = response.json()
            
            # Check if resume path exists
            has_resume = 'resume_path' in app and app['resume_path']
            
            print(f"\nApplication: {app_id}")
            print(f"  Has Resume: {'Yes' if has_resume else 'No'}")
            
            if has_resume:
                print(f"  Resume File: {app['resume_filename']}")
                print(f"  File Size: {app['resume_size'] / 1024:.1f} KB")
                print(f"  Path: {app['resume_path']}")
                
                # Now try to download
                print(f"\n  Downloading...")
                resume_response = requests.get(f"{API_BASE_URL}/api/applications/{app_id}/resume")
                
                if resume_response.status_code == 200:
                    print(f"  ✓ Download successful!")
                else:
                    print(f"  ✗ Download failed: {resume_response.status_code}")
        else:
            print(f"✗ Application not found: {app_id}")
    
    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("  RESUME ACCESS EXAMPLES")
    print("="*60)
    print("\nThis script demonstrates various ways to access resume files.")
    print("Make sure the server is running at http://localhost:8000")
    print("\nNote: Examples will fail if no applications have been submitted.")
    
    input("\nPress Enter to continue...")
    
    # Run all examples
    example_1_download_single_resume()
    example_2_list_all_resumes()
    example_3_download_all_resumes()
    example_4_get_application_with_resume()
    example_5_browser_download()
    example_6_verify_resume_exists()
    
    print("\n" + "="*60)
    print("  ALL EXAMPLES COMPLETE")
    print("="*60)
    print("\nQuick Reference:")
    print("  • API Endpoint: GET /api/applications/{app_id}/resume")
    print("  • List Resumes: GET /api/resumes")
    print("  • Admin Dashboard: admin_dashboard.html")
    print("  • CLI Tool: python storage_viewer.py")
    print("\nFor more details, see RESUME_ACCESS_GUIDE.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure:")
        print("  1. Server is running (python main.py)")
        print("  2. At least one application has been submitted")
        print("  3. API is accessible at http://localhost:8000")
