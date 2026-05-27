"""Document fetching and parsing via Docling."""

import asyncio
from pathlib import Path

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import AcceleratorDevice, AcceleratorOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DoclingDocument


def _make_pdf_converter() -> DocumentConverter:
    """Build a DocumentConverter configured to use CPU for PDF layout inference.

    Returns:
        A DocumentConverter with CPU acceleration to avoid MPS float64 issues
        on Apple Silicon.
    """
    pipeline_options = PdfPipelineOptions(
        accelerator_options=AcceleratorOptions(device=AcceleratorDevice.CPU)
    )
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )


def _convert_url(url: str) -> DoclingDocument:
    conv = DocumentConverter()
    result = conv.convert(url)
    if result.status != ConversionStatus.SUCCESS:
        raise RuntimeError(f"Docling failed to convert URL '{url}': {result.errors}")
    return result.document


def _convert_pdf(path: str) -> DoclingDocument:
    conv = _make_pdf_converter()
    result = conv.convert(Path(path))
    if result.status != ConversionStatus.SUCCESS:
        raise RuntimeError(f"Docling failed to convert PDF '{path}': {result.errors}")
    return result.document


async def load_url(url: str) -> DoclingDocument:
    """Fetch and parse a web page via Docling.

    Args:
        url: Public HTTP/HTTPS URL to fetch.

    Returns:
        Parsed DoclingDocument with text and structure extracted.

    Raises:
        RuntimeError: If Docling reports a conversion failure.
    """
    return await asyncio.to_thread(_convert_url, url)


async def load_pdf(path: str) -> DoclingDocument:
    """Load and parse a local PDF file via Docling.

    Args:
        path: Filesystem path to the PDF file.

    Returns:
        Parsed DoclingDocument with text and structure extracted.

    Raises:
        RuntimeError: If Docling reports a conversion failure.
    """
    return await asyncio.to_thread(_convert_pdf, path)
