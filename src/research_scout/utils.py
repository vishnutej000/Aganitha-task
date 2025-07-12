"""
Company detection and data processing utilities.
"""

import re
from typing import List
from .models import Author


class CompanyDetector:
    """Identifies pharmaceutical and biotech companies from text."""
    
    PHARMA_KEYWORDS = {
        "pharmaceutical", "pharmaceuticals", "pharma", "biotech", "biotechnology",
        "biopharmaceutical", "therapeutics", "medicines", "biopharma",
        "life sciences", "clinical research", "vaccine", "biosciences"
    }
    
    KNOWN_COMPANIES = {
        "pfizer", "novartis", "roche", "merck", "abbott", "bristol myers squibb",
        "johnson & johnson", "glaxosmithkline", "gsk", "sanofi", "astrazeneca",
        "eli lilly", "amgen", "gilead", "biogen", "abbvie", "takeda", "bayer",
        "boehringer ingelheim", "regeneron", "vertex", "moderna", "biontech"
    }
    
    @classmethod
    def is_pharma_biotech_affiliation(cls, affiliation: str) -> bool:
        """Check if affiliation belongs to pharma/biotech company."""
        if not affiliation:
            return False
            
        text = affiliation.lower()
        
        # Check known companies
        if any(company in text for company in cls.KNOWN_COMPANIES):
            return True
        
        # Check pharma keywords
        if any(keyword in text for keyword in cls.PHARMA_KEYWORDS):
            return True
        
        # Check corporate patterns excluding academic institutions
        corporate_indicators = [r'\b(inc\.?|corp\.?|ltd\.?|llc|plc)\b']
        academic_indicators = ["university", "college", "institute", "school", "department"]
        
        has_corporate = any(re.search(pattern, text) for pattern in corporate_indicators)
        has_academic = any(indicator in text for indicator in academic_indicators)
        
        return has_corporate and not has_academic
    
    @classmethod
    def extract_company_names(cls, affiliation: str) -> List[str]:
        """Extract company names from affiliation text."""
        if not cls.is_pharma_biotech_affiliation(affiliation):
            return []
        
        text = affiliation.lower()
        companies = []
        
        # Find known companies
        for company in cls.KNOWN_COMPANIES:
            if company in text:
                companies.append(company.title())
        
        # Extract potential company name if none found
        if not companies:
            company_part = re.split(r'[,;]', affiliation)[0].strip()
            if cls.is_pharma_biotech_affiliation(company_part):
                companies.append(company_part)
        
        return companies


def extract_email_addresses(text: str) -> List[str]:
    """Extract email addresses from text."""
    if not text:
        return []
    
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)


def get_pharma_affiliated_authors(authors: List[Author]) -> List[Author]:
    """Filter authors with pharmaceutical/biotech affiliations."""
    return [
        author for author in authors
        if author.affiliation and CompanyDetector.is_pharma_biotech_affiliation(author.affiliation)
    ]


def filter_authors_by_company_affiliation(authors: List[Author]) -> List[Author]:
    """Filter authors with pharmaceutical/biotech affiliations."""
    return get_pharma_affiliated_authors(authors)
