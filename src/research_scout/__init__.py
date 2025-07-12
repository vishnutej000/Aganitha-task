"""
Research Scout - Non-Academic Author Detection Module

A Python library for identifying pharmaceutical and biotech industry authors 
in research papers, with advanced heuristics for distinguishing academic 
from industry affiliations.
"""

__version__ = "0.1.0"
__author__ = "Research Scout Team"

# Core data types
from .research_types import ResearchAuthor, ResearchPaper, SearchRequest, SearchResults

# Industry detection system
from .company_finder import (
    IndustryDetector, 
    find_industry_authors, 
    extract_email_contacts,
    get_industry_statistics,
    analyze_affiliation_patterns
)

# Paper fetching
from .paper_hunter import PaperHunter, PubMedConnectionError, PubMedSearchError

# Data export utilities
from .data_writer import (
    save_research_results,
    generate_filename_from_query,
    create_research_summary,
    display_papers_as_table,
    export_detailed_results
)

# Legacy compatibility
from .utils import CompanyDetector, extract_email_addresses

# Main module API
__all__ = [
    # Core data types
    "ResearchAuthor",
    "ResearchPaper", 
    "SearchRequest",
    "SearchResults",
    
    # Industry detection
    "IndustryDetector",
    "find_industry_authors",
    "extract_email_contacts", 
    "get_industry_statistics",
    "analyze_affiliation_patterns",
    
    # Paper fetching
    "PaperHunter",
    "PubMedConnectionError",
    "PubMedSearchError",
    
    # Data export
    "save_research_results",
    "generate_filename_from_query",
    "create_research_summary",
    "display_papers_as_table",
    "export_detailed_results",
    
    # Legacy compatibility
    "CompanyDetector",
    "extract_email_addresses",
]