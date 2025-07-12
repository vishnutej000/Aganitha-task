
import re
from typing import List, Set
from .research_types import ResearchAuthor

class IndustryDetector:
    """
    Enhanced non-academic author detection system using multiple heuristics:
    1. Known pharmaceutical/biotech company database
    2. Industry-specific keyword detection
    3. Corporate structure analysis
    4. Email domain pattern matching
    5. Academic institution exclusion
    """
    
    INDUSTRY_KEYWORDS = {
        "pharmaceutical", "pharmaceuticals", "pharma", "biotech", "biotechnology",
        "biopharmaceutical", "therapeutics", "medicines", "biopharma",
        "life sciences", "clinical research", "vaccine", "biosciences",
        "drug development", "medical devices", "diagnostics", "molecular medicine",
        "translational medicine", "precision medicine", "personalized medicine",
        "immunotherapy", "gene therapy", "cell therapy", "biologics",
        "small molecules", "clinical trials", "regulatory affairs", "medical affairs"
    }
    
    MAJOR_COMPANIES = {
        "pfizer", "novartis", "roche", "merck", "abbott", "bristol myers squibb", "bms",
        "johnson & johnson", "johnson and johnson", "johnson johnson", "j&j", "janssen", 
        "glaxosmithkline", "gsk", "sanofi", "astrazeneca", "astra zeneca",
        "eli lilly", "lilly", "amgen", "gilead", "biogen", "abbvie", "takeda", "bayer",
        "boehringer ingelheim", "regeneron", "vertex", "moderna", "biontech",
        "immunomedics", "celgene", "genentech", "allergan", "mylan", "teva",
        "novo nordisk", "shire", "alexion", "incyte", "biomarin", "illumina",
        "thermo fisher", "danaher", "medtronic", "edwards lifesciences", "intuitive surgical",
        "merck kgaa", "roche genentech", "novartis pharmaceuticals", "pfizer inc",
        "astrazeneca pharmaceuticals", "bristol-myers squibb", "eli lilly and company",
        "gilead sciences", "biogen inc", "amgen inc", "regeneron pharmaceuticals",
        "vertex pharmaceuticals", "alexion pharmaceuticals", "shire plc"
    }
    
    # Common corporate email domains for pharmaceutical/biotech companies
    INDUSTRY_EMAIL_DOMAINS = {
        "pfizer.com", "novartis.com", "roche.com", "merck.com", "abbott.com",
        "bms.com", "jnj.com", "janssen.com", "gsk.com", "sanofi.com", 
        "astrazeneca.com", "lilly.com", "amgen.com", "gilead.com", "biogen.com",
        "abbvie.com", "takeda.com", "bayer.com", "boehringer-ingelheim.com",
        "regeneron.com", "vrtx.com", "modernatx.com", "biontech.de", "illumina.com",
        "thermofisher.com", "danaher.com", "medtronic.com", "edwards.com"
    }
    
    @classmethod
    def is_industry_affiliated(cls, affiliation: str) -> bool:
        """
        Determines if an affiliation belongs to industry (non-academic).
        
        Uses multiple heuristics:
        1. Known company database matching
        2. Industry keyword detection (excluding academic contexts)
        3. Corporate structure indicators
        4. Email domain analysis
        5. Academic institution exclusion
        
        Args:
            affiliation: The affiliation string to analyze
            
        Returns:
            bool: True if affiliation appears to be industry-affiliated
        """
        if not affiliation:
            return False
            
        text = affiliation.lower().strip()
        
        # FIRST: Check if it's academic - this takes precedence
        if cls._is_academic_context(text):
            return False
        
        # THEN: Check for industry indicators
        # Check for known major companies (highest confidence)
        if cls._has_known_company(text):
            return True
        
        # Check email domains for industry patterns
        if cls._has_industry_email_domain(text):
            return True
        
        # Check for industry keywords
        if cls._has_industry_keywords(text):
            return True
        
        # Check corporate structure indicators
        if cls._is_corporate_non_academic(text):
            return True
        
        # Additional heuristic: R&D centers that are clearly corporate
        if cls._is_corporate_research_facility(text):
            return True
        
        return False
    
    @classmethod
    def _is_academic_context(cls, text: str) -> bool:
        """
        Enhanced academic institution detection.
        
        Identifies various types of academic and research institutions
        to exclude them from industry classification.
        """
        academic_terms = [
            # Universities and colleges
            "university", "universit", "college", "institut", "school", 
            "department", "dept", "faculty", "center", "centre", "laboratory", 
            "lab", "division", "section", "program", "unit",
            
            # Medical and research institutions
            "hospital", "medical center", "clinic", "foundation", "research center",
            "research institute", "cancer center", "medical school", "school of medicine",
            "health center", "health system", "health sciences", "academic medical",
            "mayo clinic", "cleveland clinic", "johns hopkins", "memorial sloan kettering",
            
            # Government and non-profit research
            "national institute", "national center", "nih", "nci", "cdc", "fda",
            "government", "federal", "public health", "ministry of health",
            "research council", "academy of sciences",
            
            # International academic indicators
            "universidad", "université", "universität", "università", "università",
            "instituto", "centre de recherche", "cnrs", "inserm", "max planck",
            "helmholtz", "fraunhofer", "riken", "csiro",
            
            # Education-specific terms
            "graduate school", "undergraduate", "postdoc", "fellowship", "residency",
            
            # Healthcare institutions (non-commercial)
            "veterans administration", "va hospital", "children's hospital",
            "general hospital", "regional hospital", "community hospital"
        ]
        
        # Check for academic terms
        if any(term in text for term in academic_terms):
            return True
            
        # Check for academic email domains
        academic_domains = [".edu", ".ac.", ".university", ".college", ".gov"]
        if any(domain in text for domain in academic_domains):
            return True
        
        # Special patterns for well-known medical institutions
        medical_institution_patterns = [
            r'\bmayo\s+clinic\b',
            r'\bcleveland\s+clinic\b', 
            r'\bjohns\s+hopkins\b',
            r'\bmemorial\s+sloan\s+kettering\b',
            r'\bmount\s+sinai\b',
            r'\bbrigham\s+and\s+women\b',
            r'\bmassachusetts\s+general\b'
        ]
        
        for pattern in medical_institution_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
            
        return False
    
    @classmethod
    def _has_known_company(cls, text: str) -> bool:
        """
        Checks for known pharmaceutical companies using word boundary matching
        to avoid false positives from substrings.
        """
        for company in cls.MAJOR_COMPANIES:
            # Use word boundaries for single-word company names
            if len(company.split()) == 1:
                pattern = r'\b' + re.escape(company) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            else:
                # For multi-word companies, use the original substring approach
                # but be more careful about context
                if company in text:
                    # Additional check: make sure it's not part of a place name
                    # by looking at surrounding context
                    company_index = text.find(company)
                    if company_index != -1:
                        # Check if it's followed by geographic indicators
                        context_after = text[company_index + len(company):company_index + len(company) + 20]
                        geographic_indicators = [', ', ' street', ' avenue', ' road', ' drive', ' blvd']
                        
                        # If followed by geographic indicators, it might be a place name
                        is_place_name = any(indicator in context_after for indicator in geographic_indicators)
                        
                        if not is_place_name:
                            return True
        return False
    
    @classmethod
    def _has_industry_keywords(cls, text: str) -> bool:
        """Checks for industry keywords"""
        return any(keyword in text for keyword in cls.INDUSTRY_KEYWORDS)
    
    @classmethod
    def _has_industry_email_domain(cls, text: str) -> bool:
        """
        Checks if the text contains email addresses from known industry domains.
        """
        # Extract potential email domains from the text
        email_pattern = r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        domains = re.findall(email_pattern, text.lower())
        
        # Check against known industry domains
        for domain in domains:
            if domain in cls.INDUSTRY_EMAIL_DOMAINS:
                return True
            # Also check for partial matches (e.g., subdomain.pfizer.com)
            for industry_domain in cls.INDUSTRY_EMAIL_DOMAINS:
                if industry_domain in domain:
                    return True
        return False
    
    @classmethod
    def _is_corporate_research_facility(cls, text: str) -> bool:
        """
        Identifies corporate R&D centers and research facilities.
        """
        corporate_research_indicators = [
            "r&d", "research and development", "global research", "discovery research",
            "translational research", "clinical development", "drug discovery",
            "pharmaceutical research", "biomedical research", "therapeutic research",
            "innovation center", "technology center", "development center",
            "research site", "research facility", "discovery center"
        ]
        
        # Check for corporate research terms
        has_research_terms = any(term in text for term in corporate_research_indicators)
        
        # Ensure it's not academic (double-check)
        is_academic = cls._is_academic_context(text)
        
        return has_research_terms and not is_academic
    
    @classmethod
    def _is_corporate_non_academic(cls, text: str) -> bool:
        """
        Enhanced corporate structure detection with better academic exclusion.
        """
        # Corporate indicators - expanded list
        corporate_patterns = [
            r'\b(inc\.?|corp\.?|ltd\.?|llc|plc|company|co\.)\b',
            r'\b(corporation|incorporated|limited|technologies|tech|pharma)\b',
            r'\b(therapeutics|biopharmaceuticals|pharmaceuticals|biotech)\b',
            r'\b(group|holding|holdings|ventures|capital)\b'
        ]
        
        has_corporate = any(re.search(pattern, text, re.IGNORECASE) for pattern in corporate_patterns)
        
        # Enhanced academic exclusions
        is_academic = cls._is_academic_context(text)
        
        # Additional check: exclude non-profit research organizations
        nonprofit_indicators = [
            "foundation", "trust", "charity", "non-profit", "nonprofit", 
            "society", "association", "consortium", "alliance", "initiative"
        ]
        is_nonprofit = any(term in text for term in nonprofit_indicators)
        
        return has_corporate and not is_academic and not is_nonprofit
    
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
    """
    Enhanced statistics about industry representation in author list.
    """
    total_authors = len(authors)
    industry_authors = find_industry_authors(authors)
    industry_count = len(industry_authors)
    
    # Extract companies and their frequencies
    companies = []
    company_frequencies = {}
    email_domains = set()
    
    for author in industry_authors:
        if author.affiliation:
            company_names = IndustryDetector.extract_company_names(author.affiliation)
            companies.extend(company_names)
            
            for company in company_names:
                company_frequencies[company] = company_frequencies.get(company, 0) + 1
        
        # Extract email domains for additional analysis
        if author.email:
            domain = author.email.split('@')[-1].lower() if '@' in author.email else ''
            if domain:
                email_domains.add(domain)
    
    # Determine confidence level based on detection methods
    high_confidence_count = 0
    for author in industry_authors:
        if author.affiliation:
            text = author.affiliation.lower()
            # High confidence if known company or industry email domain
            if (IndustryDetector._has_known_company(text) or 
                IndustryDetector._has_industry_email_domain(text)):
                high_confidence_count += 1
    
    return {
        "total_authors": total_authors,
        "industry_authors": industry_count,
        "industry_percentage": (industry_count / total_authors * 100) if total_authors > 0 else 0,
        "unique_companies": len(set(companies)),
        "company_names": sorted(list(set(companies))),
        "company_frequencies": company_frequencies,
        "industry_email_domains": sorted(list(email_domains)),
        "high_confidence_detections": high_confidence_count,
        "confidence_rate": (high_confidence_count / industry_count * 100) if industry_count > 0 else 0
    }


