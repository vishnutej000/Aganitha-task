from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class ResearchAuthor:
    first_name: str
    last_name: str
    initials: Optional[str] = None
    affiliation: Optional[str] = None
    email: Optional[str] = None
    is_corresponding: bool = False
    
    @property
    def display_name(self) -> str:
        if self.initials:
            return f"{self.last_name} {self.initials}"
        return f"{self.first_name} {self.last_name}"

@dataclass
class ResearchPaper:
    pubmed_id: str
    title: str
    publication_date: Optional[datetime]
    authors: List[ResearchAuthor]
    abstract: Optional[str] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    
    @property
    def lead_contact_email(self) -> Optional[str]:
        for author in self.authors:
            if author.is_corresponding and author.email:
                return author.email
        return None
    
    @property
    def industry_authors(self) -> List[ResearchAuthor]:
        from .company_finder import IndustryDetector
        industry_authors = []
        for author in self.authors:
            if author.affiliation and IndustryDetector.is_industry_affiliated(author.affiliation):
                industry_authors.append(author)
        return industry_authors
    
    @property
    def has_industry_collaboration(self) -> bool:
        return len(self.industry_authors) > 0

@dataclass
class SearchRequest:
    query: str
    max_results: int = 100
    email: Optional[str] = None
    api_key: Optional[str] = None
    debug_mode: bool = False
    
    def __post_init__(self):
        if self.max_results <= 0:
            raise ValueError("Maximum results must be positive")
        if self.max_results > 1000:
            self.max_results = 1000

@dataclass
class SearchResults:
    papers: List[ResearchPaper]
    total_found: int
    query_used: str
    search_time: Optional[datetime] = None
    
    @property
    def industry_papers(self) -> List[ResearchPaper]:
        return [paper for paper in self.papers if paper.has_industry_collaboration]
    
    @property
    def success_rate(self) -> float:
        if not self.papers:
            return 0.0
        return len(self.industry_papers) / len(self.papers) * 100