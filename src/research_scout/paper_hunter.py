import requests
import xml.etree.ElementTree as ET
from typing import List, Optional
from datetime import datetime
from .research_types import SearchRequest, SearchResults, ResearchPaper, ResearchAuthor
from .company_finder import IndustryDetector
import re

class PubMedConnectionError(Exception):
    pass

class PubMedSearchError(Exception):
    pass

class PaperHunter:
    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        self.email = email
        self.api_key = api_key
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        
    def hunt_papers(self, request: SearchRequest) -> SearchResults:
        try:
            # Step 1: Search for paper IDs
            paper_ids = self._search_papers(request.query, request.max_results, request.debug_mode)
            
            if not paper_ids:
                return SearchResults(papers=[], total_found=0, query_used=request.query)
            
            if request.debug_mode:
                print(f"[DEBUG] Found {len(paper_ids)} papers")
            
            # Step 2: Fetch paper details
            papers = self._fetch_paper_details(paper_ids, request.debug_mode)
            
            # Step 3: Filter for industry affiliations
            industry_papers = [p for p in papers if p.has_industry_collaboration]
            
            if request.debug_mode:
                print(f"[DEBUG] Found {len(industry_papers)} papers with pharma/biotech affiliations")
            
            return SearchResults(
                papers=industry_papers,
                total_found=len(paper_ids),
                query_used=request.query,
                search_time=datetime.now()
            )
            
        except requests.RequestException as e:
            raise PubMedConnectionError(f"Failed to connect to PubMed: {str(e)}")
        except Exception as e:
            raise PubMedSearchError(f"Search failed: {str(e)}")
    
    def _search_papers(self, query: str, max_results: int, debug: bool) -> List[str]:
        # Try multiple query variations for better results
        queries_to_try = self._generate_query_variations(query)
        all_paper_ids = set()
        
        for search_query in queries_to_try:
            params = {
                'db': 'pubmed',
                'term': search_query,
                'retmax': str(max_results),
                'retmode': 'json',
                'sort': 'relevance'
            }
            
            if self.email:
                params['email'] = self.email
            if self.api_key:
                params['api_key'] = self.api_key
            
            if debug:
                print(f"[DEBUG] Searching for papers with query: {search_query}")
                print(f"[DEBUG] Making request to {self.base_url}/esearch.fcgi with params: {params}")
            
            try:
                response = requests.get(f"{self.base_url}/esearch.fcgi", params=params)
                response.raise_for_status()
                
                data = response.json()
                paper_ids = data.get('esearchresult', {}).get('idlist', [])
                all_paper_ids.update(paper_ids)
                
                if debug:
                    print(f"[DEBUG] Found {len(paper_ids)} papers for query: {search_query}")
                
                # If we get enough results, stop trying more variations
                if len(all_paper_ids) >= max_results:
                    break
                    
            except Exception as e:
                if debug:
                    print(f"[DEBUG] Query failed: {search_query} - {e}")
                continue
        
        final_ids = list(all_paper_ids)[:max_results]
        if debug:
            print(f"[DEBUG] Total unique papers found: {len(final_ids)}")
        
        return final_ids
    
    def _generate_query_variations(self, query: str) -> List[str]:
        """Generate multiple query variations to improve search results"""
        variations = [query]  # Always start with original query
        
        # Common company name variations
        company_variations = {
            'johnson johnson': ['johnson & johnson', 'j&j', 'janssen'],
            'johnson & johnson': ['johnson johnson', 'j&j', 'janssen'],
            'j&j': ['johnson & johnson', 'johnson johnson', 'janssen'],
            'glaxosmithkline': ['gsk'],
            'gsk': ['glaxosmithkline'],
            'bristol myers squibb': ['bms'],
            'eli lilly': ['lilly'],
        }
        
        query_lower = query.lower()
        for original, alternates in company_variations.items():
            if original in query_lower:
                for alternate in alternates:
                    new_query = query_lower.replace(original, alternate)
                    if new_query != query_lower:
                        variations.append(new_query)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for var in variations:
            if var.lower() not in seen:
                unique_variations.append(var)
                seen.add(var.lower())
        
        return unique_variations[:3]  # Limit to 3 variations to avoid too many API calls
    
    def _fetch_paper_details(self, paper_ids: List[str], debug: bool) -> List[ResearchPaper]:
        if not paper_ids:
            return []
        
        params = {
            'db': 'pubmed',
            'id': ','.join(paper_ids),
            'retmode': 'xml',
            'rettype': 'abstract'
        }
        
        if self.email:
            params['email'] = self.email
        if self.api_key:
            params['api_key'] = self.api_key
        
        if debug:
            print(f"[DEBUG] Fetching details for {len(paper_ids)} papers")
            print(f"[DEBUG] Making request to {self.base_url}/efetch.fcgi with params: {params}")
        
        response = requests.get(f"{self.base_url}/efetch.fcgi", params=params)
        response.raise_for_status()
        
        return self._parse_pubmed_xml(response.text)
    
    def _parse_pubmed_xml(self, xml_content: str) -> List[ResearchPaper]:
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                paper = self._parse_single_article(article)
                if paper:
                    # Additional email extraction from the full article
                    self._enhance_corresponding_author_email(article, paper)
                    papers.append(paper)
        
        except ET.ParseError as e:
            print(f"Warning: Failed to parse XML: {e}")
        
        return papers
    
    def _enhance_corresponding_author_email(self, article, paper: ResearchPaper):
        """Extract corresponding author email from various locations in the XML"""
        # Check for email in abstract text
        abstract_elem = article.find('.//Abstract')
        if abstract_elem is not None:
            abstract_text = ''.join(abstract_elem.itertext())
            email = self._extract_email_from_text(abstract_text)
            if email and not any(author.email for author in paper.authors):
                # Find first author without email to assign it to
                for author in paper.authors:
                    if not author.email:
                        author.email = email
                        author.is_corresponding = True
                        break
        
        # Check for email in any other text content
        if not any(author.email for author in paper.authors):
            article_text = ''.join(article.itertext())
            email = self._extract_email_from_text(article_text)
            if email:
                # Assign to the last author (common convention for corresponding author)
                if paper.authors:
                    paper.authors[-1].email = email
                    paper.authors[-1].is_corresponding = True
    
    def _parse_single_article(self, article) -> Optional[ResearchPaper]:
        try:
            # Extract basic info
            pmid_elem = article.find('.//PMID')
            pmid = pmid_elem.text if pmid_elem is not None else "Unknown"
            
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "No title"
            
            # Extract publication date
            pub_date = self._extract_publication_date(article)
            
            # Extract authors
            authors = self._extract_authors(article)
            
            # Extract abstract
            abstract_elem = article.find('.//AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else None
            
            # Extract journal
            journal_elem = article.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else None
            
            # Extract DOI
            doi = self._extract_doi(article)
            
            return ResearchPaper(
                pubmed_id=pmid,
                title=title,
                publication_date=pub_date,
                authors=authors,
                abstract=abstract,
                journal=journal,
                doi=doi
            )
            
        except Exception as e:
            print(f"Warning: Failed to parse article: {e}")
            return None
    
    def _extract_publication_date(self, article) -> Optional[datetime]:
        try:
            pub_date = article.find('.//PubDate')
            if pub_date is not None:
                year_elem = pub_date.find('Year')
                month_elem = pub_date.find('Month')
                day_elem = pub_date.find('Day')
                
                year = int(year_elem.text) if year_elem is not None else 2023
                month = int(month_elem.text) if month_elem is not None and month_elem.text.isdigit() else 1
                day = int(day_elem.text) if day_elem is not None else 1
                
                return datetime(year, month, day)
        except:
            pass
        return None
    
    def _extract_authors(self, article) -> List[ResearchAuthor]:
        authors = []
        
        author_list = article.find('.//AuthorList')
        if author_list is not None:
            for author_elem in author_list.findall('Author'):
                author = self._parse_author(author_elem)
                if author:
                    authors.append(author)
        
        return authors
    
    def _parse_author(self, author_elem) -> Optional[ResearchAuthor]:
        try:
            last_name_elem = author_elem.find('LastName')
            first_name_elem = author_elem.find('ForeName')
            initials_elem = author_elem.find('Initials')
            
            last_name = last_name_elem.text if last_name_elem is not None else ""
            first_name = first_name_elem.text if first_name_elem is not None else ""
            initials = initials_elem.text if initials_elem is not None else None
            
            # Extract affiliation
            affiliation_elem = author_elem.find('.//Affiliation')
            affiliation = affiliation_elem.text if affiliation_elem is not None else None
            
            # Extract email from affiliation text or author element
            email = None
            if affiliation:
                email = self._extract_email_from_text(affiliation)
            
            # Also check for email in other parts of author element
            if not email:
                # Check for email in any text content of the author element
                author_text = ''.join(author_elem.itertext())
                email = self._extract_email_from_text(author_text)
            
            # Check if this is corresponding author
            is_corresponding = self._is_corresponding_author(author_elem, affiliation)
            
            if not last_name and not first_name:
                return None
            
            return ResearchAuthor(
                first_name=first_name,
                last_name=last_name,
                initials=initials,
                affiliation=affiliation,
                email=email,
                is_corresponding=is_corresponding
            )
            
        except Exception:
            return None
    
    def _extract_doi(self, article) -> Optional[str]:
        doi_elem = article.find('.//ArticleId[@IdType="doi"]')
        return doi_elem.text if doi_elem is not None else None
    
    def _extract_email_from_text(self, text: str) -> Optional[str]:
        if not text:
            return None
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def _is_corresponding_author(self, author_elem, affiliation: str) -> bool:
        # Check for corresponding author indicators
        if affiliation:
            corresponding_indicators = [
                'corresponding author', 'correspondence', 'electronic address',
                'email:', 'e-mail:', 'contact:', 'corresponding'
            ]
            affiliation_lower = affiliation.lower()
            return any(indicator in affiliation_lower for indicator in corresponding_indicators)
        return False