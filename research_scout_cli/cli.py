#!/usr/bin/env python3
"""
Research Scout CLI - Command Line Interface

Main entry point for the command-line tool that uses the research_scout module.
"""

import sys
from typing import Optional

import click

# Import from the research_scout module
from research_scout import (
    PaperHunter, 
    PubMedConnectionError, 
    PubMedSearchError,
    SearchRequest,
    save_research_results,
    generate_filename_from_query,
    create_research_summary,
    display_papers_as_table,
    export_detailed_results
)

@click.command()
@click.argument('query', required=True)
@click.option('-f', '--file', type=click.Path(), 
              help='Output filename (auto-generated if not provided)')
@click.option('-d', '--debug', is_flag=True, 
              help='Show detailed processing information')
@click.option('--max-results', type=int, default=100, 
              help='Maximum papers to analyze (default: 100)')
@click.option('--email', type=str, 
              help='Your email for NCBI API (recommended for reliability)')
@click.option('--api-key', type=str, 
              help='NCBI API key for faster processing')
@click.option('--table', is_flag=True, 
              help='Display results in table format')
@click.option('--detailed', is_flag=True, 
              help='Export detailed results with abstracts')
@click.option('--auto-save', is_flag=True, default=True,
              help='Automatically save results to file')
@click.version_option(version='0.1.0')
def main(query: str, file: Optional[str], debug: bool, max_results: int,
         email: Optional[str], api_key: Optional[str], table: bool, 
         detailed: bool, auto_save: bool) -> None:
    """
    Research Scout CLI - Find pharmaceutical/biotech industry collaborations in research papers.
    
    QUERY: PubMed search query (supports full PubMed syntax)
    
    Examples:
    
        research-scout-cli "cancer treatment"
        
        research-scout-cli "diabetes AND drug therapy" --file results.csv
        
        research-scout-cli "COVID-19 vaccine" --debug --max-results 50
    """
    
    # Display startup message
    if debug:
        click.echo("🔍 Research Scout CLI Debug Mode Enabled")
        click.echo(f"📝 Query: {query}")
        click.echo(f"📊 Max Results: {max_results}")
        if file:
            click.echo(f"💾 Output: {file}")
        click.echo("")
    
    # Create search request
    try:
        search_request = SearchRequest(
            query=query,
            max_results=max_results,
            email=email,
            api_key=api_key,
            debug_mode=debug
        )
        
        if debug:
            click.echo("✅ Search request created successfully")
            
    except ValueError as e:
        click.echo(f"❌ Invalid search parameters: {e}", err=True)
        sys.exit(1)
    
    # Initialize paper hunter
    try:
        hunter = PaperHunter(debug=debug)
        if debug:
            click.echo("✅ PaperHunter initialized")
            
    except Exception as e:
        click.echo(f"❌ Failed to initialize PaperHunter: {e}", err=True)
        sys.exit(1)
    
    # Execute search
    try:
        if debug:
            click.echo("🔍 Starting paper search...")
            
        results = hunter.search_papers(search_request)
        
        if debug:
            click.echo(f"✅ Search completed: {len(results.papers)} papers found")
            
    except PubMedConnectionError as e:
        click.echo(f"❌ Connection error: {e}", err=True)
        click.echo("💡 Try checking your internet connection or using an API key", err=True)
        sys.exit(1)
        
    except PubMedSearchError as e:
        click.echo(f"❌ Search error: {e}", err=True)
        click.echo("💡 Try simplifying your search query", err=True)
        sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)
    
    # Check if we have results
    if not results.papers:
        click.echo("⚠️  No papers found matching your criteria")
        sys.exit(0)
    
    # Filter for industry papers
    industry_papers = results.industry_papers
    if not industry_papers:
        click.echo("⚠️  No papers found with pharmaceutical/biotech industry affiliations")
        sys.exit(0)
    
    # Display results
    if table:
        display_papers_as_table(industry_papers)
    else:
        # Create summary
        summary = create_research_summary(results)
        click.echo(summary)
    
    # Save results to file
    output_file = file
    if auto_save and not output_file:
        output_file = generate_filename_from_query(query)
    
    if output_file:
        try:
            if detailed:
                export_detailed_results(industry_papers, output_file)
            else:
                save_research_results(industry_papers, output_file)
            
            click.echo(f"💾 Results saved to: {output_file}")
            
        except Exception as e:
            click.echo(f"❌ Failed to save results: {e}", err=True)
            sys.exit(1)
    
    # Final status
    click.echo(f"✅ Analysis complete: {len(industry_papers)} industry papers found")


if __name__ == "__main__":
    main()
