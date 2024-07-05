import requests
from fastapi import FastAPI, Depends
from sqlalchemy import func
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
    existing_vacancy = session.query(Vacancy).filter_by(id=vacancy['id']).first()
    if not existing_vacancy:
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

@app.get("/vacancies/")
def search_vacancies_by_name(name: str, area: str = None, experience: str = None, employment: str = None, page: int = 0, per_page: int = 20, db: Session = Depends(get_db)):
    query = db.query(Vacancy)
    if name:
        query = query.filter(func.lower(Vacancy.name).contains(func.lower(name)))
    if area:
        query = query.filter(func.lower(Vacancy.area) == func.lower(area))
    if experience:
        query = query.filter(func.lower(Vacancy.experience) == func.lower(experience))
    if employment:
        query = query.filter(func.lower(Vacancy.employment) == func.lower(employment))

    return query.offset(page * per_page).limit(per_page).all()
@app.get("/vacancies/search_by_salary/")
def get_vacancies(sort_by: str = "salary", order: str = "desc", db: Session = Depends(get_db)):
    query = db.query(Vacancy).all()
    if sort_by == "salary":
        if order == "asc":
            return sorted(query, key=lambda x: int(x.salary))
    return sorted(query, key=lambda x: int(x.salary), reverse=True)
