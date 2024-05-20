/**/
CREATE TABLE IF NOT EXISTS search_sessions (
    id INTEGER PRIMARY KEY,
    terms TEXT,
    location TEXT,
    filter_tags TEXT,
    n_pages INTEGER,
    ended_at DATETIME,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

/**/
CREATE TABLE IF NOT EXISTS job_postings (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    job_unique_id TEXT UNIQUE,
    job_title TEXT,
    job_link TEXT,
    job_description TEXT,
    job_company TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES search_sessions(id)
);

CREATE TABLE IF NOT EXISTS job_details (
    id INTEGER PRIMARY KEY,
    job_unique_id INTEGER UNIQUE,
    position_summary TEXT,
    salary TEXT,
    location TEXT,
    employer TEXT,
    education TEXT,
    key_skills TEXT,
    employment_type TEXT,
    work_environment TEXT,
    experience_level TEXT,
    responsibilities TEXT,
    benefits TEXT,
    application_deadline TEXT,
    industry TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_unique_id) REFERENCES job_postings(job_unique_id)
);
