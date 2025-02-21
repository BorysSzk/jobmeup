import requests
import pandas as pd
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

'''
Uwaga: włączenie tego pliku mocno obciąża procesor (obstawiam, że przez geckodriver Firefoxa do Selenium) i web scraping zajmuje dobre kilka minut.
'''

def fetch_justjoinit():
    '''
    Funkcja web scrapująca dane z JustJoinIT i dodająca je do listy "data" z zamianą jej na DataFrame.
    '''
    url = 'https://justjoin.it/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    options = Options()
    options.add_argument('--headless')
    service = Service('geckodriver-v0.34.0-win64/geckodriver.exe')
    driver = webdriver.Firefox(service=service, options=options)

    data = []

    job_offers = soup.select('li[class^="MuiBox-root"]')
    for job in job_offers:
        title = job.find('h3', class_='css-1gehlh0').text if job.find('h3', class_='css-1gehlh0') else None

        salary_div = job.find('div', class_='MuiBox-root css-18ypp16')
        if salary_div:
            undisclosed_salary = salary_div.find('div')
            if undisclosed_salary and undisclosed_salary.text.strip() == "Undisclosed Salary":
                salary_from = salary_to = currency = "Nieujawnione"
            else:
                salary_spans = salary_div.find_all('span')
                if len(salary_spans) >= 3:
                    salary_from = salary_spans[0].text.strip()
                    salary_to = salary_spans[1].text.strip()
                    currency = salary_spans[2].text.strip()
                else:
                    salary_from = salary_to = currency = None
        else:
            salary_from = salary_to = currency = None

        company_div = job.find('div', class_='MuiBox-root css-1kb0cuq')
        company = company_div.find('span') if company_div else None
        company_text = company.text if company else None

        requirements_elements = job.find_all('div', class_='MuiBox-root css-jikuwi')
        requirements = [req.text.strip() for req in requirements_elements if req.text.strip() not in ["New"]]

        city_div = job.find('div', class_='MuiBox-root css-1un5sk1')
        city = city_div.find('span') if city_div else None
        city_text = city.text if city else None

        link = job.find('a', class_='offer_list_offer_link', href=True)
        job_url = f"https://justjoin.it{link['href']}" if link else None

        if job_url:
            try:
                driver.get(job_url)
                employment_type_element = driver.find_element(
                    By.XPATH,
                    "//div[text()='Employment Type']/following-sibling::div"
                )
                employment_type = employment_type_element.text.strip() if employment_type_element else None
            except Exception as e:
                employment_type = None
                print(f"Error finding Employment TypeJJ: {e}")
        else:
            employment_type = None

        data.append({'title': title, 
                     'company': company_text,
                     'requirements': ', '.join(requirements),
                     'salary_from': salary_from, 
                     'salary_to': salary_to, 
                     'currency': currency, 
                     'city': city_text,
                     'employment_type': employment_type
                    })

    return pd.DataFrame(data)


def fetch_nofluffjobs():
    '''
    Funkcja web scrapująca dane z NoFluffJobs i dodająca je do listy "data" z zamianą jej na DataFrame.
    Niestety przy NoFluffJobs musiałem całkowicie użyć Selenium, ponieważ używają oni Angulara na ich stronie 
    i BeautifulSoup nie jestw stanie "przejść" przez niektóre customowe obiekty html Angulara.
    '''
    options = Options()
    options.add_argument('--headless')
    service = Service('geckodriver-v0.34.0-win64/geckodriver.exe')
    driver = webdriver.Firefox(service=service, options=options)
    driver.get("https://nofluffjobs.com/pl")

    data = []
    job_links = []

    job_offers = driver.find_elements(By.CSS_SELECTOR, '[id^="nfjPostingListItem"]')
    for job in job_offers:
        job_links.append(job.get_attribute('href'))
        try:
            h3 = job.find_element(By.CSS_SELECTOR, 'h3.posting-title__position')
            driver.execute_script("arguments[0].querySelectorAll('span').forEach(span => span.remove());", h3)
            title = h3.text.strip()

            company = job.find_element(By.TAG_NAME, 'h4').text.strip()
            
            salary_element = job.find_element(By.CSS_SELECTOR, 'nfj-posting-item-salary span.posting-tag')
            salary_text = salary_element.text.split()
            if len(salary_text) >= 6:
                salary_from = f"{salary_text[0]} {salary_text[1]}"
                salary_to = f"{salary_text[3]} {salary_text[4]}"
                currency = salary_text[5].lower()
            else:
                salary_from = salary_to = currency = "Nieujawnione"
            
            city_element = job.find_element(By.CSS_SELECTOR, 'span[class^="tw-text-ellipsis"]')
            city = city_element.text.strip() if city_element else None

            requirement_elements = job.find_elements(By.CSS_SELECTOR, 'nfj-posting-item-tiles.ng-star-inserted span.posting-tag')
            requirements = [req.text.strip() for req in requirement_elements if req.text.strip()]

            data.append({
                'title': title,
                'company': company,
                'requirements': ', '.join(requirements),
                'salary_from': salary_from,
                'salary_to': salary_to,
                'currency': currency,
                'city': city,
                'employment_type': "Nieujawnione"
            })

        except Exception as e:
            print(f"Error processing job: {e}")


    for index, link in enumerate(job_links):
        driver.get(link)
    
        employment_type = "Nieujawnione"
        try:
            employment_elements = driver.find_elements(By.CSS_SELECTOR, 'div.paragraph.tw-text-xs')

            if employment_elements:
                for element in employment_elements:
                    span = element.find_element(By.TAG_NAME, 'span')
                    if "B2B" in span.text:
                        employment_type = "B2B"
                        break
                    elif "UoP" in span.text:
                        employment_type = "UoP"
                        break
                    elif "UoD" in span.text:
                        employment_type = "UoD"
                        break
                    elif "UZ" in span.text:
                        employment_type = "UZ"
                        break
        except Exception as e:
            print(f"Error finding employment typeNFJ: {e}")
    
        data[index]['employment_type'] = employment_type

    driver.quit()
    return pd.DataFrame(data)


