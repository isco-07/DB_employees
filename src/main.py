from src.db_manager import DBManager
import os

import psycopg2
import requests

from src.config import config

if __name__ == '__main__':

    db_filename = os.path.join(os.path.dirname(__file__), "../database.ini")
    db_params = config(db_filename, "postgresql")
    db_name = "head_hunter"

    conn = psycopg2.connect(**db_params)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE {db_name}")
    except psycopg2.Error as err:
        print(err)
    db_params.update({"dbname": db_name})
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cur:
                with open("../create_db.sql", "r", encoding="utf-8") as file:
                    try:
                        cur.execute(file.read())
                    except psycopg2.Error as err:
                        print(err)
    except (Exception, psycopg2.DatabaseError) as err:
        print(err)

    params = {"only_with_vacancies": "true", "sort_by": "by_vacancies_open"}
    employers_url = "https://api.hh.ru/employers"
    response = requests.get(url=employers_url, params=params).json()["items"][:10]
    companies = []
    for i in response:
        companies.append(
            {
                "company_id": int(i["id"]),
                "company_name": i["name"],
                "open_vacancies": i["open_vacancies"],
            }
        )
    vacancies = []
    for company in companies:
        vacancies_list = requests.get(
            f'https://api.hh.ru/vacancies?employer_id={company["company_id"]}'
        ).json()["items"]
        for vacancy in vacancies_list:
            salary = (
                0
                if vacancy["salary"] is None
                else (
                    vacancy["salary"]["from"]
                    if vacancy["salary"]["to"] is None
                    else vacancy["salary"]["to"]
                )
            )
            vacancies.append(
                {
                    "vacancy_id": vacancy["id"],
                    "company_id": vacancy["employer"]["id"],
                    "vacancy_name": vacancy["name"],
                    "experience": vacancy["experience"]["name"],
                    "url": f'https://hh.ru/vacancy/{vacancy["id"]}',
                    "salary": salary,
                }
            )
    with conn.cursor() as cur:
        for company in companies:
            cur.execute(
                """
            INSERT INTO companies (company_id, company_name)
            VALUES (%s, %s)
        """,
                (company["company_id"], company["company_name"]),
            )
        for vacancy in vacancies:
            cur.execute(
                """
            INSERT INTO vacancies (vacancy_id, company_id, vacancy_name, experience, url, salary)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
                (
                    vacancy["vacancy_id"],
                    vacancy["company_id"],
                    vacancy["vacancy_name"],
                    vacancy["experience"],
                    vacancy["url"],
                    vacancy["salary"],
                ),
            )

    conn.commit()
    cur.close()
    conn.close()

    requester = DBManager()
    requester.get_companies_and_vacancies_count()
    requester.get_all_vacancies()
    requester.get_avg_salary()
    requester.get_vacancies_with_higher_salary()
    keyword = input()
    requester.get_vacancies_with_keyword(keyword)
