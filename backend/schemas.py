from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=120
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=5000
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=15000
    )

    effective_date: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "effective_date"
    )
    @classmethod
    def clean_values(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class DocumentResponse(BaseModel):

    document_type: str

    content: str

    ai_provider: str


class ExportRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1
    )

    document_type: str = Field(
        default="Legal Document",
        min_length=1,
        max_length=120
    )