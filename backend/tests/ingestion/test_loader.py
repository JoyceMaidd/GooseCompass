"""Tests for backend/ingestion/loader.py.

These are integration tests: load_url makes a real HTTP request, load_pdf
reads a fixture file from disk, and load_html reads a fixture file from
disk. All require Docling to be installed.
"""

from pathlib import Path

import pytest
from docling_core.types.doc import DoclingDocument

from backend.ingestion.loader import load_html, load_pdf, load_url

FIXTURE_PDF = Path(__file__).parent.parent / "fixtures" / "test.pdf"
FIXTURE_HTML = Path(__file__).parent.parent / "fixtures" / "test.html"
TEST_URL = "https://uwaterloo.ca/international-experience/exchange-and-study-abroad/go-abroad/getting-started"


class TestLoadUrl:
    async def test_returns_docling_document(self):
        doc = await load_url(TEST_URL)
        assert isinstance(doc, DoclingDocument)

    async def test_document_has_content(self):
        doc = await load_url(TEST_URL)
        text = doc.export_to_text()
        assert len(text) > 100

    async def test_invalid_url_raises(self):
        with pytest.raises((RuntimeError, Exception)):
            await load_url("https://this-domain-does-not-exist-xyz.invalid/page")


class TestLoadPdf:
    async def test_returns_docling_document(self):
        assert FIXTURE_PDF.exists(), f"Missing test fixture: {FIXTURE_PDF}"
        doc = await load_pdf(str(FIXTURE_PDF))
        assert isinstance(doc, DoclingDocument)

    async def test_document_has_content(self):
        doc = await load_pdf(str(FIXTURE_PDF))
        text = doc.export_to_text()
        assert len(text) > 0

    async def test_missing_file_raises(self):
        with pytest.raises((RuntimeError, Exception)):
            await load_pdf("/nonexistent/path/file.pdf")


class TestLoadHtml:
    async def test_returns_docling_document(self):
        assert FIXTURE_HTML.exists(), f"Missing test fixture: {FIXTURE_HTML}"
        doc = await load_html(str(FIXTURE_HTML))
        assert isinstance(doc, DoclingDocument)

    async def test_document_has_content(self):
        doc = await load_html(str(FIXTURE_HTML))
        text = doc.export_to_text()
        assert len(text) > 0

    async def test_missing_file_raises(self):
        with pytest.raises((RuntimeError, Exception)):
            await load_html("/nonexistent/path/file.html")
