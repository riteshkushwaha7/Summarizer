import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import os
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv


# -----------------------------
# Configure Gemini
# -----------------------------
def configure_genai(api_key):
    genai.configure(api_key=api_key)


# -----------------------------
# Gemini Response
# -----------------------------
def get_gemini_response(prompt):

    model = genai.GenerativeModel("gemini-3-flash-preview")  
    # Fast, cheap, VERY stable

    response = model.generate_content(prompt)

    if not response or not response.text:
        raise Exception("Empty response from Gemini")

    return response.text


# -----------------------------
# PDF Extraction (VERY RELIABLE)
# -----------------------------
def extract_pdf_text(uploaded_file):

    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    if not text.strip():
        raise Exception(
            "This PDF appears to be scanned (image-based). "
            "Please upload a text-based earnings transcript."
        )

    return text


# -----------------------------
# PERFECT Prompt (No JSON = No Break)
# -----------------------------
def prepare_prompt(document_text):

    prompt = f"""
You are a senior equity research analyst.

Analyze the following earnings call transcript or management discussion.

Return your answer in CLEAR STRUCTURED FORMAT using headings.

DO NOT return JSON.

DO NOT add explanations.

ONLY extract what is present in the document.

If something is missing, write: Not mentioned.


FORMAT:

Management Tone:
Confidence Level:

Key Positives:
- bullet
- bullet

Key Concerns:
- bullet
- bullet

Forward Guidance:
Revenue Outlook:
Margin Outlook:
Capex Outlook:

Capacity Utilization Trend:

New Growth Initiatives:
- bullet
- bullet

Important Management Quotes:
- "quote"
- "quote"



DOCUMENT:
{document_text}
"""

    return prompt


# -----------------------------
# Session State
# -----------------------------
def init_session():
    if "processing" not in st.session_state:
        st.session_state.processing = False


# -----------------------------
# UI
# -----------------------------
def main():

    load_dotenv()
    init_session()

    st.set_page_config(
        page_title="AI Research Portal",
        page_icon="📊",
        layout="wide"
    )

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.error("Please add GOOGLE_API_KEY inside .env file")
        return

    configure_genai(api_key)

    # ---------------- SIDEBAR ----------------
    with st.sidebar:

        st.title("📊 AI Research Portal")

        st.write("""
This internal research tool helps analysts quickly extract insights from:

✅ Earnings Call Transcripts  
✅ Management Discussion  
✅ Annual Commentary  

Built for fast financial research.
""")

        add_vertical_space(2)
        st.write("Built by **Ritesh Kushwaha**")


    # ---------------- MAIN ----------------

    st.title("Management Commentary Analyzer")

    st.write(
        "Upload an earnings transcript and get structured research insights in seconds."
    )

    uploaded_file = st.file_uploader(
        "Upload Earnings Transcript (PDF)",
        type=["pdf"]
    )


    if st.button("Run Analysis", disabled=st.session_state.processing):

        if not uploaded_file:
            st.warning("Please upload a PDF.")
            return

        st.session_state.processing = True

        try:

            with st.spinner("Analyzing document..."):

                text = extract_pdf_text(uploaded_file)

                prompt = prepare_prompt(text)

                result = get_gemini_response(prompt)

                st.success("Analysis Complete ✅")

                st.markdown("---")

                st.markdown(result)

                st.download_button(
                    "Download Analysis",
                    result,
                    file_name="management_analysis.txt"
                )

        except Exception as e:
            st.error(f"Error: {str(e)}")

        finally:
            st.session_state.processing = False


if __name__ == "__main__":
    main()
