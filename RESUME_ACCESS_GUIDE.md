# 📎 Resume File Access Guide

## Overview

Resumes are now **stored on disk** in the `/home/claude/resumes/` directory and can be accessed through multiple methods:

---

## 🗂️ Where Resumes Are Stored

### File System Location
```
/home/claude/resumes/
├── APP-00001_resume.pdf
├── APP-00002_John_Doe_CV.docx
└── APP-00003_resume.pdf
```

**Naming Convention:** `{APPLICATION_ID}_{ORIGINAL_FILENAME}`

---

## 🔍 Methods to Access Resumes

### Method 1: API Endpoints (Recommended)

#### Download Resume via API
```bash
# Download resume for application APP-00001
curl -O http://localhost:8000/api/applications/APP-00001/resume
```

#### List All Resumes
```bash
curl http://localhost:8000/api/resumes
```

**Response:**
```json
{
  "total": 2,
  "resumes": [
    {
      "application_id": "APP-00001",
      "applicant_name": "John Doe",
      "position": "Software Engineer",
      "filename": "resume.pdf",
      "file_size": 102400,
      "file_exists": true,
      "download_url": "/api/applications/APP-00001/resume",
      "submitted_at": "2025-11-08T10:30:00"
    }
  ]
}
```

#### Get Application with Resume Info
```bash
curl http://localhost:8000/api/applications/APP-00001
```

**Response includes:**
```json
{
  "application_id": "APP-00001",
  "full_name": "John Doe",
  "resume_filename": "resume.pdf",
  "resume_path": "/home/claude/resumes/APP-00001_resume.pdf",
  "resume_size": 102400,
  ...
}
```

---

### Method 2: Admin Dashboard (Web Interface)

1. **Open:** `admin_dashboard.html` in your browser
2. **View Applications:** See all applications in a table
3. **Download Resume:** Click the "📎 Resume" button next to any application
4. The resume will download automatically

**Features:**
- Visual interface
- One-click resume download
- View application details
- Real-time storage monitoring

---

### Method 3: Storage Viewer Script (Interactive CLI)

```bash
python storage_viewer.py
```

**Menu Options:**
```
9. List All Resumes        # See all available resumes
10. Download Resume        # Download by Application ID
```

**Example Session:**
```
Enter your choice: 9

📎 Resumes (2):
  APP-00001: John Doe
    File: resume.pdf (100.0 KB) - ✓ Available
  APP-00002: Jane Smith
    File: cv.docx (85.5 KB) - ✓ Available

Enter your choice: 10
Enter Application ID: APP-00001
Save as (press Enter for default): john_doe_resume.pdf
✓ Resume downloaded: john_doe_resume.pdf
```

---

### Method 4: Python Script (Programmatic Access)

#### Simple Download
```python
import requests

app_id = "APP-00001"
response = requests.get(f"http://localhost:8000/api/applications/{app_id}/resume")

if response.status_code == 200:
    with open(f"{app_id}_resume.pdf", "wb") as f:
        f.write(response.content)
    print("Resume downloaded!")
```

#### Download All Resumes
```python
import requests

# Get list of all resumes
response = requests.get("http://localhost:8000/api/resumes")
resumes = response.json()['resumes']

# Download each resume
for resume in resumes:
    if resume['file_exists']:
        app_id = resume['application_id']
        filename = f"{app_id}_{resume['filename']}"
        
        response = requests.get(f"http://localhost:8000/api/applications/{app_id}/resume")
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"Downloaded: {filename}")
```

#### Using Storage Viewer Class
```python
from storage_viewer import StorageViewer

viewer = StorageViewer()

# List all resumes
resumes = viewer.list_all_resumes()
print(f"Found {resumes['total']} resumes")

# Download specific resume
viewer.download_resume("APP-00001", "downloaded_resume.pdf")
```

---

### Method 5: Direct File System Access

If you have access to the server:

```bash
# List all resume files
ls -lh /home/claude/resumes/

# Copy a resume
cp /home/claude/resumes/APP-00001_resume.pdf ./

# View PDF (if tools available)
xdg-open /home/claude/resumes/APP-00001_resume.pdf
```

---

## 🔗 API Endpoint Details

### Download Resume
**GET** `/api/applications/{application_id}/resume`

**Example:**
```bash
curl -O -J http://localhost:8000/api/applications/APP-00001/resume
```

**Response Headers:**
- `Content-Type`: `application/pdf` (or appropriate type)
- `Content-Disposition`: `attachment; filename="resume.pdf"`

**Supported File Types:**
- PDF: `application/pdf`
- DOC: `application/msword`
- DOCX: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

---

### List All Resumes
**GET** `/api/resumes`

**Response:**
```json
{
  "total": 2,
  "resumes": [
    {
      "application_id": "APP-00001",
      "applicant_name": "John Doe",
      "position": "Software Engineer",
      "filename": "resume.pdf",
      "file_size": 102400,
      "file_exists": true,
      "download_url": "/api/applications/APP-00001/resume",
      "submitted_at": "2025-11-08T10:30:00.123456"
    }
  ]
}
```

---

## 💻 Complete Example: Processing All Resumes

