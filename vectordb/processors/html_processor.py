import logging
from typing import Dict, List

from bs4 import BeautifulSoup

from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class HTMLProcessor(BaseProcessor):
    """Processor for HTML files."""

    def __init__(self, file_path: str, extract_tags: List[str] = None):
        """Initialize HTML processor.

        Args:
            file_path: Path to HTML file
            extract_tags: List of HTML tags to extract text from (if None, extracts from all tags)
        """
        super().__init__(file_path)
        self.extract_tags = extract_tags or [
            "p",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "div",
            "span",
            "article",
        ]
        self.soup = None

    def _load_html(self) -> None:
        """Load HTML content and create BeautifulSoup object."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.soup = BeautifulSoup(content, "html.parser")
        except Exception as e:
            logger.error(f"Error loading HTML file {self.file_path}: {str(e)}")
            raise

    def _extract_text_from_tag(self, tag) -> str:
        """Extract text from a specific HTML tag.

        Args:
            tag: BeautifulSoup tag object

        Returns:
            str: Extracted text
        """
        # Remove script and style elements
        for element in tag.find_all(["script", "style"]):
            element.decompose()

        # Get text and clean it
        text = tag.get_text(strip=True)
        return text if text else ""

    def extract_text(self) -> str:
        """Extract text content from HTML file.

        Returns:
            str: Extracted text content
        """
        if not self.soup:
            self._load_html()

        try:
            texts = []

            # Extract title if present
            title = self.soup.title
            if title and title.string:
                texts.append(f"Title: {title.string.strip()}")

            # Extract meta description if present
            meta_desc = self.soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                texts.append(f"Description: {meta_desc['content'].strip()}")

            # Extract text from specified tags
            for tag_name in self.extract_tags:
                for tag in self.soup.find_all(tag_name):
                    text = self._extract_text_from_tag(tag)
                    if text:
                        texts.append(f"{tag_name}: {text}")

            return "\n\n".join(texts)

        except Exception as e:
            logger.error(f"Error extracting text from HTML {self.file_path}: {str(e)}")
            raise

    def extract_metadata(self) -> Dict:
        """Extract metadata from HTML file.

        Returns:
            Dict: Extracted metadata
        """
        if not self.soup:
            self._load_html()

        try:
            metadata = {
                "title": self.soup.title.string.strip() if self.soup.title else "",
                "charset": self._get_charset(),
                "links": len(self.soup.find_all("a")),
                "images": len(self.soup.find_all("img")),
                "scripts": len(self.soup.find_all("script")),
                "styles": len(self.soup.find_all("link", rel="stylesheet"))
                + len(self.soup.find_all("style")),
                "meta_tags": self._extract_meta_tags(),
            }

            return {k: v for k, v in metadata.items() if v}

        except Exception as e:
            logger.error(
                f"Error extracting metadata from HTML {self.file_path}: {str(e)}"
            )
            raise

    def _get_charset(self) -> str:
        """Get character encoding from HTML.

        Returns:
            str: Character encoding
        """
        # Check meta charset
        meta_charset = self.soup.find("meta", charset=True)
        if meta_charset:
            return meta_charset["charset"]

        # Check content-type meta
        meta_content_type = self.soup.find("meta", {"http-equiv": "Content-Type"})
        if meta_content_type and "charset=" in meta_content_type.get("content", ""):
            return meta_content_type["content"].split("charset=")[-1]

        return "utf-8"  # Default charset

    def _extract_meta_tags(self) -> Dict:
        """Extract metadata from meta tags.

        Returns:
            Dict: Metadata from meta tags
        """
        meta_data = {}

        for meta in self.soup.find_all("meta"):
            name = meta.get("name", "").lower()
            content = meta.get("content", "")

            if name and content:
                meta_data[name] = content

        return meta_data
