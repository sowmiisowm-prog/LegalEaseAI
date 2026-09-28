import os

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

LOGO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "backend",
    "assets",
    "logo.png",
)


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 25px;
    }

    .download-title {
        font-size: 24px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOGO
# ============================================================

if os.path.isfile(LOGO_PATH):

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:
        st.image(
            LOGO_PATH,
            width=140,
        )


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">AI-Powered Legal Document Generator</div>',
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = "Freelance Work Contract"


# ============================================================
# INPUT SECTION
# ============================================================

st.subheader("Create Your Legal Document")

document_type = st.text_input(
    "Document Type",
    value=st.session_state.document_type,
    placeholder="Example: Freelance Work Contract",
)

parties = st.text_area(
    "Parties Involved",
    placeholder=(
        "Client: ABC Technologies Pvt. Ltd.\n"
        "Freelancer: Arun Kumar"
    ),
    height=100,
)

effective_date = st.text_input(
    "Effective Date",
    placeholder="Example: 1 October 2026",
)

terms = st.text_area(
    "Terms & Conditions",
    placeholder=(
        "Enter the terms and conditions here.\n\n"
        "Example:\n"
        "1. The Freelancer will develop a professional business website for the Client.\n"
        "2. The total project fee is Rs. 25,000.\n"
        "3. The Client will pay 50% of the project fee as an advance.\n"
        "4. The remaining 50% will be paid after completion."
    ),
    height=300,
)


# ============================================================
# GENERATE DOCUMENT
# ============================================================

if st.button(
    "Generate Document",
    type="primary",
    use_container_width=True,
):

    if not document_type.strip():
        st.error("Please enter the document type.")
        st.stop()

    if not parties.strip():
        st.error("Please enter the parties involved.")
        st.stop()

    if not effective_date.strip():
        st.error("Please enter the effective date.")
        st.stop()

    if not terms.strip():
        st.error("Please enter the terms and conditions.")
        st.stop()

    payload = {
        "document_type": document_type,
        "parties": parties,
        "terms": terms,
        "effective_date": effective_date,
    }

    try:

        with st.spinner("Generating legal document..."):

            response = requests.post(
                f"{BACKEND_URL}/generate",
                json=payload,
                timeout=120,
            )

        if response.status_code == 200:

            result = response.json()

            generated_text = result.get(
                "document",
                "",
            )

            if not generated_text:
                st.error(
                    "Backend returned an empty document."
                )
            else:

                st.session_state.document_text = (
                    generated_text
                )

                st.session_state.document_type = (
                    document_type
                )

                st.success(
                    "Document generated successfully."
                )

        else:

            try:
                error_data = response.json()
                detail = error_data.get(
                    "detail",
                    response.text,
                )
            except Exception:
                detail = response.text

            st.error(
                f"Document generation failed: {detail}"
            )

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to LegalEase backend. "
            f"Please make sure FastAPI is running at {BACKEND_URL}"
        )

    except requests.exceptions.Timeout:

        st.error(
            "The backend took too long to respond."
        )

    except Exception as exc:

        st.error(
            f"Document generation failed: {exc}"
        )


# ============================================================
# EDITABLE DOCUMENT
# ============================================================

if st.session_state.document_text:

    st.subheader("Generated Document")

    edited_text = st.text_area(
        "Edit your document if required",
        value=st.session_state.document_text,
        height=650,
    )

    st.session_state.document_text = edited_text


# ============================================================
# DOWNLOAD DOCUMENTS
# ============================================================

if st.session_state.document_text:

    st.markdown(
        '<div class="download-title">Download Document</div>',
        unsafe_allow_html=True,
    )

    document_text = st.session_state.document_text
    current_document_type = st.session_state.document_type

    col1, col2, col3 = st.columns(3)

    # --------------------------------------------------------
    # TXT
    # --------------------------------------------------------

    with col1:

        if st.button(
            "📄 Download TXT",
            use_container_width=True,
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export/txt",
                    json={
                        "text": document_text,
                        "document_type": current_document_type,
                    },
                    timeout=60,
                )

                if response.status_code == 200:

                    st.download_button(
                        label="⬇️ Save TXT File",
                        data=response.content,
                        file_name="LegalEase_Document.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

                else:

                    try:
                        detail = response.json().get(
                            "detail",
                            response.text,
                        )
                    except Exception:
                        detail = response.text

                    st.error(
                        f"TXT export error: {detail}"
                    )

            except Exception as exc:

                st.error(
                    f"TXT export error: {exc}"
                )

    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    with col2:

        if st.button(
            "📝 Download Word",
            use_container_width=True,
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export/docx",
                    json={
                        "text": document_text,
                        "document_type": current_document_type,
                    },
                    timeout=60,
                )

                if response.status_code == 200:

                    st.download_button(
                        label="⬇️ Save Word File",
                        data=response.content,
                        file_name="LegalEase_Document.docx",
                        mime=(
                            "application/vnd.openxmlformats-"
                            "officedocument.wordprocessingml.document"
                        ),
                        use_container_width=True,
                    )

                else:

                    try:
                        detail = response.json().get(
                            "detail",
                            response.text,
                        )
                    except Exception:
                        detail = response.text

                    st.error(
                        f"Word export error: {detail}"
                    )

            except Exception as exc:

                st.error(
                    f"Word export error: {exc}"
                )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    with col3:

        if st.button(
            "📕 Download PDF",
            use_container_width=True,
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export/pdf",
                    json={
                        "text": document_text,
                        "document_type": current_document_type,
                    },
                    timeout=60,
                )

                if response.status_code == 200:

                    st.download_button(
                        label="⬇️ Save PDF File",
                        data=response.content,
                        file_name="LegalEase_Document.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

                else:

                    try:
                        detail = response.json().get(
                            "detail",
                            response.text,
                        )
                    except Exception:
                        detail = response.text

                    st.error(
                        f"PDF export failed: {detail}"
                    )

            except Exception as exc:

                st.error(
                    f"PDF export failed: {exc}"
                )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown("---")

st.caption(
    "LegalEase generates AI-assisted legal drafts. "
    "Review the document carefully and, where appropriate, "
    "consult a qualified legal professional before signing "
    "or relying on it."
)