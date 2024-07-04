import requests
from fastapi import FastAPI, Depends
from db import Session, get_db, Vacancy

app = FastAPI()

def get_area_id_by_name(area_name):
    url = "https://api.hh.ru/areas"
    response = requests.get(url)
    areas = response.json()
    for country in areas:
        for area in country['areas']:
            if area['name'].lower() == area_name.lower():
                return area['id']
            for sub_area in area['areas']:
                if sub_area['name'].lower() == area_name.lower():
                    return sub_area['id']
    return None

def search_vacancies(query, area=1, page=0, per_page=20, experience='noExperience',salary=None, employment='full', only_with_salary=True):
    url = "https://api.hh.ru/vacancies"
    params = {
        'text': query,
        'area': area,  # Регион поиска (1 - Москва)
        'page': page,
        'per_page': per_page,
        'experience': experience,
        'only_with_salary': only_with_salary,
        'salary': salary,
        'employment': employment
    }
    response = requests.get(url, params=params)
    return response.json()

def add_database(vacancy, session):
    session.add(Vacancy(
        id= vacancy['id'],
        name=vacancy['name'],
        experience=vacancy['experience']['name'],
        employer=vacancy['employer']['name'],
        employment=vacancy['employment']['name'],
        salary=vacancy['salary']['from'] if vacancy['salary']['from'] else vacancy['salary']['to'],
        area=vacancy['area']['name']
    ))
    session.commit()
@app.get("/search/")
def search(query: str, area: int = 1, page: int = 0, per_page: int = 20, experience='noExperience', salary=None, employment=None, db: Session = Depends(get_db)):
    vacancies = search_vacancies(query, area, page, per_page, experience, salary, employment, only_with_salary=True)
    if vacancies['items']:
        for vacancy in vacancies['items']:
            add_database(vacancy, db)
        return vacancies
    else:
        return {"error": "An error occurred while fetching vacancies"}
