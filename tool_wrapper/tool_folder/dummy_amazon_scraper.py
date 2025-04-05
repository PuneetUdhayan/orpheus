from typing import List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, HttpUrl


class CountriesUrl(BaseModel):
    url: HttpUrl = Field(
        ...,
        description="URL for https://www.scrapethissite.com that contains all countries"
    )

class CountryInfo(BaseModel):
    name: str
    capital: str
    population: int
    area: float

def get_countries_of_the_world(input: CountriesUrl) -> List[CountryInfo]:
    response = requests.get(input.url)
    soup = BeautifulSoup(response.text, 'html.parser')

    countries = []

    for country_div in soup.find_all('div', class_='country'):
        name = country_div.find('h3', class_='country-name').get_text(strip=True)
        capital = country_div.find('span', class_='country-capital').get_text(strip=True)
        population = country_div.find('span', class_='country-population').get_text(strip=True)
        area = country_div.find('span', class_='country-area').get_text(strip=True)
        
        country_info = {
            'name': name,
            'capital': capital,
            'population': int(population.replace(',', '')),
            'area': float(area.replace(',', ''))
        }
        countries.append(CountryInfo(**country_info))
    return countries


if __name__ == "__main__":
    countries = get_countries_of_the_world(CountriesUrl(url='https://www.scrapethissite.com/pages/simple/'))
    for country in countries:
        print(country)