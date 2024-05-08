import argparse
from indeed_scraper import IndeedScraper, main  # Adjust this import based on your actual module structure.

def parse_args():
    parser = argparse.ArgumentParser(description="Scrape job listings from Indeed.")
    parser.add_argument('--keywords', type=str, default='Data Analyst', help='Keywords to search for.')
    parser.add_argument('--location', type=str, default='Remote', help='Location to search in.')
    parser.add_argument('--country', type=str, choices=['USA', 'CANADA'], default='usa', help='Country to search in.')
    parser.add_argument('--sort_by', type=str, choices=['date', 'relevance'], default='date', help='Sort by date or relevance.')
    parser.add_argument('--max_pages', type=int, default=5, help='Maximum number of pages to scrape.')
    parser.add_argument('--dont_search', action='store_true', help='Disable searching for new jobs.')
    parser.add_argument('--dont_update_job_descriptions', action='store_true', help='Disable updating job descriptions.')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    # Set the country and sort_by using the enumeration in IndeedScraper, adjusting as needed for your implementation.
    country_enum = getattr(IndeedScraper.Country, args.country)
    sort_by_enum = getattr(IndeedScraper.SortBy, args.sort_by.upper())

    # Construct the search parameters Object
    search_params = {
        'keywords': args.keywords,
        'location': args.location,
        'country': country_enum,
        'sort_by': sort_by_enum
    }

    # Run the main function with the parsed command line arguments.
    main(
        max_pages=args.max_pages, 
        dont_search=args.dont_search, 
        dont_update_job_descriptions=args.dont_update_job_descriptions,
        **search_params
    )
    
    # Handle temporary bug fix with the second call
    if args.dont_update_job_descriptions:  # Check if updating descriptions is needed
        main(
            max_pages=0, 
            dont_search=args.dont_search, 
            dont_update_job_descriptions=False, 
            **search_params
        )
# python main.py --keywords "Engineering" --location "Toronto" --country CANADA --sort_by relevance --max_pages 2 --dont_search --dont_update_job_descriptions