def fetch_rocketjobs():
    '''
    Funkcja web scrapująca dane z RocketJobs i dodająca je do listy "data" z zamianą jej na DataFrame.
    '''
    url = 'https://rocketjobs.pl/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    options = Options()
    options.add_argument('--headless')
    service = Service('geckodriver-v0.34.0-win64/geckodriver.exe')
    driver = webdriver.Firefox(service=service, options=options)

    data = []

    job_offers = soup.select('li[class^="MuiBox-root"]')
    for job in job_offers:
        title = job.find('h3', class_="css-vgztiw").text if job.find('h3', class_="css-vgztiw") else None

        salary_div = job.find('div', class_='MuiBox-root css-606a0h')
        if salary_div:
            salary_spans = salary_div.find_all('span')
            if len(salary_spans) >= 3:
                salary_from = salary_spans[0].text.strip()
                salary_to = salary_spans[1].text.strip()
                currency = salary_spans[2].text.strip()
            else:
                salary_from = salary_to = currency = "Nieujawnione"
        else:
            salary_from = salary_to = currency = "Nieujawnione"

        company_div = job.find('div', class_='MuiBox-root css-1lztmxj')
        company = company_div.find('span') if company_div else None
        company_text = company.text if company else None

        requirements_elements = job.find_all('div', class_='MuiBox-root css-jikuwi')
        requirements = [req.text.strip() for req in requirements_elements if req.text.strip() not in ["Nowa"]]

        city_div = job.find('div', class_='MuiBox-root css-ll20ho')
        city = city_div.find('span') if city_div else None
        city_text = city.text if city else None

        link = job.find('a', class_='offer_list_offer_link', href=True)
        job_url = f"https://rocketjobs.pl{link['href']}" if link else None

        if job_url:
            try:
                driver.get(job_url)
                employment_type_element = driver.find_element(
                    By.XPATH,
                    "//div[text()='Forma zatrudnienia']/following-sibling::div"
                )
                employment_type = employment_type_element.text.strip() if employment_type_element else None
            except Exception as e:
                employment_type = None
                print(f"Error finding Employment TypeRJ: {e}")
        else:
            employment_type = None
        
        data.append({'title': title, 
                     'company': company_text, 
                     'requirements': ', '.join(requirements),
                     'salary_from': salary_from, 
                     'salary_to': salary_to, 
                     'currency': currency, 
                     'city': city_text,
                     'employment_type': employment_type
                    })

    return pd.DataFrame(data)
        


def aggregate_data():
    '''
    Funkcja tworząca 3 zmienne dla DataFrame'ów odpowednio dla każdej funkcji wszystkich serwisów. Funkcja także tworzy dodatkowe kolumny 'source' odpowiednio dla każdego DataFrame'a, które pozwalają na identyfikację z jakiego serwisu pochodzą dane.
    Finalnie funkcja tworzy zagregowanego DataFrame "aggregated_df", w którym jest wykonana konkatenacja wszystkich 3 DataFrame'ów.
    '''
    justjoinit_df = fetch_justjoinit()
    nofluffjobs_df = fetch_nofluffjobs()
    rocketjobs_df = fetch_rocketjobs()
    
    justjoinit_df['source'] = 'justjoinit'
    nofluffjobs_df['source'] = 'nofluffjobs'
    rocketjobs_df['source'] = 'rocketjobs'
    
    aggregated_df = pd.concat([justjoinit_df, nofluffjobs_df, rocketjobs_df], ignore_index=True)
    return aggregated_df


def save_to_sqlite(df, database_name="job_offers.db"):
    '''
    Wywołana funkcja z dowolnym DataFrame'em zapisze go do tabeli SQLite o nazwie job_offers. Funkcja także stworzy plik bazy danych "job_offers.db", jeśli ta już nie istnieje - jeśli istnieje to zamienia dane w razie wywołania funkcji. 
    '''
    with sqlite3.connect(database_name) as conn:
        df.to_sql('job_offers', conn, if_exists='replace', index=False)


def main():
    '''
    Funkcja tworząca (użycie funkcji aggregate_data) i wyświetlająca zagregowany DataFrame zawierający web scrapowane dane z wszystkich 3 serwisów. Funkcja ta także zapisuje ten DataFrame do bazy danych SQLite3 przy użyciu funkcji save_to_sqlite
    i wyświetla potwierdzenie, że dane udało się zapisać.
    '''
    aggregated_df = aggregate_data()
    print(aggregated_df)
    save_to_sqlite(aggregated_df)
    print("Data saved to SQLite.")

    '''
    Tutaj na pamiątkę sposób wyświetlenia całej tabeli równo, samo print niestety nie pokazuje całej tabeli dzięki poniższemu sposobowi jest to o wiele bardziej czytelne (niestety nie ma w niej employment_type, ponieważ już zająłem się czymś innym)
    '''
    # print(f"\n-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    # print(f"| Title                                                        | Company                                     |  Requirements        | salary_from          | salary_to            | currency             | city            | source       |")
    # print(f"-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

    # for index, rows in aggregated_df.iterrows():
    #     print(f"| {rows['title'][:59]:<60} | {rows['company'][:42]:<43} | {rows['requirements'][:19]:<20} | {rows['salary_from']:<20} | {rows['salary_to']:<20} | {rows['currency']:<20} | {rows['city'][:14]:<15} | {rows['source']:<12} |")

    # print(f"-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

if __name__ == "__main__":
    main()