def analyze_affiliation_patterns(authors: List[ResearchAuthor]) -> dict:
    """
    Analyzes patterns in affiliations to provide insights into detection quality.
    """
    total_affiliations = sum(1 for author in authors if author.affiliation)
    academic_count = 0
    industry_count = 0
    unclear_count = 0
    
    # Pattern analysis
    detection_methods = {
        "known_company": 0,
        "industry_keywords": 0, 
        "corporate_structure": 0,
        "email_domain": 0,
        "research_facility": 0
    }
    
    for author in authors:
        if not author.affiliation:
            continue
            
        text = author.affiliation.lower()
        
        if IndustryDetector._is_academic_context(text):
            academic_count += 1
        elif IndustryDetector.is_industry_affiliated(author.affiliation):
            industry_count += 1
            
            # Track which method detected it
            if IndustryDetector._has_known_company(text):
                detection_methods["known_company"] += 1
            elif IndustryDetector._has_industry_email_domain(text):
                detection_methods["email_domain"] += 1
            elif IndustryDetector._has_industry_keywords(text):
                detection_methods["industry_keywords"] += 1
            elif IndustryDetector._is_corporate_non_academic(text):
                detection_methods["corporate_structure"] += 1
            elif IndustryDetector._is_corporate_research_facility(text):
                detection_methods["research_facility"] += 1
        else:
            unclear_count += 1
    
    return {
        "total_affiliations": total_affiliations,
        "academic_affiliations": academic_count,
        "industry_affiliations": industry_count,
        "unclear_affiliations": unclear_count,
        "detection_methods": detection_methods,
        "academic_percentage": (academic_count / total_affiliations * 100) if total_affiliations > 0 else 0,
        "industry_percentage": (industry_count / total_affiliations * 100) if total_affiliations > 0 else 0
    }
