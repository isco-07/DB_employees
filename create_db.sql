CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    company_name VARCHAR(255)
);

CREATE TABLE vacancies (
    vacancy_id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(company_id),
    vacancy_name VARCHAR(255),
    experience VARCHAR(255),
    url VARCHAR(255),
    salary INTEGER
);