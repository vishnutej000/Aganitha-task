"""
Company detection and data processing utilities.
"""

import re
from typing import List
from .research_types import ResearchAuthor
from .company_finder import IndustryDetector


class CompanyDetector:
    """
    Legacy wrapper for backward compatibility.
    Now delegates to the enhanced IndustryDetector.
    """
    
    @classmethod
    def is_pharma_biotech_affiliation(cls, affiliation: str) -> bool:
        """Check if affiliation belongs to pharma/biotech company."""
        return IndustryDetector.is_industry_affiliated(affiliation)
    
    @classmethod
    def extract_company_names(cls, affiliation: str) -> List[str]:
        """Extract company names from affiliation text."""
        return IndustryDetector.extract_company_names(affiliation)


def extract_email_addresses(text: str) -> List[str]:
    """Extract email addresses from text."""
    if not text:
        return []
    
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)


def get_pharma_affiliated_authors(authors: List[ResearchAuthor]) -> List[ResearchAuthor]:
    """Filter authors with pharmaceutical/biotech affiliations."""
    return [
        author for author in authors
        if author.affiliation and IndustryDetector.is_industry_affiliated(author.affiliation)
    ]


def filter_authors_by_company_affiliation(authors: List[ResearchAuthor]) -> List[ResearchAuthor]:
    """Filter authors with pharmaceutical/biotech affiliations."""
    return get_pharma_affiliated_authors(authors)
