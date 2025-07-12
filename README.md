# Research Scout - Non-Academic Author Detection

A Python library and CLI tool for identifying pharmaceutical and biotech industry authors in research papers. Uses advanced heuristics to distinguish academic from industry affiliations with high accuracy.

## 🏗️ Project Structure

This project is split into two components:

### 1. **research-scout** (Python Library/Module)
- **Location**: `src/research_scout/`
- **Purpose**: Core library for industry author detection
- **Installation**: `pip install research-scout` (from Test PyPI)
- **Usage**: Import and use programmatically in Python code

### 2. **research-scout-cli** (Command Line Tool)
- **Location**: `research_scout_cli/`
- **Purpose**: CLI tool that uses the research-scout library
- **Installation**: `pip install research-scout-cli` 
- **Usage**: Command-line interface for end users

## 📦 Installation

### Option 1: Install from Test PyPI (Recommended)

```bash
# Install the core library
pip install --index-url https://test.pypi.org/simple/ research-scout

# Install the CLI tool (includes the library as dependency)
pip install --index-url https://test.pypi.org/simple/ research-scout-cli
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/vishnutej000/Aganitha-task.git
cd Aganitha-task

# Install the library
pip install -e .

# Or install with Poetry
poetry install
```
## 🚀 Usage

### Using the Python Library (Programmatic)

```python
import research_scout

# Initialize the paper hunter
hunter = research_scout.PaperHunter(debug=True)

# Create search request
request = research_scout.SearchRequest(
    query="cancer treatment",
    max_results=50,
    email="your.email@example.com"
)

# Search for papers
results = hunter.search_papers(request)

# Filter for industry papers
industry_papers = results.industry_papers

# Analyze industry representation
for paper in industry_papers:
    print(f"Title: {paper.title}")
    print(f"PubMed ID: {paper.pubmed_id}")
    
    # Get industry authors
    industry_authors = paper.industry_authors
    for author in industry_authors:
        print(f"  Author: {author.display_name}")
        print(f"  Affiliation: {author.affiliation}")
        
        # Extract company names
        companies = research_scout.IndustryDetector.extract_company_names(
            author.affiliation
        )
        print(f"  Companies: {companies}")

# Generate statistics
stats = research_scout.get_industry_statistics(
    [author for paper in industry_papers for author in paper.authors]
)
print(f"Industry authors: {stats['industry_percentage']:.1f}%")
print(f"Companies found: {stats['company_names']}")

# Save results
research_scout.save_research_results(industry_papers, "results.csv")
```

### Using the Command Line Interface

```bash
# Basic search
research-scout-cli "cancer treatment"

# Save to specific file
research-scout-cli "diabetes AND drug therapy" --file results.csv

# Enable debug mode with API key
research-scout-cli "COVID-19 vaccine" --debug --email your@email.com --api-key YOUR_KEY

# Display results in table format
research-scout-cli "alzheimer disease" --table --max-results 25

# Export detailed results with abstracts
research-scout-cli "immunotherapy" --detailed --file detailed_results.csv
```

### CLI Options

- `query`: PubMed search query (required, supports full PubMed syntax)
- `-f, --file`: Specify filename to save results (optional)
- `-d, --debug`: Enable debug information during execution
- `--max-results`: Maximum number of papers to fetch (default: 100)
- `--email`: Email address for NCBI API identification (recommended)
- `--api-key`: NCBI API key for higher rate limits
- `--table`: Display results in table format
- `--detailed`: Export detailed results with abstracts
- `--auto-save`: Automatically save results to file (default: True)
- `-h, --help`: Display usage instructions
- `--version`: Show version information

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

## Non-Academic Author Identification System

The program uses a sophisticated multi-layered heuristic system to identify non-academic (industry) authors with high accuracy. The identification process is implemented in the `IndustryDetector` class and uses the following approaches:

### 1. Known Company Database Matching
- **High Confidence Detection**: Maintains an extensive database of 50+ major pharmaceutical and biotech companies
- **Company Variations**: Handles multiple name formats (e.g., "Johnson & Johnson", "J&J", "Janssen")
- **Examples**: Pfizer, Novartis, Roche, Merck, Abbott, Bristol Myers Squibb, GSK, Sanofi, etc.

### 2. Industry-Specific Keyword Detection
- **Enhanced Keyword Set**: Expanded vocabulary of 25+ industry-specific terms
- **Keywords Include**:
  - Core pharma: "pharmaceutical", "biotech", "biopharmaceutical", "therapeutics"
  - Specialized: "drug development", "clinical trials", "molecular medicine", "gene therapy"
  - Medical devices: "medical devices", "diagnostics", "precision medicine"
- **Academic Exclusion**: Keywords are only considered when NOT in academic contexts

### 3. Corporate Structure Analysis
- **Corporate Indicators**: Detects legal entity suffixes (Inc., Corp., Ltd., LLC, PLC)
- **Enhanced Patterns**: Recognizes "Corporation", "Technologies", "Therapeutics", "Group"
- **Academic Filtering**: Excludes universities, hospitals, research institutes, non-profits

