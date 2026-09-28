from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.schemas import DocumentRequest
from backend.services.gemini_generator import GeminiDocumentGenerator
from backend.services.exporters import (
    make_txt,
    make_docx,
    make_pdf,
)

router = APIRouter()

generator = GeminiDocumentGenerator()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "legalease-backend",
    }


@router.post("/generate")
def generate_document(request: DocumentRequest):

    try:
        text, source = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
        )

        return {
            "document": text,
            "source": source,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document generation failed: {str(exc)}",
        )


@router.post("/export/txt")
def export_txt(request: dict):

    try:
        text = request.get("text", "")
        document_type = request.get(
            "document_type",
            "Legal Document",
        )

        if not text:
            raise HTTPException(
                status_code=400,
                detail="No document text provided.",
            )

        data = make_txt(
            text=text,
            document_type=document_type,
        )

        return Response(
            content=data,
            media_type="text/plain; charset=utf-8",
            headers={
                "Content-Disposition": (
                    'attachment; filename="LegalEase_Document.txt"'
                )
            },
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"TXT export failed: {str(exc)}",
        )


@router.post("/export/docx")
def export_docx(request: dict):

    try:
        text = request.get("text", "")
        document_type = request.get(
            "document_type",
            "Legal Document",
        )

        if not text:
            raise HTTPException(
                status_code=400,
                detail="No document text provided.",
            )

        data = make_docx(
            text=text,
            document_type=document_type,
        )

        return Response(
            content=data,
            media_type=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            headers={
                "Content-Disposition": (
                    'attachment; filename="LegalEase_Document.docx"'
                )
            },
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Word export failed: {str(exc)}",
        )


@router.post("/export/pdf")
def export_pdf(request: dict):

    try:
        text = request.get("text", "")
        document_type = request.get(
            "document_type",
            "Legal Document",
        )

        if not text:
            raise HTTPException(
                status_code=400,
                detail="No document text provided.",
            )

        data = make_pdf(
            text=text,
            document_type=document_type,
        )

        return Response(
            content=data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    'attachment; filename="LegalEase_Document.pdf"'
                )
            },
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"PDF export failed: {str(exc)}",
        )