# Vector Knowledge Base with Writer Integration

This project implements a vector knowledge base using ChromaDB and integrates it with Writer's Knowledge Graph functionality for enhanced information retrieval.

## Features

- Process multiple file formats (PDF, JSON, HTML)
- Vector-based document search using ChromaDB
- Integration with Writer's Knowledge Graph
- Combined search results from both vector database and knowledge graph
- Comprehensive error handling and logging
- Command-line interface for queries

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd vectordb
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Writer API credentials:
```env
WRITER_API_KEY="your-api-key"
GRAPH_IDS="your-graph-id"
```

## Usage

### Process Documents

To create the vector database from your documents:

```bash
python process_data.py
```

This will:
- Scan the `docs/data` directory for supported files
- Process each file and extract text and metadata
- Store the documents in ChromaDB

### Query the Database

To query only the vector database:

```bash
python query_db.py "your query here"
```

Options:
- `--collection/-c`: Specify collection name (default: "neurofitness")
- `--results/-n`: Number of results to return (default: 5)
- `--db-dir/-d`: Database directory (default: "vectordb/data")

### Combined Search

To query both the vector database and Writer's Knowledge Graph:

```bash
python writer_integration.py
```

This will:
- Query the Writer Knowledge Graph
- Search the vector database
- Combine and format the results

## Project Structure

```
vectordb/
├── processors/
│   ├── base_processor.py
│   ├── pdf_processor.py
│   ├── json_processor.py
│   └── html_processor.py
├── db/
│   └── db_manager.py
├── data/
├── process_data.py
├── query_db.py
├── writer_integration.py
└── requirements.txt
```

## File Processors

- `PDFProcessor`: Handles PDF files using PyPDF2
- `JSONProcessor`: Processes JSON files with text field extraction
- `HTMLProcessor`: Extracts text from HTML files using BeautifulSoup

## Database Manager

The `DBManager` class provides:
- Collection management
- Document addition
- Query functionality
- Metadata filtering

## Writer Integration

The `WriterIntegration` class offers:
- Knowledge graph queries
- Combined search results
- Configurable model parameters

## Error Handling

The system includes comprehensive error handling for:
- File processing errors
- Database operations
- API communication
- Invalid input formats

## Logging

Detailed logging is implemented for:
- File processing status
- Database operations
- Query execution
- Error tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