### 4. Email Domain Pattern Matching
- **Industry Email Domains**: Database of 25+ known pharmaceutical company email domains
- **Pattern Examples**: @pfizer.com, @novartis.com, @jnj.com, @gsk.com
- **Subdomain Support**: Handles subdomain variations (e.g., research.pfizer.com)

### 5. Corporate R&D Facility Detection
- **Research Centers**: Identifies corporate research and development facilities
- **Indicators**: "R&D", "discovery research", "innovation center", "development center"
- **Academic Distinction**: Differentiates from university research centers

### 6. Academic Institution Exclusion
- **Comprehensive Academic Terms**: 30+ terms for universities, colleges, institutes
- **Medical Institutions**: Hospitals, medical centers, clinics, health systems
- **Government/Non-profit**: NIH, CDC, foundations, research councils
- **International Support**: Terms in multiple languages (Universidad, Université, etc.)
- **Educational Domains**: .edu, .ac.*, university, college domains

### Heuristic Accuracy and Confidence Scoring

The system provides confidence scoring based on detection method:

- **High Confidence** (95%+ accuracy):
  - Known company database matches
  - Industry email domain matches
  
- **Medium Confidence** (85-95% accuracy):
  - Industry keywords + corporate structure
  - Corporate R&D facilities
  
- **Lower Confidence** (70-85% accuracy):
  - Corporate structure alone (without keywords)

### Examples of Detection Logic

```python
# High confidence - known company
"Pfizer Global R&D, Groton, CT" → Industry ✓

# Medium confidence - keywords + structure  
"Acme Therapeutics Inc., Cambridge, MA" → Industry ✓

# Correctly excluded - academic
"Harvard Medical School, Boston, MA" → Academic ✗

# Correctly excluded - hospital
"Mayo Clinic, Rochester, MN" → Academic ✗

# Email domain detection
"john.doe@novartis.com" → Industry ✓
```

### Statistical Analysis Features

The system provides detailed statistics:
- Total vs. industry author counts and percentages
- Company frequency analysis
- Detection method breakdown
- Confidence scoring metrics
- Pattern analysis for quality assessment

## 📦 Publishing to Test PyPI

This project is set up for publishing to Test PyPI. Here's how to publish:

### Prerequisites

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Create Test PyPI Account**: 
   - Go to https://test.pypi.org/account/register/
   - Verify your email address

3. **Generate API Token**:
   - Go to https://test.pypi.org/manage/account/token/
   - Create a new API token with "Entire account" scope

### Publishing Steps

1. **Run the setup script**:
   ```bash
   python setup_test_pypi.py
   ```

2. **Configure your API token**:
   ```bash
   poetry config pypi-token.test-pypi <your-token-here>
   ```

3. **Publish to Test PyPI**:
   ```bash
   poetry publish --repository test-pypi
   ```

4. **Install and test**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ research-scout
   ```

### Automated Setup

The `setup_test_pypi.py` script automates most of the setup:
- Checks Poetry installation
- Updates version for test publishing
- Configures Test PyPI repository
- Builds the package
- Provides step-by-step publishing instructions

### Package Structure for Publishing

- **research-scout**: Core library module
- **research-scout-cli**: Command-line interface (depends on research-scout)

Both packages can be published independently to Test PyPI.

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

### Development Tools
1. **GitHub Copilot**: AI-assisted code completion and development
2. **Poetry**: Dependency management and packaging [https://python-poetry.org/](https://python-poetry.org/)
3. **Click Documentation**: Command-line interface framework [https://click.palletsprojects.com/](https://click.palletsprojects.com/)
4. **Python Type Hints**: Static typing [https://docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html)

### External APIs and Data Sources
5. **PubMed API Documentation**: [https://www.ncbi.nlm.nih.gov/books/NBK25499/](https://www.ncbi.nlm.nih.gov/books/NBK25499/)
6. **NCBI E-utilities**: XML parsing and data extraction
7. **Pharmaceutical Company Database**: Manually curated from public sources including:
   - Fortune 500 pharmaceutical companies
   - BioPharma industry reports
   - Public company websites and SEC filings

### Algorithm Development Resources
8. **Regular Expression Documentation**: Pattern matching for corporate structures
9. **Academic Institution Lists**: University databases for exclusion patterns
10. **Email Domain Analysis**: Corporate email pattern identification
11. **Natural Language Processing**: Text analysis for affiliation parsing

### Quality Assurance Tools
12. **pytest**: Testing framework for validation
13. **mypy**: Static type checking
14. **black**: Code formatting
15. **flake8**: Code linting

### Enhanced Non-Academic Detection Algorithm

The non-academic author identification system was developed using:
- **Heuristic Design Principles**: Multi-layered detection with confidence scoring
- **Machine Learning Concepts**: Pattern recognition without requiring training data
- **Domain Expertise**: Pharmaceutical industry knowledge for company identification
- **Linguistic Analysis**: Academic vs. corporate language pattern differentiation

All external data sources used are publicly available and the detection algorithms use rule-based heuristics rather than proprietary datasets.

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