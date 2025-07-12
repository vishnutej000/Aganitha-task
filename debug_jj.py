#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from research_scout.paper_hunter import PaperHunter
from research_scout.research_types import SearchRequest
from research_scout.data_writer import save_research_results

def debug_jj_search():
    print("🔍 Debugging Johnson & Johnson Search")
    print("=" * 50)
    
    hunter = PaperHunter()
    
    # Test different search queries
    queries = [
        "Johnson AND Johnson vaccine",
        "Janssen vaccine",
        "J&J COVID vaccine", 
        "Johnson Johnson coronavirus"
    ]
    
    for query in queries:
        print(f"\n📋 Testing query: '{query}'")
        print("-" * 30)
        
        request = SearchRequest(query=query, max_results=5, debug_mode=False)
        results = hunter.hunt_papers(request)
        
        print(f"Total papers: {len(results.papers)}")
        print(f"Industry papers: {len(results.industry_papers)}")
        
        if results.industry_papers:
            print("\n✅ Found industry papers:")
            for i, paper in enumerate(results.industry_papers[:2], 1):
                print(f"  {i}. {paper.title[:60]}...")
                print(f"     PubMed ID: {paper.pubmed_id}")
                for author in paper.industry_authors[:3]:
                    print(f"     - {author.display_name}: {author.affiliation[:50]}...")
                print()
                
            # Save results for this query
            filename = f"debug_{query.replace(' ', '_').replace('&', 'and')}.csv"
            save_research_results(results, filename)
            print(f"💾 Saved results to: {filename}")
        else:
            print("❌ No industry papers found")
            
        print()

if __name__ == "__main__":
    debug_jj_search()
