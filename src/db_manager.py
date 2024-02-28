import psycopg2


class DBManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            user="postgres", password="1405", port="5432", database="head_hunter"
        )
        self.cur = self.conn.cursor()

    def get_companies_and_vacancies_count(self) -> list:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        self.cur.execute(
            """select c.company_name, count(v.vacancy_id) from companies as c
                            join vacancies as v using (company_id)
                            group by c.company_id, c.company_name"""
        )
        return self.cur.fetchall()

    def get_all_vacancies(self) -> list:
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        self.cur.execute(
            """select c.company_name, v.vacancy_name, v.salary, v.url from vacancies as v
                            join companies as c using(company_id)"""
        )
        return self.cur.fetchall()

    def get_avg_salary(self) -> list:
        """Получает среднюю зарплату по вакансиям"""
        self.cur.execute("""select avg(salary) from vacancies""")
        return self.cur.fetchall()

    def get_vacancies_with_higher_salary(self) -> list:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        self.cur.execute(
            """select * from vacancies
                            where salary > (select avg(salary) from vacancies)"""
        )
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> list:
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""
        self.cur.execute(
            """select * from vacancies
        where lower(vacancy_name) like lower(%s)""",
            (f"%{keyword}%",),
        )
        return self.cur.fetchall()
