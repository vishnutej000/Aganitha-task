
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
        "pfizer", "novartis", "roche", "merck", "abbott", "bristol myers squibb", "bms",
        "johnson & johnson", "johnson and johnson", "johnson johnson", "j&j", "janssen", 
        "glaxosmithkline", "gsk", "sanofi", "astrazeneca", "astra zeneca",
        "eli lilly", "lilly", "amgen", "gilead", "biogen", "abbvie", "takeda", "bayer",
        "boehringer ingelheim", "regeneron", "vertex", "moderna", "biontech",
        "immunomedics", "celgene", "genentech", "allergan", "mylan", "teva",
        "novo nordisk", "shire", "alexion", "incyte", "biomarin", "illumina",
        "thermo fisher", "danaher", "medtronic", "edwards lifesciences", "intuitive surgical"
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
        
        # Check for industry keywords BUT exclude academic contexts
        if cls._has_industry_keywords(text) and not cls._is_academic_context(text):
            return True
        
        # Check corporate structure indicators (but exclude academia)
        if cls._is_corporate_non_academic(text):
            return True
        
        return False
    
    @classmethod
    def _is_academic_context(cls, text: str) -> bool:
        # More comprehensive academic exclusions
        academic_terms = [
            "university", "college", "institute", "school", "department",
            "faculty", "center", "centre", "laboratory", "lab", "hospital",
            "medical center", "clinic", "foundation", "research center",
            "dept", "division", "section", "program", "unit"
        ]
        return any(term in text for term in academic_terms)
    
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
        if not cls.is_industry_affiliated(affiliation):
            return []
        
        text = affiliation.lower()
        found_companies = []
        
        # Look for known companies first (this is most reliable)
        for company in cls.MAJOR_COMPANIES:
            if company in text:
                proper_name = cls._get_proper_company_name(company)
                if proper_name not in found_companies:
                    found_companies.append(proper_name)
        
        # If no known companies found, extract based on keywords and corporate structure
        # This matches the original task requirements
        if not found_companies:
            # Look for pharmaceutical/biotech keywords and extract nearby text
            for keyword in cls.INDUSTRY_KEYWORDS:
                if keyword in text:
                    # Find the part of affiliation containing the keyword
                    parts = re.split(r'[,;]', affiliation)
                    for part in parts:
                        if keyword in part.lower() and not cls._is_academic_context(part.lower()):
                            clean_name = cls._clean_company_name(part.strip())
                            if clean_name and clean_name not in found_companies:
                                found_companies.append(clean_name)
                            break
                    break
            
            # Also check for corporate structure indicators
            if not found_companies and cls._is_corporate_non_academic(text):
                # Extract potential company name from corporate affiliation
                potential_name = cls._extract_potential_company_name(affiliation)
                if potential_name and not cls._is_academic_context(potential_name.lower()):
                    found_companies.append(potential_name)
        
        return found_companies
    
    @classmethod
    def _clean_company_name(cls, company_text: str) -> str:
        # Clean up company name by removing locations and common suffixes
        # Remove content in parentheses
        clean = re.sub(r'\([^)]*\)', '', company_text)
        # Remove common location patterns
        clean = re.sub(r',\s*[A-Z]{2,}\s*\d*$', '', clean)  # Remove state/country codes
        clean = re.sub(r',\s*[A-Za-z\s]+,\s*[A-Z]{2,}$', '', clean)  # Remove city, state
        
        # Take first meaningful part that contains the company info
        parts = re.split(r'[,;-]', clean)
        for part in parts:
            part = part.strip()
            # Skip parts that are clearly academic
            if cls._is_academic_context(part.lower()):
                continue
            # If this part has industry keywords or corporate indicators, use it
            if (any(keyword in part.lower() for keyword in cls.INDUSTRY_KEYWORDS) or 
                any(re.search(pattern, part.lower()) for pattern in [r'\b(inc\.?|corp\.?|ltd\.?|llc|plc|company|co\.)\b'])):
                # Remove common corporate suffixes for cleaner display
                result = re.sub(r'\s+(Inc\.?|Corp\.?|Ltd\.?|LLC|Company|Co\.?)$', '', part, flags=re.IGNORECASE)
                return result.strip()
        
        # If no good part found, return the first part cleaned up
        if parts:
            result = parts[0].strip()
            result = re.sub(r'\s+(Inc\.?|Corp\.?|Ltd\.?|LLC|Company|Co\.?)$', '', result, flags=re.IGNORECASE)
            return result.strip()
        
        return clean.strip()
    
    @classmethod
    def _get_proper_company_name(cls, company_key: str) -> str:
        # Converts company key to proper display name
        name_mapping = {
            "johnson & johnson": "Johnson & Johnson",
            "johnson and johnson": "Johnson & Johnson", 
            "j&j": "Johnson & Johnson",
            "janssen": "Johnson & Johnson (Janssen)",
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
