# PubMed Paper Fetcher

A Python program to fetch research papers from PubMed API that have at least one author affiliated with pharmaceutical or biotech companies. The program returns results as a CSV file with detailed information about papers and their non-academic authors.

## Features

- **PubMed API Integration**: Fetches papers using PubMed's full query syntax
- **Company Detection**: Identifies pharmaceutical and biotech company affiliations using heuristics and known company databases
- **CSV Export**: Outputs results in structured CSV format with required columns
- **Command-line Interface**: Easy-to-use CLI with various options
- **Modular Design**: Separated into reusable module and CLI components
- **Type Safety**: Fully typed Python code for better reliability
- **Error Handling**: Robust error handling for API failures and invalid queries

## Project Structure

```
pubmed-paper-fetcher/
├── src/
│   └── pubmed_fetcher/
│       ├── __init__.py          # Package initialization
│       ├── models.py            # Data models (Paper, Author)
│       ├── fetcher.py           # PubMed API interaction
│       ├── utils.py             # Utility functions (CompanyDetector)
│       ├── csv_export.py        # CSV export functionality
│       └── cli.py               # Command-line interface
├── tests/
│   ├── __init__.py
│   └── test_pubmed_fetcher.py   # Unit tests
├── pyproject.toml               # Poetry configuration
├── README.md                    # This file
└── LICENSE                      # License file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry for dependency management

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vishnutej000/Cloudpac.git
   cd Aganitha-task
   ```

2. **Install dependencies using Poetry:**
   ```bash
   poetry install
   ```

3. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

## Usage

### Command Line Interface

The program provides a command-line tool called `get-papers-list` that can be used after installation.

#### Basic Usage

```bash
# Search for papers and print to console
get-papers-list "cancer treatment"

# Save results to a CSV file
get-papers-list "diabetes AND drug therapy" --file results.csv

# Enable debug mode for detailed output
get-papers-list "COVID-19 vaccine" --debug

# Limit the number of results
get-papers-list "alzheimer disease" --max-results 50 --file alzheimer_papers.csv
```

#### Command Line Options

- `query`: PubMed search query (required, supports full PubMed syntax)
- `-f, --file`: Specify filename to save results (optional, prints to console if not provided)
- `-d, --debug`: Enable debug information during execution
- `--max-results`: Maximum number of papers to fetch (default: 100)
- `--email`: Email address for NCBI API identification (recommended)
- `--api-key`: NCBI API key for higher rate limits
- `-h, --help`: Display usage instructions
- `--version`: Show version information

#### Examples

```bash
# Search with complex PubMed query
get-papers-list "breast cancer[Title] AND (2020:2023[PDAT])" --file recent_breast_cancer.csv

# Search with author email for better API usage
get-papers-list "immunotherapy" --email your.email@example.com --file immuno_papers.csv

# Debug mode to see processing details
get-papers-list "machine learning medicine" --debug --max-results 25
```

### Using as a Python Module

The package can also be used programmatically:

```python
from pubmed_fetcher import PubMedFetcher
from pubmed_fetcher.csv_export import save_papers_to_file

# Initialize the fetcher
fetcher = PubMedFetcher(email="your.email@example.com", debug=True)

# Search and fetch papers
papers = fetcher.search_and_fetch_papers("cancer treatment", max_results=50)

# Save to CSV file
save_papers_to_file(papers, "results.csv")

# Process papers programmatically
for paper in papers:
    print(f"Title: {paper.title}")
    print(f"PubMed ID: {paper.pubmed_id}")
    
    # Get non-academic authors
    from pubmed_fetcher.utils import filter_authors_by_company_affiliation
    company_authors = filter_authors_by_company_affiliation(paper.authors)
    
    for author in company_authors:
        print(f"Author: {author.full_name}")
        print(f"Affiliation: {author.affiliation}")
```

## Output Format

The program outputs CSV files with the following columns:

- **PubmedID**: Unique identifier for the paper
- **Title**: Title of the paper
- **Publication Date**: Date the paper was published (YYYY-MM-DD format)
- **Non-academic Author(s)**: Names of authors affiliated with non-academic institutions (semicolon-separated)
- **Company Affiliation(s)**: Names of pharmaceutical/biotech companies (semicolon-separated)
- **Corresponding Author Email**: Email address of the corresponding author

### Example Output

