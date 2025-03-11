from fastapi import requests, HTTPException
from db import Session, Vacancy

HH_API_URL = "https://api.hh.ru"

def get_area_id_by_name(area_name: str) -> str | None:
    """Получение ID региона по его названию"""
    try:
        response = requests.get(f"{HH_API_URL}/areas")
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка запроса к API hh.ru: {e}")

    for country in response.json():
        for area in country["areas"]:
            if area["name"].lower() == area_name.lower():
                return area["id"]
            for sub_area in area["areas"]:
                if sub_area["name"].lower() == area_name.lower():
                    return sub_area["id"]
    return None

def search_vacancies(
    query: str, area: int = 1, page: int = 0, per_page: int = 20,
    experience: str = "noExperience", salary: int | None = None,
    employment: str = "full", only_with_salary: bool = True
) -> dict:
    """Поиск вакансий на hh.ru"""
    params = {
        "text": query, "area": area, "page": page, "per_page": per_page,
        "experience": experience, "only_with_salary": only_with_salary,
        "salary": salary, "employment": employment
    }
    try:
        response = requests.get(f"{HH_API_URL}/vacancies", params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка запроса к API hh.ru: {e}")


def add_vacancy_to_db(vacancy: dict, session: Session) -> None:
    """Добавление вакансии в базу данных"""
    if session.query(Vacancy).filter_by(id=vacancy["id"]).first():
        return

    salary = vacancy.get("salary")
    salary_value = None
    if salary:
        salary_value = salary.get("from") or salary.get("to")

    new_vacancy = Vacancy(
        id=vacancy["id"], name=vacancy["name"], experience=vacancy["experience"]["name"],
        employer=vacancy["employer"]["name"], employment=vacancy["employment"]["name"],
        salary=salary_value, area=vacancy["area"]["name"]
    )
    session.add(new_vacancy)
    session.commit()

import requests
