"""Test module."""

from pathlib import Path

from pypdf import PdfReader, PdfWriter


def keep_first_page_only(input_path: str | Path, output_path: str | Path | None = None) -> None:
    """Remove all pages of a PDF except the first one.

    Args:
        input_path: Path to the source PDF file.
        output_path: Path for the resulting PDF. If None, overwrites the input file.
    """
    input_path = Path(input_path)
    output_path = Path(output_path) if output_path is not None else input_path

    reader = PdfReader(input_path)
    writer = PdfWriter()

    if len(reader.pages) == 0:
        raise ValueError(f"PDF has no pages: {input_path}")

    writer.add_page(reader.pages[0])
    writer.write(output_path)


def main():
    """Entry point."""
    pass


if __name__ == "__main__":
    main()
