# upload_to_gcs_app.py
import streamlit as st
from google.cloud import storage
import tempfile
import os
import uuid

# === CONFIG ===
BUCKET_NAME = "mj-test-langchain"
GCS_UPLOAD_FOLDER = "uploaded-files/"  # Optional folder path in GCS
SERVICE_ACCOUNT_FILE = "/workspaces/brd-generation/keys/brd-generation-91eaf7b1a023.json"
#MAX_FILE_SIZE_MB = 10  # Max upload size limit
MAX_FILE_SIZE_KB = 500  # Max upload size limit

# === AUTH ===
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

# === STREAMLIT UI ===
st.title("Input Collection ")
#st.write("⚠️ Note: Files must be less than 200 KB. Larger files will be rejected.")
uploaded_file = st.file_uploader("Choose a DOCX, CSV, or TXT file", type=["docx", "csv", "txt"])

def sanitize_filename(filename: str) -> str:
    # Remove problematic characters and prepend a UUID to avoid collisions
    base_name = os.path.basename(filename)
    unique_name = f"{uuid.uuid4().hex}_{base_name}"
    return unique_name.replace(" ", "_")

if uploaded_file is not None:
    file_size_kb = uploaded_file.size / 1024
    st.write(f"Selected file: **{uploaded_file.name}** ({file_size_kb:.2f} KB)")

    if file_size_kb > MAX_FILE_SIZE_KB:
        st.error(f"File is too large. Please upload files smaller than {MAX_FILE_SIZE_KB} KB.")
    else:
        if st.button("Submit"):
            sanitized_name = sanitize_filename(uploaded_file.name)
            gcs_path = GCS_UPLOAD_FOLDER + sanitized_name
            
            with st.spinner("Uploading file..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name

                    blob = bucket.blob(gcs_path)
                    blob.upload_from_filename(tmp_path)

                    st.success(f"✅ File uploaded to GCS: `{gcs_path}`")
                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")
                finally:
                    # Cleanup temp file
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)