
import sys
from typing import Optional

import click

from .paper_hunter import PaperHunter, PubMedConnectionError, PubMedSearchError
from .research_types import SearchRequest
from .data_writer import (
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
    # Main CLI command for research-scout
    
    # Display startup message
    if debug:
        click.echo("🔍 Research Scout Debug Mode Enabled")
        click.echo(f"📝 Query: {query}")
        click.echo(f"📊 Max Results: {max_results}")
        if file:
            click.echo(f"💾 Output: {file}")
        click.echo("")
    
    # Create search request
    search_request = SearchRequest(
        query=query,
        max_results=max_results,
        email=email,
        api_key=api_key,
        debug_mode=debug
    )
    
    # Initialize the paper hunter
    hunter = PaperHunter(email=email, api_key=api_key)
    
    try:
        # Execute the search
        click.echo("🎯 Hunting for research papers...")
        results = hunter.hunt_papers(search_request)
        
        if not results.industry_papers:
            click.echo("❌ No papers found with pharmaceutical/biotech industry affiliations.")
            click.echo("💡 Try a different query or increase --max-results")
            return
        
        # Display results summary
        click.echo(f"✅ Found {len(results.industry_papers)} papers with industry connections!")
        
        # Show table view if requested
        if table:
            display_papers_as_table(results.industry_papers)
        
        # Handle file output
        if auto_save or file:
            output_filename = file or generate_filename_from_query(query)
            
            if detailed:
                export_detailed_results(results, output_filename)
            else:
                save_research_results(results, output_filename)
            
            click.echo(f"💾 Results saved to: {output_filename}")
        
        # Display summary
        if not table:
            summary = create_research_summary(results)
            click.echo(summary)
        
        # Show quick stats
        success_rate = results.success_rate
        if success_rate > 0:
            click.echo(f"📈 Success Rate: {success_rate:.1f}% of searched papers have industry affiliations")
        
    except PubMedConnectionError as e:
        click.echo(f"🌐 Connection Error: {str(e)}", err=True)
        click.echo("💡 Check your internet connection and try again", err=True)
        sys.exit(1)
        
    except PubMedSearchError as e:
        click.echo(f"🔍 Search Error: {str(e)}", err=True)
        click.echo("💡 Try simplifying your search query", err=True)
        sys.exit(1)
        
    except Exception as e:
        click.echo(f"❌ Unexpected Error: {str(e)}", err=True)
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@click.command()
@click.argument('query', required=True)
@click.option('--quick', is_flag=True, default=True,
              help='Quick search with 25 results')
def scout(query: str, quick: bool) -> None:
    # Quick research scouting command
    max_results = 25 if quick else 100
    
    click.echo(f"🔍 Quick scouting: {query}")
    
    search_request = SearchRequest(
        query=query,
        max_results=max_results,
        debug_mode=False
    )
    
    hunter = PaperHunter()
    
    try:
        results = hunter.hunt_papers(search_request)
        
        if results.industry_papers:
            click.echo(f"✅ Found {len(results.industry_papers)} relevant papers")
            display_papers_as_table(results.industry_papers[:10])  # Show top 10
        else:
            click.echo("❌ No industry-affiliated papers found")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)


@click.group()
def cli():
    # Research Scout CLI group
    pass


# Add commands to the group
cli.add_command(main, name="hunt")
cli.add_command(scout, name="quick")


if __name__ == '__main__':
    main()
