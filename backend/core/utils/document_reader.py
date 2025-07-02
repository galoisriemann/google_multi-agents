"""Document Reader Utility for PDF and DOCX Files.

This module provides functionality to read PDF and DOCX files and convert
their content to markdown format for use in agent workflows.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

logger = logging.getLogger(__name__)


class DocumentReaderError(Exception):
    """Custom exception for document reading errors."""
    pass


class DocumentReader:
    """Reader class for PDF and DOCX documents with markdown output."""
    
    def __init__(self, input_directory: Optional[Path] = None):
        """Initialize the document reader.
        
        Args:
            input_directory: Directory containing input documents.
                           Defaults to 'backend/input' if not provided.
        """
        if input_directory is None:
            # Default to backend/input directory
            self.input_directory = Path(__file__).parent.parent.parent / "input"
        else:
            self.input_directory = Path(input_directory)
        
        # Create input directory if it doesn't exist
        self.input_directory.mkdir(parents=True, exist_ok=True)
        
        # Create input_markdown directory for saving markdown versions
        self.input_markdown_directory = self.input_directory.parent / "input_markdown"
        self.input_markdown_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DocumentReader initialized with input directory: {self.input_directory}")
        logger.info(f"Markdown output directory: {self.input_markdown_directory}")
    
    def read_document(self, filename: str) -> str:
        """Read a document and return its content as markdown.
        
        Args:
            filename: Name of the file to read (with extension)
            
        Returns:
            Document content as markdown string. Empty string if file not found.
            
        Raises:
            DocumentReaderError: If there's an error reading the document
        """
        if not filename or not filename.strip():
            return ""
        
        file_path = self.input_directory / filename
        
        if not file_path.exists():
            logger.warning(f"Document not found: {file_path}")
            return ""
        
        # Check if markdown version already exists
        markdown_filename = file_path.stem + ".md"
        markdown_path = self.input_markdown_directory / markdown_filename
        
        if markdown_path.exists():
            # Return existing markdown version
            logger.info(f"Using cached markdown version: {markdown_path}")
            try:
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to read cached markdown, regenerating: {e}")
        
        try:
            # Determine file type by extension and read content
            extension = file_path.suffix.lower()
            
            if extension == '.pdf':
                content = self._read_pdf(file_path)
            elif extension == '.docx':
                content = self._read_docx(file_path)
            else:
                logger.warning(f"Unsupported file type: {extension}")
                return ""
            
            # Save markdown version to input_markdown directory
            if content:
                self._save_markdown_version(content, markdown_path, filename)
            
            return content
                
        except Exception as e:
            error_msg = f"Error reading document {filename}: {str(e)}"
            logger.error(error_msg)
            raise DocumentReaderError(error_msg) from e
    
    def _save_markdown_version(self, content: str, markdown_path: Path, original_filename: str) -> None:
        """Save markdown version of the document to input_markdown directory.
        
        Args:
            content: Markdown content to save
            markdown_path: Path where to save the markdown file
            original_filename: Original filename for logging
        """
        try:
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved markdown version: {markdown_path} (from {original_filename})")
        except Exception as e:
            logger.warning(f"Failed to save markdown version for {original_filename}: {e}")
    
    def _read_pdf(self, file_path: Path) -> str:
        """Read PDF file and convert to markdown.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            PDF content as markdown string
            
        Raises:
            DocumentReaderError: If PyPDF2 is not installed or reading fails
        """
        if PyPDF2 is None:
            raise DocumentReaderError(
                "PyPDF2 is not installed. Please install it with: pip install PyPDF2"
            )
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content_parts = []
                
                # Add metadata header
                content_parts.append(f"# Document: {file_path.name}\n")
                content_parts.append(f"**Source**: PDF file with {len(pdf_reader.pages)} pages\n")
                content_parts.append("---\n")
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            content_parts.append(f"## Page {page_num}\n")
                            content_parts.append(page_text.strip())
                            content_parts.append("\n")
                    except Exception as e:
                        logger.warning(f"Error reading page {page_num}: {e}")
                        content_parts.append(f"## Page {page_num}\n")
                        content_parts.append("*[Error reading this page]*\n")
                
                result = "\n".join(content_parts)
                logger.info(f"Successfully read PDF: {file_path.name} ({len(pdf_reader.pages)} pages)")
                return result
                
        except Exception as e:
            raise DocumentReaderError(f"Failed to read PDF {file_path.name}: {str(e)}") from e
    
    def _read_docx(self, file_path: Path) -> str:
        """Read DOCX file and convert to markdown.
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            DOCX content as markdown string
            
        Raises:
            DocumentReaderError: If python-docx is not installed or reading fails
        """
        if Document is None:
            raise DocumentReaderError(
                "python-docx is not installed. Please install it with: pip install python-docx"
            )
        
        try:
            doc = Document(file_path)
            content_parts = []
            
            # Add metadata header
            content_parts.append(f"# Document: {file_path.name}\n")
            content_parts.append(f"**Source**: DOCX file with {len(doc.paragraphs)} paragraphs\n")
            content_parts.append("---\n")
            
            # Extract text from paragraphs
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                if text:
                    # Simple heuristic for headers (all caps or starts with numbers)
                    if text.isupper() or (text and text[0].isdigit() and '.' in text[:10]):
                        content_parts.append(f"## {text}\n")
                    else:
                        content_parts.append(f"{text}\n")
            
            # Extract text from tables if any
            if doc.tables:
                content_parts.append("\n## Tables\n")
                for table_num, table in enumerate(doc.tables, 1):
                    content_parts.append(f"### Table {table_num}\n")
                    content_parts.append("| " + " | ".join("Column " + str(i+1) for i in range(len(table.rows[0].cells))) + " |\n")
                    content_parts.append("| " + " | ".join("---" for _ in range(len(table.rows[0].cells))) + " |\n")
                    
                    for row in table.rows:
                        row_data = []
                        for cell in row.cells:
                            cell_text = cell.text.strip().replace('\n', ' ')
                            row_data.append(cell_text if cell_text else " ")
                        content_parts.append("| " + " | ".join(row_data) + " |\n")
                    content_parts.append("\n")
            
            result = "\n".join(content_parts)
            logger.info(f"Successfully read DOCX: {file_path.name} ({len(doc.paragraphs)} paragraphs)")
            return result
            
        except Exception as e:
            raise DocumentReaderError(f"Failed to read DOCX {file_path.name}: {str(e)}") from e
    
    def list_available_documents(self) -> Dict[str, Dict[str, Any]]:
        """List all available PDF and DOCX documents in the input directory.
        
        Returns:
            Dictionary with filename as key and file info as value
        """
        documents = {}
        
        for file_path in self.input_directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.docx']:
                documents[file_path.name] = {
                    'path': str(file_path),
                    'type': file_path.suffix.lower(),
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime
                }
        
        return documents
    
    def validate_document(self, filename: str) -> bool:
        """Validate if a document exists and is readable.
        
        Args:
            filename: Name of the file to validate
            
        Returns:
            True if document exists and is supported, False otherwise
        """
        if not filename or not filename.strip():
            return False
        
        file_path = self.input_directory / filename
        
        if not file_path.exists():
            return False
        
        extension = file_path.suffix.lower()
        return extension in ['.pdf', '.docx']


# Convenience functions for direct usage
def read_document(filename: str, input_directory: Optional[Path] = None) -> str:
    """Convenience function to read a document.
    
    Args:
        filename: Name of the file to read
        input_directory: Directory containing the file
        
    Returns:
        Document content as markdown string
    """
    reader = DocumentReader(input_directory)
    return reader.read_document(filename)


def list_documents(input_directory: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """Convenience function to list available documents.
    
    Args:
        input_directory: Directory to search for documents
        
    Returns:
        Dictionary of available documents
    """
    reader = DocumentReader(input_directory)
    return reader.list_available_documents() 