from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import func
from db import Session, get_db, Vacancy
from vacancies import search_vacancies, add_vacancy_to_db

app = FastAPI()

@app.get("/search/")
def search(
    query: str, area: int = 1, page: int = 0, per_page: int = 20,
    experience: str = "noExperience", salary: int | None = None,
    employment: str | None = None, db: Session = Depends(get_db)
):
    """Поиск вакансий и сохранение их в базу данных"""
    vacancies = search_vacancies(query, area, page, per_page, experience, salary, employment)
    if "items" in vacancies:
        for vacancy in vacancies["items"]:
            add_vacancy_to_db(vacancy, db)
        return vacancies
    raise HTTPException(status_code=500, detail="Ошибка при получении вакансий")


@app.get("/vacancies/")
def get_vacancies(
        name: str = "", area: str | None = None, experience: str | None = None,
        employment: str | None = None, db: Session = Depends(get_db)
):
    """Получение вакансий из БД с фильтрацией"""
    query = db.query(Vacancy)
    if name:
        query = query.filter(func.lower(Vacancy.name).contains(func.lower(name)))
    if area:
        query = query.filter(func.lower(Vacancy.area) == func.lower(area))
    if experience:
        query = query.filter(func.lower(Vacancy.experience) == func.lower(experience))
    if employment:
        query = query.filter(func.lower(Vacancy.employment) == func.lower(employment))

    return query.all()
@app.get("/vacancies/sorted/")
def get_sorted_vacancies(
    sort_by: str = "salary", order: str = "desc", db: Session = Depends(get_db)
):
    """Сортировка вакансий по зарплате"""
    vacancies = db.query(Vacancy).all()
    if sort_by == "salary":
        return sorted(
            vacancies, key=lambda x: int(x.salary) if x.salary else 0, reverse=(order == "desc")
        )
    return vacancies
