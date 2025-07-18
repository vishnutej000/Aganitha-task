import re
import csv
from typing import List
from datetime import datetime
from .research_types import SearchResults, ResearchPaper

def save_research_results(results: SearchResults, filename: str) -> None:
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['PubmedID', 'Title', 'Publication Date', 'Non-academic Author(s)', 'Company Affiliation(s)', 'Corresponding Author Email'])
        
        for paper in results.industry_papers:
            # Extract only non-academic author names
            industry_authors = [author.display_name for author in paper.industry_authors]
            industry_author_names = '; '.join(industry_authors)
            
            # Extract company names (not full affiliations)
            from .company_finder import IndustryDetector
            company_names = set()
            for author in paper.industry_authors:
                if author.affiliation:
                    companies = IndustryDetector.extract_company_names(author.affiliation)
                    company_names.update(companies)
            
            company_list = '; '.join(sorted(company_names)) if company_names else ''
            
            # Get corresponding author email
            corresponding_email = ''
            for author in paper.authors:
                if author.is_corresponding and author.email:
                    corresponding_email = author.email
                    break
            
            writer.writerow([
                paper.pubmed_id,
                paper.title,
                paper.publication_date.strftime('%Y-%m-%d') if paper.publication_date else '',
                industry_author_names,
                company_list,
                corresponding_email
            ])

def generate_filename_from_query(query: str) -> str:
    clean_query = re.sub(r'[^\w\s-]', '', query.lower())
    clean_query = re.sub(r'\s+', '_', clean_query)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{clean_query}_{timestamp}.csv"

def create_research_summary(results: SearchResults) -> str:
    industry_count = len(results.industry_papers)
    total_count = len(results.papers)
    
    summary = f"\n📊 Research Summary:\n"
    summary += f"   Total papers analyzed: {total_count}\n"
    summary += f"   Papers with industry affiliations: {industry_count}\n"
    summary += f"   Success rate: {results.success_rate:.1f}%\n"
    
    return summary

def display_papers_as_table(papers: List[ResearchPaper]) -> None:
    print("\n📑 Research Papers with Industry Affiliations:")
    print("-" * 80)
    
    for i, paper in enumerate(papers[:10], 1):
        print(f"{i}. {paper.title[:60]}...")
        print(f"   PubMed ID: {paper.pubmed_id}")
        industry_authors = [author.display_name for author in paper.industry_authors]
        print(f"   Industry Authors: {', '.join(industry_authors)}")
        print("-" * 80)

def export_detailed_results(results: SearchResults, filename: str) -> None:
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['PubmedID', 'Title', 'Abstract', 'Publication Date', 'Journal', 'DOI', 'Non-academic Author(s)', 'Company Affiliation(s)', 'Corresponding Author Email'])
        
        for paper in results.industry_papers:
            # Extract only non-academic author names
            industry_authors = [author.display_name for author in paper.industry_authors]
            industry_author_names = '; '.join(industry_authors)
            
            # Extract company names (not full affiliations)
            from .company_finder import IndustryDetector
            company_names = set()
            for author in paper.industry_authors:
                if author.affiliation:
                    companies = IndustryDetector.extract_company_names(author.affiliation)
                    company_names.update(companies)
            
            company_list = '; '.join(sorted(company_names)) if company_names else ''
            
            # Get corresponding author email
            corresponding_email = ''
            for author in paper.authors:
                if author.is_corresponding and author.email:
                    corresponding_email = author.email
                    break
            
            writer.writerow([
                paper.pubmed_id,
                paper.title,
                paper.abstract or '',
                paper.publication_date.strftime('%Y-%m-%d') if paper.publication_date else '',
                paper.journal or '',
                paper.doi or '',
                industry_author_names,
                company_list,
                corresponding_email
            ])