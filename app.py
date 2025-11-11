import streamlit as st
import pdfplumber
from groq import Groq
import io

st.set_page_config(page_title="AI Resume Tailor", page_icon="🤖")

# --- Sidebar: API Key ---
st.sidebar.title("🔑 Groq API Key")
api_key = st.sidebar.text_input("Enter your Groq API key", type="password")
client = Groq(api_key=api_key) if api_key else None

# --- Title ---
st.title("AI Resume Tailor")
st.markdown("""
<style>
h1, h2, h3 { color: #007acc; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.write("Upload your resume and paste a job description to get a tailored summary, missing skills, and a cover letter.")

# --- Upload Resume ---
uploaded_file = st.file_uploader("📄 Upload your Resume (PDF)", type="pdf")
job_desc = st.text_area("💼 Paste the Job Description")

# --- Try with Sample Job Description ---
if st.button("Try with sample data"):
    job_desc = """We are looking for a Python Developer with experience in APIs and automation testing."""
    st.session_state["job_desc"] = job_desc

if st.button("✨ Generate Tailored Output"):
    if not uploaded_file or not job_desc:
        st.warning("Please upload your resume and paste the job description.")
    elif not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
    else:
        with pdfplumber.open(uploaded_file) as pdf:
            resume_text = ""
            for page in pdf.pages:
                resume_text += page.extract_text() or ""

        with st.spinner("Analyzing your resume..."):
            # run the API call
            prompt = f"""
            You are an AI career assistant. 
            Compare this resume and job description, then provide:
            1. A 4-line summary tailored to this job.
            2. A list of missing or underrepresented keywords/skills.
            3. A short 1-paragraph cover letter draft.
    
            Resume:
            {resume_text}
    
            Job Description:
            {job_desc}
            """

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # or "llama3-8b-8192" for slightly faster responses
                messages=[{"role": "user", "content": prompt}]
            )

            output = response.choices[0].message.content

            # --- Split sections based on keywords ---
            sections = {
                "Summary": "",
                "Missing Keywords": "",
                "Cover Letter": ""
            }

            for key in sections.keys():
                start = output.lower().find(key.lower())
                if start != -1:
                    end = len(output)
                    for next_key in sections.keys():
                        if next_key != key:
                            next_start = output.lower().find(next_key.lower(), start + 1)
                            if next_start != -1 and next_start < end:
                                end = next_start
                    sections[key] = output[start:end].strip()

            # --- Display in Streamlit ---
            st.subheader("🎯 Tailored Summary")
            st.write(sections["Summary"] or output)

            st.subheader("🧩 Missing Keywords / Skills")
            st.write(sections["Missing Keywords"] or "Not identified clearly.")

            st.subheader("💌 Cover Letter Draft")
            st.write(sections["Cover Letter"] or "No cover letter generated.")

            if output:
                st.download_button(
                    label="📥 Download Result",
                    data=io.StringIO(output).getvalue(),
                    file_name="tailored_resume_output.txt",
                    mime="text/plain"
                )

# --- Website footer ---
st.markdown("""
<style>
footer {
    visibility: visible;
    position: fixed;
}
</style>

<footer>
    🧠 Powered by <b>Llama 3</b> via <b>Groq API</b> — Made with ❤️ using <b>Streamlit</b>
</footer>
""", unsafe_allow_html=True)
