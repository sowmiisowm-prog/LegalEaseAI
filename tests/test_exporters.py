from backend.services.exporters import make_txt, make_docx, make_pdf


def test_txt_export():
    data = make_txt(
        "TITLE\nFreelance Work Contract"
    )

    assert isinstance(data, bytes)
    assert len(data) > 0
    assert b"Freelance Work Contract" in data


def test_docx_export():
    data = make_docx(
        "TITLE\nFreelance Work Contract"
    )

    assert isinstance(data, bytes)
    assert len(data) > 0


def test_pdf_export():
    data = make_pdf(
        "TITLE\nFreelance Work Contract"
    )

    assert isinstance(data, bytes)
    assert len(data) > 0