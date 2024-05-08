# Indeed Job Scraper

This Python project automates the process of scraping job listings from Indeed using Selenium. The data is stored in a SQLite database and can be analyzed or visualized through Jupyter notebooks.

<video controls>
   <source src="demo/demo.mp4" type="video/mp4">
   Your browser does not support the video tag.
</video>


## Project Structure

- `env/`: Virtual environment for project dependencies.
- `.gitignore`: Specifies intentionally untracked files to ignore.
- `database_tools.py`: Contains utilities for interacting with the SQLite database.
- `ddl.sql`: SQL script for creating database tables.
- `indeed_scraper.py`: Main script for scraping job data from Indeed.
- `indeed.db`: SQLite database file containing the scraped data.
- `requirements.txt`: List of dependencies to install using pip.
- `selenium_base.py`: Base setup for Selenium WebDriver.
- `view_data.ipynb`: Jupyter notebook for data analysis and visualization.

## Setup

1. Clone this repository to your local machine.
2. Ensure Python 3.x is installed.
3. Set up a virtual environment (ON WINDOWS):
   ```bash
   python -m venv env
   env\Scripts\activate
   pip install -r requirements.txt

## Example Useage In Command Line Interface

```bash
# Run the scraper for Data Analyst positions, in Remote location, in the USA, sorted by date, scraping 5 pages
python main.py --keywords "Data Analyst" --location "Remote" --country USA --sort_by date --max_pages 5
```
```bash
# Run the scraper without searching for new jobs, just updating job descriptions for existing entries
python main.py --dont_search
```
```bash
# Run the scraper with a different keyword and location, only scraping 3 pages, without updating job descriptions
python main.py --keywords "Software Developer" --location "New York" --country USA --sort_by relevance --max_pages 3 --dont_update_job_descriptions
```
```bash
# Run the scraper for Canada in the city of Toronto, looking for Engineering positions, sorting by relevance
python main.py --keywords "Engineering" --location "Toronto" --country CANADA --sort_by relevance --max_pages 2
```