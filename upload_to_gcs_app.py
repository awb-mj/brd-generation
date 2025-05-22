# upload_to_gcs_app.py
import streamlit as st
from google.cloud import storage
import tempfile
import os

# === CONFIG ===
BUCKET_NAME = "mj-test-langchain"
GCS_UPLOAD_FOLDER = "uploaded-files/"  # Optional folder path in GCS
SERVICE_ACCOUNT_FILE = "/workspaces/brd-generation/keys/brd-generation-91eaf7b1a023.json"


# === AUTH ===
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

# === STREAMLIT UI ===
st.title("📁 Upload to Google Cloud Storage")

uploaded_file = st.file_uploader("Choose a DOCX or CSV file", type=["docx", "csv"])

if uploaded_file is not None:
    filename = uploaded_file.name
    gcs_path = GCS_UPLOAD_FOLDER + filename

    # Save temporarily and upload
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(tmp_path)

    st.success(f"✅ File uploaded to GCS: `{gcs_path}`")
