import os
import json
import tempfile
from typing import List, Optional, Dict, Union

import streamlit as st
from streamlit_option_menu import option_menu
from docxcompose.composer import Composer
from docx import Document as Document_compose
from docx.shared import Inches

# Configuration
SUBMISSIONS_FILE = "submissions.json"
MAX_FILE_SIZE_MB = 10
ALLOWED_IMAGE_TYPES = ["png", "jpg", "jpeg"]

def validate_input(name: str, proj: str) -> bool:
    """Validate input fields."""
    if not name or not proj:
        st.error("Customer Name and Project Name are required!")
        return False
    return True

def save_temp_file(uploaded_file: Union[st.runtime.uploaded_file_manager.UploadedFile, None], prefix: str = '') -> Optional[str]:
    """
    Save uploaded file to a temporary location.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        prefix: Optional prefix for temp file
    
    Returns:
        Temporary file path or None
    """
    if uploaded_file is None:
        return None
    
    # File size check
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"File size exceeds {MAX_FILE_SIZE_MB} MB")
        return None
    
    # File type check
    if uploaded_file.type.split('/')[-1] not in ALLOWED_IMAGE_TYPES:
        st.error(f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}")
        return None
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.type.split('/')[-1]}") as tmpfile:
        tmpfile.write(uploaded_file.getbuffer())
        return tmpfile.name

def save_submission(submission: Dict):
    """Save submission to JSON file."""
    try:
        submissions = load_submissions()
        submissions.append(submission)
        with open(SUBMISSIONS_FILE, 'w') as f:
            json.dump(submissions, f, indent=4)
    except Exception as e:
        st.error(f"Error saving submission: {e}")

def load_submissions() -> List[Dict]:
    """Load submissions from JSON file."""
    try:
        if os.path.exists(SUBMISSIONS_FILE):
            with open(SUBMISSIONS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading submissions: {e}")
        return []

def create_proposal(name: str, proj: str, logo: Optional[st.runtime.uploaded_file_manager.UploadedFile], 
                    topology: Optional[st.runtime.uploaded_file_manager.UploadedFile], 
                    technologies: List[str], 
                    models: List[str], 
                    comments: str):
    """Main function to create technical proposal."""
    if not validate_input(name, proj):
        return

    logo_path = save_temp_file(logo)
    topology_path = save_temp_file(topology)

    try:
        master = Document_compose('section0.docx')
        
        if logo_path:
            replace_image_placeholder(master, "(Logo)", logo_path, 1.25)
            os.unlink(logo_path)

        replace_placeholder(master, "(Proj)", proj)
        replace_placeholder(master, "<<Customer Name>>", name)
        
        composer = Composer(master)
        
        # Enhanced file path handling
        models = [os.path.join("/home/fortinet/streamlit_env/TPB/Models", f"{model}.docx") 
                  for model in models]
        technologies = [f"{tech}.docx" for tech in technologies]
        mid = ['Design.docx']
        
        combined_list = technologies + mid + models
        
        process_documents(composer, combined_list, name, topology_path, comments)
        
    except Exception as e:
        st.error(f"Error creating proposal: {e}")

def process_documents(composer, document_list, name, topology_path, comments):
    """Process and combine documents."""
    missing_files = []
    for item in document_list:
        try:
            doc2 = Document_compose(item)
            replace_placeholder(doc2, "<<Customer Name>>", name)
            
            if item.endswith("Design.docx"):
                if topology_path:
                    replace_image_placeholder(doc2, "<<Design>>", topology_path, 6)
                    os.unlink(topology_path)
                replace_placeholder(doc2, "<<Design Describtion>>", comments)
            
            composer.append(doc2)
        except Exception as e:
            missing_files.append(item)
            st.error(f"Error appending {item}: {e}")

    # Existing code for saving and downloading the document...

# Existing helper functions like replace_placeholder() remain the same
