import logging
import time
import json
from selenium.webdriver.common.by import By
import pyautogui
from markdownify import markdownify as md
import re


from database_tools import DatabaseTools
from selenium_base import SeleniumScraper, Browsers


class IndeedScraper(SeleniumScraper):
    """Initializes the Indeed Scraper with the specified browser and database settings."""
    print('Indeed Scraper Initialized')
    def __init__(self, browser: str = Browsers.CHROME, use_database: bool = False):
        super().__init__(browser=browser, use_database=use_database)
        self.session_id = None

    """Type Parameters for Indeed Scraper"""
    class SortBy:
        DATE = 'date'
        RELEVANCE = 'relevance'

    class Country:
        USA = 'com'
        CANADA = 'ca'

    """The URL Builder for Indeed Scraper"""

    def build_query_url(self,
                        keywords: str = None,  # job title, skills, etc
                        country: str = None,  # 'usa' or 'canada'
                        location: str = None,  # city, province, state or "Remote"
                        sort_by: str = SortBy.DATE,  # or relevance
                        # in countries default units (miles or km)
                        radius: int = 50,
                        page_number: int = None  # the page number to start on
                        ):

        if keywords is None:
            raise ValueError('Keywords are required.')
        else:
            keywords = keywords.replace(' ', '%20')
        if country is None:
            raise ValueError('Country is required.')

        if country == self.Country.CANADA:
            region_code = 'ca'
        elif country == self.Country.USA:
            region_code = 'com'

        # This is the base url for all queries
        self.url = f"https://www.indeed.{region_code}/jobs?q={keywords}"

        # add location to the query
        if location is not None:
            self.url = f"{self.url}&l={location}"

        # a remote tag only makes sense for non-remote positions
        if radius is not None and location.lower() == 'remote':
            self.url = f"{self.url}"
        # effectively the same as remote becuase there is no search location
        elif radius is not None and location is None:
            self.url = f"{self.url}"
        elif radius is not None and location.lower() != 'remote' and location is not None:
            # add the radius only if its not a remote job, and the location is specified as something other than remote
            self.url = f"{self.url}&radius={radius}"

        # order the search results by date or relevance
        if sort_by is not None:
            if sort_by in ('date', 'relevance'):
                if sort_by == 'date':
                    self.url = f"{self.url}&sort=date"
                elif sort_by == 'relevance':
                    # its the default sort
                    self.url = f"{self.url}"
            else:
                raise ValueError(
                    'Invalid sort_by value. Use "date" or "relevance"')

        # add the page number to the query
        if page_number is not None:
            # page numbers not 1,2,3, etc. its 0, 10, 20, etc. where 0=1, 10=2, 20=3, etc.
            if page_number == 1:
                new_page_num = 0
            elif page_number > 1:
                new_page_num = (page_number - 1) * 10
            self.url = f"{self.url}&start={new_page_num}"
        logging.log(logging.INFO, f'URL built: {self.url}')
        # return the url
        return self.url

    """Parsing Functions"""

    def get_filter_items(self):
        """Returns the list of filter tags from an in Indeed job search results list."""
        menu_items = []
        for dropdown in self.driver.find_elements(by=By.CLASS_NAME, value='yosegi-FilterPill-dropdownPillContainer'):
            button = dropdown.find_element(by=By.CSS_SELECTOR, value="button")
            if button.get_attribute('id').startswith('filter'):
                button.click()
                options = [x.text for x in dropdown.find_elements(
                    by=By.CLASS_NAME, value='yosegi-FilterPill-dropdownListItemLink')]
                menu_item = {
                    'name': button.text,
                    'options': options
                }
                menu_items.append(menu_item)
        logging.log(logging.INFO, f'Filter items found: {menu_items}')
        return menu_items

    def get_current_url(self):
        logging.log(
            logging.INFO, f'Getting current url: {self.driver.current_url}')
        return '&'.join(self.driver.current_url.split('&')[0:-2])

    """UI Manipulation Functions"""

    def close_popup(self):
        try:
            logging.log(logging.INFO, 'Closing popup')
            self.driver.find_element(
                by=By.CSS_SELECTOR, value='button[aria-label="close"]').click()
            time.sleep(1)
        except:
            pass

    def click_next(self):
        logging.log(logging.INFO, 'Clicking next page')
        self.driver.find_element(
            by=By.CSS_SELECTOR, value='a[data-testid="pagination-page-next"]').click()

    def click_prev(self):
        logging.log(logging.INFO, 'Clicking previous page')
        self.driver.find_element(
            by=By.CSS_SELECTOR, value='a[data-testid="pagination-page-prev"]').click()

    # !!!! TODO: This function doesnt work on all resolutions and browsers. Also it should minimize back. Full-screen indeed is bright.
    def requires_human_verification(self):
        logging.log(logging.INFO, 'Checking for human verification')
        # works on 1080 * 1920 resolution, with firefox browser
        if 'Verify' in str(self.driver.page_source):
            logging.log(logging.INFO, 'Human verification required')
            self.driver.fullscreen_window()
            time.sleep(2)
            where = {
                Browsers.FIREFOX: {'x': 537, 'y': 286}
            }
            pyautogui.click(where[self.browser]['x'], where[self.browser]['y'])
            time.sleep(2)
            self.driver.minimize_window()
            return True
        else:
            return False

    """Main Functions"""

    def search_for_jobs(self, max_pages=2, **search_params):
        """Collects job listings from the current page and returns them as a list of dictionaries."""

        current_page = 0

        self.open_browser(wait_seconds=0)

        self.url = self.build_query_url(
            page_number=current_page+1, **search_params)

        self.go_to_url(self.url)

        time.sleep(1)
        filter_items = self.get_filter_items()

        # create a new search session record in the database
        db_tools = DatabaseTools()
        self.session_id = db_tools.start_new_session(
            terms=search_params['keywords'],
            location=search_params['location'],
            filter_tags=str(json.dumps(filter_items)),
            n_pages=max_pages
        )

        for page in range(max_pages):
            print(f'Page {current_page+1} of {max_pages}')
            if current_page <= max_pages:
                self.current_url = self.get_current_url()
                if current_page != 0:
                    self.url = self.build_query_url(
                        page_number=current_page+1, **search_params)
                    self.go_to_url(self.url)
                self.close_popup()
                self.requires_human_verification()

                # Isolate the job cards on the page. Each card is a job listing.
                job_cards = self.driver.find_elements(
                    By.CLASS_NAME, 'cardOutline')

                for job in job_cards:

                    try:  # to get the unique id of the job
                        job_unique_id = job.find_element(By.CLASS_NAME, 'jobTitle').find_element(
                            By.TAG_NAME, 'a').get_attribute('id')
                    except:
                        job_unique_id = None

                    try:  # to get the job title
                        job_title = job.find_element(
                            By.CLASS_NAME, 'jcs-JobTitle').text
                    except:
                        print('no job title')
                        job_title = None

                    try:  # to get the job link
                        job_link = job.find_element(
                            By.TAG_NAME, 'a').get_attribute('href')
                    except:
                        print('no job link')
                        job_link = None

                    # Build the job object
                    obj = {
                        'job_unique_id': job_unique_id,
                        'job_title': job_title,
                        'job_link': job_link,
                        'session_id': self.session_id
                    }
                    db = DatabaseTools()
                    db.update_job_postings(obj)

                # Prepare to switch pages. Saving the last working link is helful for error handling.
                self.previous_url = self.get_current_url()

                current_page += 1
        self.close_browser()

    """Obtaining and parsing the job description from the job page."""

    def get_job_html(self, url: str):

        def get_description_html():
            try:
                description_element = self.driver.find_element(
                    By.CLASS_NAME, 'jobsearch-JobComponent')
                return description_element.get_attribute('innerHTML')
            except:
                
                # Sometimes in indeed the job description links out to a different website, and not the "jobsearch-JobComponent" class.
                # This is a workaround to get the job description in those cases. We'll just get the entire page.
                ele = self.driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML')
                if 'Verifying you are human' in ele:
                    time.sleep(1)
                    self.requires_human_verification()
                else:
                    return ele
        self.go_to_url(url)

        try:
            description_html = get_description_html()

        except:
            self.requires_human_verification()
            try:
                description_html = get_description_html()
            except:
                time.sleep(3)
                self.requires_human_verification()
                description_html = get_description_html()

        return description_html

    def html_to_markdown(self, description_html: str):
        md_text = md(description_html)
        logging.log(logging.DEBUG, md_text)
        return md_text

    def remove_links_from_markdown(self, markdown, replace_with: str = '<url removed>'):
        def replace_link(match):
            return f"[{match.group(1)}]({replace_with})"
        pattern = r'\[([^]]+)]\(([^)]+)\)'
        return re.sub(pattern, replace_link, markdown).replace('\n', '')