```python
import requests
import os

API_BASE_URL = "http://localhost:8000"

def download_all_resumes(output_dir="downloaded_resumes"):
    """Download all resumes to a directory"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of all resumes
    response = requests.get(f"{API_BASE_URL}/api/resumes")
    data = response.json()
    
    print(f"Found {data['total']} resumes")
    
    # Download each resume
    for resume in data['resumes']:
        if not resume['file_exists']:
            print(f"⚠️  Skipping {resume['application_id']} - file not found")
            continue
        
        app_id = resume['application_id']
        applicant = resume['applicant_name']
        filename = f"{app_id}_{applicant.replace(' ', '_')}_{resume['filename']}"
        filepath = os.path.join(output_dir, filename)
        
        # Download resume
        response = requests.get(f"{API_BASE_URL}/api/applications/{app_id}/resume")
        
        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            size_kb = len(response.content) / 1024
            print(f"✓ Downloaded: {filename} ({size_kb:.1f} KB)")
        else:
            print(f"✗ Failed: {app_id}")
    
    print(f"\n✓ All resumes downloaded to: {output_dir}/")

if __name__ == "__main__":
    download_all_resumes()
```

---

## 📊 Resume Storage Information

### Storage Structure
```python
# In main.py - application data includes:
{
    "application_id": "APP-00001",
    "full_name": "John Doe",
    "resume_filename": "resume.pdf",        # Original filename
    "resume_path": "/home/claude/resumes/APP-00001_resume.pdf",  # Disk path
    "resume_size": 102400,                  # File size in bytes
    ...
}
```

### File Management
- **Automatic Directory Creation:** The `/home/claude/resumes/` directory is created automatically on first upload
- **Unique Filenames:** Each resume is prefixed with the application ID to prevent conflicts
- **Persistent Storage:** Files remain on disk even if the server restarts

---

## 🔒 Security Considerations

### Current Implementation (Development)
- ⚠️ No authentication - anyone can download any resume
- ⚠️ Resume files stored in plaintext on disk
- ⚠️ No access logging

### Production Recommendations
1. **Add Authentication:** Require login to access resumes
2. **Authorization:** Check user permissions before serving files
3. **Encryption:** Encrypt resumes at rest
4. **Audit Logging:** Log all resume access
5. **Secure Storage:** Use cloud storage (S3) with signed URLs
6. **Virus Scanning:** Scan uploaded files for malware
7. **Rate Limiting:** Prevent bulk downloading

---

## 🚨 Troubleshooting

### Resume Not Found
**Error:** `404 - Resume file not found`

**Solutions:**
1. Check if application ID is correct
2. Verify resume was uploaded successfully
3. Check if `/home/claude/resumes/` directory exists
4. Verify file permissions

```bash
# Check if directory exists
ls -la /home/claude/resumes/

# Fix permissions if needed
chmod 755 /home/claude/resumes/
chmod 644 /home/claude/resumes/*
```

### Cannot Download Resume
**Error:** Download fails or corrupted file

**Solutions:**
1. Check server logs for errors
2. Verify file exists on disk
3. Check file size matches expected size
4. Try downloading with different method

```bash
# Verify file integrity
ls -lh /home/claude/resumes/APP-00001_resume.pdf
file /home/claude/resumes/APP-00001_resume.pdf
```

### Resume List Empty
**Error:** API returns empty list but files exist

**Solutions:**
1. Restart the server
2. Check if applications are in memory
3. Verify resume_path is stored in application data

---

## 📝 Quick Reference

### Download Single Resume
```bash
# Via cURL
curl -O http://localhost:8000/api/applications/APP-00001/resume

# Via Python
import requests
r = requests.get("http://localhost:8000/api/applications/APP-00001/resume")
open("resume.pdf", "wb").write(r.content)

# Via Browser
http://localhost:8000/api/applications/APP-00001/resume
```

### List All Resumes
```bash
# Via cURL
curl http://localhost:8000/api/resumes | jq

# Via Python
import requests
resumes = requests.get("http://localhost:8000/api/resumes").json()

# Via Storage Viewer
python storage_viewer.py
# Choose option 9
```

### Admin Dashboard
```bash
# Open in browser
open admin_dashboard.html
# or
firefox admin_dashboard.html
# or
chrome admin_dashboard.html
```

---

## 🎯 Best Practices

1. **Always use API endpoints** instead of direct file access
2. **Check file_exists** before attempting download
3. **Handle errors gracefully** in your code
4. **Use appropriate file extensions** when saving
5. **Implement authentication** in production
6. **Add virus scanning** for uploaded files
7. **Log resume access** for audit trails
8. **Use cloud storage** (S3) for production

---

## 🔄 Migration from In-Memory to Database

When moving to production with a database:

```python
# Update application model to include resume_path
class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True)
    application_id = Column(String, unique=True)
    resume_path = Column(String)  # Store file path
    # ... other fields

# Or use cloud storage
class Application(Base):
    resume_s3_key = Column(String)  # S3 object key
    resume_s3_bucket = Column(String)  # S3 bucket name
```

---

**Need help?** Check the admin dashboard or run `python storage_viewer.py` for interactive access!
