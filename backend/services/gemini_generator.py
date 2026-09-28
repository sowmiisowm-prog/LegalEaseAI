from google import genai
from google.genai import types

from backend.config import get_settings
from backend.utils.text import sanitize_text


class GeminiDocumentGenerator:

    def __init__(self):
        self.settings = get_settings()
        self.client = None

        if self.settings.GEMINI_API_KEY:
            try:
                self.client = genai.Client(
                    api_key=self.settings.GEMINI_API_KEY
                )
            except Exception:
                self.client = None

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ):

        # Try Gemini first
        if self.client:

            prompt = f"""
You are LegalEase, an AI-assisted legal document drafting system.

Create a professional legal document using ONLY the information supplied
by the user.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

EFFECTIVE DATE:
{effective_date}

TERMS:
{terms}

IMPORTANT:
- Use the actual information supplied by the user.
- Do not replace specific information with generic phrases.
- Do not invent names, dates, amounts, jurisdictions, or obligations.
- Preserve every important user-supplied term.
- Do not create duplicate numbering such as "1. 1." or "2. 2.".
- Do not invent governing law.
- If governing law is not supplied, use:
  [JURISDICTION TO BE CONFIRMED]

Create the document using this structure:

TITLE

PARTIES

EFFECTIVE DATE

1. PURPOSE

2. SERVICES AND OBLIGATIONS

3. PAYMENT AND CONSIDERATION

4. CONFIDENTIALITY

5. INTELLECTUAL PROPERTY

6. TERMINATION

7. GOVERNING LAW AND DISPUTE RESOLUTION

8. ADDITIONAL TERMS

9. SIGNATURES

10. AI-ASSISTED DRAFT DISCLAIMER

The SERVICES AND OBLIGATIONS section must contain the actual services
from the supplied terms.

The PAYMENT AND CONSIDERATION section must contain the actual fee
and payment schedule from the supplied terms.

The TERMINATION section must contain the actual termination terms
from the supplied terms.

Return only the final legal document as plain text.
"""

            try:
                response = self.client.models.generate_content(
                    model=self.settings.GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=8000,
                    ),
                )

                generated_text = getattr(
                    response,
                    "text",
                    ""
                )

                generated_text = self.clean_output(
                    generated_text
                )

                if generated_text:
                    return (
                        generated_text,
                        f"gemini:{self.settings.GEMINI_MODEL}",
                    )

            except Exception:
                pass

        # Use local fallback if Gemini is unavailable
        return (
            self.local_fallback(
                document_type,
                parties,
                terms,
                effective_date,
            ),
            "local-fallback",
        )

    def clean_output(self, text: str) -> str:

        if not text:
            return ""

        text = text.replace("•", "-")
        text = text.replace("–", "-")
        text = text.replace("—", "-")

        cleaned_lines = []

        for line in text.splitlines():

            line = line.rstrip()

            # Fix:
            # 1. 1. Text
            # 2. 2. Text
            parts = line.split(".", 2)

            if (
                len(parts) == 3
                and parts[0].strip().isdigit()
                and parts[1].strip() == parts[0].strip()
            ):
                line = (
                    f"{parts[0].strip()}. "
                    f"{parts[2].strip()}"
                )

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    def clean_terms(self, terms: str):

        if not terms:
            return []

        result = []

        for line in terms.splitlines():

            line = line.strip()

            if not line:
                continue

            # Remove existing numbering.
            while True:

                new_line = line

                if len(line) >= 2:

                    i = 0

                    while i < len(line) and line[i].isdigit():
                        i += 1

                    if i > 0 and i < len(line):

                        if line[i] in [".", ")", "-"]:
                            new_line = line[i + 1:].strip()

                if new_line == line:
                    break

                line = new_line

            if line:
                result.append(line)

        return result

    def local_fallback(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
    ):

        terms_list = self.clean_terms(terms)

        # Find important terms from the user's actual input.
        service_terms = []
        payment_terms = []
        confidentiality_terms = []
        termination_terms = []
        additional_terms = []

        for term in terms_list:

            lower = term.lower()

            if any(
                word in lower
                for word in [
                    "develop",
                    "website",
                    "service",
                    "work",
                    "deliver",
                ]
            ):
                service_terms.append(term)

            elif any(
                word in lower
                for word in [
                    "fee",
                    "payment",
                    "pay",
                    "advance",
                    "remaining",
                ]
            ):
                payment_terms.append(term)

            elif any(
                word in lower
                for word in [
                    "confidential",
                    "private",
                ]
            ):
                confidentiality_terms.append(term)

            elif any(
                word in lower
                for word in [
                    "terminate",
                    "termination",
                    "notice",
                ]
            ):
                termination_terms.append(term)

            else:
                additional_terms.append(term)

        document_parts = []

        document_parts.append(
            document_type
        )

        document_parts.append("")

        document_parts.append("TITLE")
        document_parts.append(document_type)

        document_parts.append("")

        document_parts.append("PARTIES")
        document_parts.append(parties)

        document_parts.append("")

        document_parts.append("EFFECTIVE DATE")
        document_parts.append(effective_date)

        document_parts.append("")

        document_parts.append("1. PURPOSE")
        document_parts.append(
            "This agreement records the principal terms "
            "agreed between the parties for the services "
            "described below."
        )

        document_parts.append("")

        document_parts.append(
            "2. SERVICES AND OBLIGATIONS"
        )

        if service_terms:

            for term in service_terms:
                document_parts.append(
                    f"- {term}"
                )

        else:

            document_parts.append(
                "The parties shall perform the services "
                "and obligations agreed between them."
            )

        document_parts.append("")

        document_parts.append(
            "3. PAYMENT AND CONSIDERATION"
        )

        if payment_terms:

            for term in payment_terms:
                document_parts.append(
                    f"- {term}"
                )

        else:

            document_parts.append(
                "Payment terms shall be as agreed between "
                "the parties."
            )

        document_parts.append("")

        document_parts.append(
            "4. CONFIDENTIALITY"
        )

        if confidentiality_terms:

            for term in confidentiality_terms:
                document_parts.append(
                    f"- {term}"
                )

        else:

            document_parts.append(
                "The parties shall keep confidential "
                "information received from the other party "
                "private and use it only for the purposes "
                "of this agreement."
            )

        document_parts.append("")

        document_parts.append(
            "5. INTELLECTUAL PROPERTY"
        )

        document_parts.append(
            "Intellectual property ownership and permitted "
            "use of work product should be confirmed by "
            "the parties before signing."
        )

        document_parts.append("")

        document_parts.append(
            "6. TERMINATION"
        )

        if termination_terms:

            for term in termination_terms:
                document_parts.append(
                    f"- {term}"
                )

        else:

            document_parts.append(
                "Termination shall be according to the "
                "conditions agreed between the parties."
            )

        document_parts.append("")

        document_parts.append(
            "7. GOVERNING LAW AND DISPUTE RESOLUTION"
        )

        document_parts.append(
            "[JURISDICTION TO BE CONFIRMED]"
        )

        document_parts.append(
            "The parties should specify applicable law "
            "and dispute-resolution procedures before signing."
        )

        document_parts.append("")

        document_parts.append(
            "8. ADDITIONAL TERMS"
        )

        if additional_terms:

            for index, term in enumerate(
                additional_terms,
                start=1
            ):
                document_parts.append(
                    f"{index}. {term}"
                )

        else:

            document_parts.append(
                "Both parties agree to communicate and "
                "cooperate in good faith to complete the project."
            )

        document_parts.append("")

        document_parts.append(
            "9. SIGNATURES"
        )

        document_parts.append("")

        document_parts.append("Party 1:")
        document_parts.append(
            "Signature: ______________________________"
        )
        document_parts.append(
            "Name: __________________________________"
        )
        document_parts.append(
            "Date: __________________________________"
        )

        document_parts.append("")

        document_parts.append("Party 2:")
        document_parts.append(
            "Signature: ______________________________"
        )
        document_parts.append(
            "Name: __________________________________"
        )
        document_parts.append(
            "Date: __________________________________"
        )

        document_parts.append("")

        document_parts.append(
            "10. AI-ASSISTED DRAFT DISCLAIMER"
        )

        document_parts.append(
            "This document is an AI-assisted draft based "
            "on user-provided information."
        )

        document_parts.append(
            "It should be reviewed and, where appropriate, "
            "customized by a qualified legal professional "
            "before it is signed or relied upon."
        )

        return sanitize_text(
            "\n".join(document_parts)
        )