def main(max_pages=15, dont_search=False, dont_update_job_descriptions=False, **search_params):
    print(f'Searching for {search_params["keywords"]} jobs in {search_params["location"]}.')
    # Run the Scraper to collect job postings
    scraper = IndeedScraper(browser=Browsers.FIREFOX, use_database=False)
   
    if dont_search:
        print(f'Skipping search. Only updating job descriptions.')
    else:
        print(f'Searching for {max_pages} pages of job postings.')
        scraper.search_for_jobs(max_pages=max_pages, **search_params)

    if dont_update_job_descriptions:
        print('Skipping job description updates.')
    else:
        # Determine which job postings need to be updated
        db = DatabaseTools()
        df = db.sql_to_df(
            '''SELECT * FROM job_postings WHERE 
            (job_description IS NULL or job_description like '' 
            or job_description like 'Verify% you are human'
            or job_description like '%nable JavaScript%') 
            and job_link is not null''')
        if len(df.index) == 0:
            print('No job postings to update.')
            exit()

        # For each job posting without a description, get the description from the job link and update the database.
        print(f'Updating {len(df.index)} job postings.')
        scraper.open_browser()
        for index, row in df.iterrows():
            # job number and url
            print(f'Job {index+1} of {len(df.index)}: {row["job_link"]}')
            job_html = scraper.get_job_html(row['job_link'])
            if job_html is not None:
                job_markdown = scraper.html_to_markdown(job_html)
                db.update_job_posting_description(
                    row['job_unique_id'], job_markdown)
        scraper.close_browser()
        print('All job postings updated.')


if __name__ == '__main__':

    # Set the search parameters
    KEYWORDS = 'Data Analyst'
    LOCATION = 'Remote'
    COUNTRY = IndeedScraper.Country.USA
    SORT_BY = IndeedScraper.SortBy.DATE

    # Construct the search parameters Object
    search_params = {
        'keywords': KEYWORDS,
        'location': LOCATION,
        'country': COUNTRY,
        'sort_by': SORT_BY
    }
    
    #####!temp bug fix - for then we need to run the two processes separately
    # These options are nice to have for debugging and testing. 
    dont_search = False
    dont_update_job_descriptions = False
        
    # Run the main function over max_pages=N, with the search parameters.
    main(
        max_pages=5, 
        dont_search=dont_search, 
        dont_update_job_descriptions=dont_update_job_descriptions,
        **search_params
    )
    
    #####!temp bug fix - run just the description update again as it missses some for some larger jobs. This is a browser issue.
    main(max_pages=0, dont_search=dont_search, 
         dont_update_job_descriptions=dont_update_job_descriptions, **search_params)