```csv
PubmedID,Title,Publication Date,Non-academic Author(s),Company Affiliation(s),Corresponding Author Email
12345678,"Novel cancer treatment using targeted therapy",2023-06-15,"Smith JA; Johnson MK","Pfizer; Novartis",smith@pfizer.com
87654321,"Diabetes drug development and clinical trials",2023-08-22,"Brown PR","Johnson & Johnson",brown@jnj.com
```

## Company Detection Logic

The program identifies pharmaceutical and biotech companies using several heuristics:

### 1. Known Company Database
- Maintains a database of major pharmaceutical and biotech companies
- Includes: Pfizer, Novartis, Roche, Merck, Abbott, Bristol Myers Squibb, etc.

### 2. Keyword Detection
- Searches for industry-specific keywords in affiliations:
  - "pharmaceutical", "biotech", "biotechnology", "biopharmaceutical"
  - "therapeutics", "life sciences", "clinical research"
  - "drug", "medicines", "vaccine", "molecular medicine"

### 3. Corporate Structure Indicators
- Identifies corporate entities (Inc., Corp., Ltd., LLC, PLC)
- Excludes academic institutions (University, College, Institute, Department)

### 4. Email Domain Analysis
- Extracts email addresses from author affiliations
- Uses corporate email domains as additional signals

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=pubmed_fetcher

# Run specific test file
poetry run pytest tests/test_pubmed_fetcher.py
```

### Code Quality

The project uses several tools for code quality:

```bash
# Type checking with mypy
poetry run mypy src/pubmed_fetcher

# Code formatting with black
poetry run black src/pubmed_fetcher tests

# Linting with flake8
poetry run flake8 src/pubmed_fetcher tests
```

### API Rate Limits

The PubMed API has rate limits:
- **Without API key**: 3 requests per second
- **With API key**: 10 requests per second

For better performance and reliability:
1. Register for an NCBI account and get an API key
2. Provide your email address when using the tool
3. Use the `--api-key` option or set it programmatically

## Dependencies

### Core Dependencies
- **requests**: HTTP library for API calls
- **click**: Command-line interface framework
- **pandas**: Data manipulation and CSV export
- **typing-extensions**: Enhanced type hints

### Development Dependencies
- **pytest**: Testing framework
- **black**: Code formatting
- **mypy**: Static type checking
- **flake8**: Code linting

## Tools and Resources Used

This project was developed using the following tools and resources:

1. **PubMed API Documentation**: [https://www.ncbi.nlm.nih.gov/books/NBK25499/](https://www.ncbi.nlm.nih.gov/books/NBK25499/)
2. **Poetry**: Dependency management and packaging [https://python-poetry.org/](https://python-poetry.org/)
3. **Click Documentation**: [https://click.palletsprojects.com/](https://click.palletsprojects.com/)
4. **Python Type Hints**: [https://docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html)
5. **GitHub Copilot**: AI-assisted code completion and development

## Error Handling

The program includes comprehensive error handling for:

- **API Failures**: Network timeouts, rate limiting, server errors
- **Invalid Queries**: Malformed PubMed queries
- **Missing Data**: Papers without required fields
- **File I/O Errors**: Permission issues, disk space
- **XML Parsing Errors**: Malformed API responses

## Performance Considerations

- **Batch Processing**: Fetches paper details in batches to optimize API usage
- **Rate Limiting**: Implements exponential backoff for rate limit handling
- **Memory Efficiency**: Processes papers in streams for large result sets
- **Caching**: Session reuse for HTTP connections

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

1. **API Rate Limiting**
   - Solution: Use an API key and email address
   - Add delays between requests if needed

2. **No Results Found**
   - Check your query syntax against PubMed documentation
   - Try broader search terms
   - Verify the papers have pharmaceutical/biotech affiliations

3. **XML Parsing Errors**
   - Usually temporary API issues
   - Retry the request or reduce batch size

4. **Memory Issues with Large Datasets**
   - Reduce `--max-results` parameter
   - Process results in smaller batches

### Getting Help

- Check the [PubMed API documentation](https://www.ncbi.nlm.nih.gov/books/NBK25499/)
- Review the debug output with `--debug` flag
- Submit issues on the GitHub repository

## Future Enhancements

- Add support for additional databases (PMC, bioRxiv)
- Implement result caching for repeated queries
- Add more sophisticated company detection algorithms
- Support for batch processing from file inputs
- Web interface for non-technical users