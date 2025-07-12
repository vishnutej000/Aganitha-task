
import re
from typing import List, Set
from .research_types import ResearchAuthor

class IndustryDetector:
    
    INDUSTRY_KEYWORDS = {
        "pharmaceutical", "pharmaceuticals", "pharma", "biotech", "biotechnology",
        "biopharmaceutical", "therapeutics", "medicines", "biopharma",
        "life sciences", "clinical research", "vaccine", "biosciences",
        "drug development", "medical devices", "diagnostics"
    }
    
    MAJOR_COMPANIES = {
        "pfizer", "novartis", "roche", "merck", "abbott", "bristol myers squibb",
        "johnson & johnson", "glaxosmithkline", "gsk", "sanofi", "astrazeneca",
        "eli lilly", "amgen", "gilead", "biogen", "abbvie", "takeda", "bayer",
        "boehringer ingelheim", "regeneron", "vertex", "moderna", "biontech",
        "immunomedics", "celgene", "genentech", "allergan", "mylan"
    }
    
    @classmethod
    def is_industry_affiliated(cls, affiliation: str) -> bool:
        # Returns True if the affiliation appears to be from industry
        if not affiliation:
            return False
            
        text = affiliation.lower().strip()
        
        # Check for known major companies
        if cls._has_known_company(text):
            return True
        
        # Check for industry keywords
        if cls._has_industry_keywords(text):
            return True
        
        # Check corporate structure indicators (but exclude academia)
        if cls._is_corporate_non_academic(text):
            return True
        
        return False
    
    @classmethod
    def _has_known_company(cls, text: str) -> bool:
        # Checks for known pharmaceutical companies
        return any(company in text for company in cls.MAJOR_COMPANIES)
    
    @classmethod
    def _has_industry_keywords(cls, text: str) -> bool:
        # Checks for industry keywords
        return any(keyword in text for keyword in cls.INDUSTRY_KEYWORDS)
    
    @classmethod
    def _is_corporate_non_academic(cls, text: str) -> bool:
        # Checks for corporate structure, excluding academic
        # Corporate indicators
        corporate_patterns = [r'\b(inc\.?|corp\.?|ltd\.?|llc|plc|company|co\.)\b']
        has_corporate = any(re.search(pattern, text) for pattern in corporate_patterns)
        
        # Academic exclusions
        academic_terms = [
            "university", "college", "institute", "school", "department",
            "faculty", "center", "centre", "laboratory", "lab", "hospital",
            "medical center", "clinic", "foundation"
        ]
        has_academic = any(term in text for term in academic_terms)
        
        return has_corporate and not has_academic
    
    @classmethod
    def extract_company_names(cls, affiliation: str) -> List[str]:
        # Extracts potential company names from an affiliation string
        if not cls.is_industry_affiliated(affiliation):
            return []
        
        text = affiliation.lower()
        found_companies = []
        
        # Look for known companies first
        for company in cls.MAJOR_COMPANIES:
            if company in text:
                # Get the proper case version
                proper_name = cls._get_proper_company_name(company)
                found_companies.append(proper_name)
        
        # If no known companies found, try to extract from structure
        if not found_companies:
            potential_name = cls._extract_potential_company_name(affiliation)
            if potential_name:
                found_companies.append(potential_name)
        
        return found_companies
    
    @classmethod
    def _get_proper_company_name(cls, company_key: str) -> str:
        # Converts company key to proper display name
        name_mapping = {
            "johnson & johnson": "Johnson & Johnson",
            "glaxosmithkline": "GlaxoSmithKline",
            "gsk": "GSK",
            "bristol myers squibb": "Bristol Myers Squibb",
            "eli lilly": "Eli Lilly",
            "boehringer ingelheim": "Boehringer Ingelheim"
        }
        return name_mapping.get(company_key, company_key.title())
    
    @classmethod
    def _extract_potential_company_name(cls, affiliation: str) -> str:
        # Tries to extract a company name from the affiliation text
        # Take the first part before comma or semicolon
        parts = re.split(r'[,;]', affiliation)
        if parts:
            potential_name = parts[0].strip()
            # Remove common location indicators
            potential_name = re.sub(r'\b(usa?|uk|eu|inc\.?|corp\.?|ltd\.?)$', '', 
                                  potential_name, flags=re.IGNORECASE).strip()
            return potential_name
        return affiliation.strip()


def find_industry_authors(authors: List[ResearchAuthor]) -> List[ResearchAuthor]:
    # Returns authors with industry affiliations
    industry_authors = []
    for author in authors:
        if author.affiliation and IndustryDetector.is_industry_affiliated(author.affiliation):
            industry_authors.append(author)
    return industry_authors


def extract_email_contacts(text: str) -> List[str]:
    # Extracts email addresses from text
    if not text:
        return []
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Remove duplicates while preserving order
    unique_emails = []
    seen = set()
    for email in emails:
        if email.lower() not in seen:
            unique_emails.append(email)
            seen.add(email.lower())
    
    return unique_emails


def get_industry_statistics(authors: List[ResearchAuthor]) -> dict:
    # Generates statistics about industry representation in author list
    total_authors = len(authors)
    industry_authors = find_industry_authors(authors)
    industry_count = len(industry_authors)
    
    # Extract companies
    companies = set()
    for author in industry_authors:
        if author.affiliation:
            company_names = IndustryDetector.extract_company_names(author.affiliation)
            companies.update(company_names)
    
    return {
        "total_authors": total_authors,
        "industry_authors": industry_count,
        "industry_percentage": (industry_count / total_authors * 100) if total_authors > 0 else 0,
        "unique_companies": len(companies),
        "company_names": sorted(list(companies))
    }
