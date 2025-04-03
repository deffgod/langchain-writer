"""Vector knowledge base package."""

from .db.db_manager import DBManager
from .processors.base_processor import BaseProcessor
from .processors.html_processor import HTMLProcessor
from .processors.json_processor import JSONProcessor
from .processors.pdf_processor import PDFProcessor
from .processors.processor_factory import ProcessorFactory
from .processors.text_processor import TextProcessor

__version__ = "0.1.0"

__all__ = [
    "BaseProcessor",
    "TextProcessor",
    "PDFProcessor",
    "JSONProcessor",
    "HTMLProcessor",
    "ProcessorFactory",
    "DBManager",
]
