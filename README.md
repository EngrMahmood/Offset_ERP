# Offset_ERP

A web-based ERP system for managing offset printing operations, built with Django and Python.  
This project includes modules for SKU management, recipe management, bulk uploads, and error handling.

---

## Features

- **SKU Management:** Add, edit, and delete SKUs.  
- **Recipe Management:** Create and manage printing recipes.  
- **Bulk Upload:** Upload CSV or Excel files to add multiple recipes at once.  
- **Error Handling:** Generates human-readable error files for failed bulk uploads.  
- **Template Downloads:** Download sample CSV and Excel templates for bulk uploads.  

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/EngrMahmood/Offset_ERP.git
cd Offset_ERP
Create a virtual environment:

bash
Copy code
python -m venv venv
Activate the virtual environment:

Windows (PowerShell):

powershell
Copy code
.\venv\Scripts\Activate.ps1
Windows (cmd):

cmd
Copy code
.\venv\Scripts\activate.bat
Linux / macOS:

bash
Copy code
source venv/bin/activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Apply migrations:

bash
Copy code
python manage.py migrate
Run the development server:

bash
Copy code
python manage.py runserver
Visit http://127.0.0.1:8000/ in your browser.

Usage
Navigate to Recipes → Bulk Upload to upload multiple recipes using CSV or Excel.

Download sample templates from Download Sample CSV / Excel.

If there are errors in your upload, download the error file for easy debugging.

Git Version Control
Commit changes:

bash
Copy code
git add .
git commit -m "Your commit message"
Push changes to GitHub:

bash
Copy code
git push origin main
Rollback / retrieve previous versions:
You can use git log to see previous commits and git checkout <commit_id> to revert to any version.

License
This project is licensed under the MIT License.

Author
Engr Mahmood