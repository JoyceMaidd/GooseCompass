"""Tests for backend/ingestion/chunker.py."""

from pathlib import Path

import pytest
from docling_core.types.doc import DocItemLabel, DoclingDocument

from backend.ingestion.chunker import chunk_document
from backend.ingestion.loader import load_url
from backend.ingestion.models import ChunkData

TEST_URL = "https://uwaterloo.ca/international-experience/exchange-and-study-abroad/go-abroad/getting-started"
WEB_META = {"type": "web", "url": TEST_URL}
PDF_META = {"type": "pdf", "path": "documents/public/exchange_guide.pdf"}
HTML_META = {"type": "html", "path": "documents/private/country_guides/China (PRC).html"}


def _make_test_doc() -> DoclingDocument:
    """Build a minimal DoclingDocument with heading/paragraph structure."""
    doc = DoclingDocument(name="exchange-guide")
    doc.add_heading(text="Exchange Information", level=1)
    doc.add_text(label=DocItemLabel.PARAGRAPH, text=(
        "This section explains the exchange program requirements and eligibility "
        "criteria for University of Waterloo students."
    ))
    doc.add_heading(text="GPA Requirements", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH, text=(
        "Students must maintain a minimum cumulative GPA of 70 percent to be "
        "eligible. Some partner universities may require higher academic standing."
    ))
    doc.add_heading(text="Application Steps", level=2)
    doc.add_text(label=DocItemLabel.PARAGRAPH, text=(
        "Submit the online application form at least six months before your "
        "intended departure. Attach all required documents including transcripts."
    ))
    return doc


def _make_single_heading_doc(name: str) -> DoclingDocument:
    """Build a DoclingDocument with one generic heading, like the real country guides."""
    doc = DoclingDocument(name=name)
    doc.add_heading(text="Tips", level=1)
    doc.add_text(label=DocItemLabel.PARAGRAPH, text=(
        "Public transit passes are affordable and widely used by exchange "
        "students living off campus during their term abroad."
    ))
    return doc


class TestChunkDocumentUrl:
    async def test_returns_nonempty_list(self):
        doc = await load_url(TEST_URL)
        chunks = await chunk_document(doc, WEB_META)
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    async def test_each_chunk_has_content(self):
        doc = await load_url(TEST_URL)
        chunks = await chunk_document(doc, WEB_META)
        for chunk in chunks:
            assert isinstance(chunk, ChunkData)
            assert chunk.content.strip() != ""

    async def test_metadata_populated(self):
        doc = await load_url(TEST_URL)
        chunks = await chunk_document(doc, WEB_META)
        for chunk in chunks:
            assert chunk.source_url == TEST_URL
            assert chunk.document_type == "web"
            assert isinstance(chunk.document_title, str)
            assert isinstance(chunk.section_title, str)
            assert isinstance(chunk.chunk_index, int)

    async def test_chunk_indices_are_sequential(self):
        doc = await load_url(TEST_URL)
        chunks = await chunk_document(doc, WEB_META)
        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))


class TestChunkDocumentPdf:
    async def test_returns_nonempty_list(self):
        doc = _make_test_doc()
        chunks = await chunk_document(doc, PDF_META)
        assert len(chunks) > 0

    async def test_each_chunk_has_content(self):
        doc = _make_test_doc()
        chunks = await chunk_document(doc, PDF_META)
        for chunk in chunks:
            assert isinstance(chunk, ChunkData)
            assert chunk.content.strip() != ""

    async def test_pdf_metadata_populated(self):
        doc = _make_test_doc()
        chunks = await chunk_document(doc, PDF_META)
        for chunk in chunks:
            assert chunk.source_url == PDF_META["path"]
            assert chunk.document_type == "pdf"
            assert chunk.document_title != ""
            assert chunk.section_title != ""


class TestChunkDocumentHtml:
    async def test_returns_nonempty_list(self):
        doc = _make_single_heading_doc("China (PRC)")
        chunks = await chunk_document(doc, HTML_META)
        assert len(chunks) > 0

    async def test_document_title_uses_filename_not_heading(self):
        doc = _make_single_heading_doc("China (PRC)")
        chunks = await chunk_document(doc, HTML_META)
        for chunk in chunks:
            assert chunk.document_title == "China (PRC)"
            assert chunk.document_title != "Tips"

    async def test_section_title_still_uses_heading(self):
        doc = _make_single_heading_doc("China (PRC)")
        chunks = await chunk_document(doc, HTML_META)
        for chunk in chunks:
            assert chunk.section_title == "Tips"

    async def test_html_metadata_populated(self):
        doc = _make_single_heading_doc("Sweden")
        chunks = await chunk_document(doc, HTML_META)
        for chunk in chunks:
            assert chunk.source_url == HTML_META["path"]
            assert chunk.document_type == "html"
