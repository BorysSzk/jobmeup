from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import logging
import csv
from visualizations import jobs_per_city_bar_plot
from visualizations import highest_max_salaries_per_city_bar_plot
from visualizations import lowest_min_salaries_per_city_bar_plot
from visualizations import employment_types_pie_chart


app = Flask(__name__)
database = 'job_offers.db'


def db_connection():
    '''
    Funkcja połączenia z bazą danych, a także zamiany wierszy na "sqlite3.Row".
    Sqlite3.Row zamienia każdą krotkę wynikową z zapytań SQL na obiekt sqlite3.Row, który pozwala na dostęp do danych za pomocą indeksów liczbowych i konkretnych nazw kolumn.
    '''
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    '''
    Funkcja głównego endpointu
    '''
    return render_template('menu.html')
    

@app.route('/oferty-pracy')
def table_full():
    '''
    Funkcja endpointu z pełną tabelą ofert pracy
    '''
    conn = db_connection()
    job_offers = conn.execute('SELECT * FROM job_offers').fetchall()
    conn.close()
    return render_template('table_full.html', job_offers = job_offers)


@app.route('/filtr', methods=['GET', 'POST'])
def filtr():
    '''
    Funkcja endpointu z filtrowaniem ofert pracy. W tej funkcji są stworzone zmienne odpowiednio dla tych danych, przez które filtrujemy. 
    Jest także dodany if z 'clear', który z połączeniem z html pozwala na wyczyszczenie filtrów.
    W tym if'ie poniżej w else, dla każdej zmiennej *kolumna*_filter są zapisane odpowiednie zapytania filtrujące dane.
    '''
    title_filter = request.args.get('title', '')
    company_filter = request.args.get('company', '')
    requirements_filter = request.args.get('requirements', '')
    salary_from_filter = request.args.get('salary_from', '')
    salary_to_filter = request.args.get('salary_to', '')
    currency_filter = request.args.get('currency', '')
    undisclosed_salary_and_currency_filter = request.args.get('undisclosed_salary_and_currency_filter', '')
    city_filter = request.args.get('city', '')
    employment_type_filter = request.args.get('employment_type', '')
    source_filter = request.args.get('source', '')
    sort_key = request.args.get('sort_key', '')
    sort_order = request.args.get('sort_order', '')

    if 'clear' in request.args:
        query = 'SELECT * FROM job_offers'
        params = []
        title_filter = ''
        company_filter = ''
        requirements_filter = ''
        salary_from_filter = ''
        salary_to_filter = ''
        currency_filter = ''
        city_filter = ''
        employment_type_filter = ''
        source_filter = ''
        undisclosed_salary_and_currency_filter = None
        sort_key = None
        sort_order = None

    else:
        query = 'SELECT * FROM job_offers WHERE 1=1'
        params = []

        if title_filter:
            query += ' AND LOWER(title) LIKE ?'
            params.append(f'%{title_filter.lower()}%')
        if company_filter:
            query += ' AND LOWER(company) LIKE ?'
            params.append(f'%{company_filter.lower()}%')
        if requirements_filter:
            keywords = [kw.strip().lower() for kw in requirements_filter.split(',')]
            for keyword in keywords:
                query += ' AND LOWER(requirements) LIKE ?'
                params.append(f'%{keyword}%')
        if salary_from_filter:
            query += ' AND CAST(REPLACE(salary_from, " ", "") AS INTEGER) >= ?'
            params.append(int(salary_from_filter))
        if salary_to_filter:
            query += ' AND CAST(REPLACE(salary_to, " ", "") AS INTEGER) <= ?'
            params.append(int(salary_to_filter))
        if currency_filter:
            query += ' AND LOWER(currency) LIKE ?'
            params.append(f'%{currency_filter.lower()}%')
        if undisclosed_salary_and_currency_filter == 'on':
            query += ' AND (salary_from = "Nieujawnione" OR salary_to = "Nieujawnione" OR currency = "Nieujawnione")'
        if city_filter:
            query += ' AND LOWER(city) LIKE ?'
            params.append(f'%{city_filter.lower()}%')
        if employment_type_filter:
            if employment_type_filter == 'Mandate':
                query += ' AND (employment_type LIKE ? OR employment_type LIKE ?)'
                params.append('%Mandate%')
                params.append('%UZ%')
            elif employment_type_filter == 'Dowolna':
                query += ' AND (employment_type LIKE ? OR employment_type LIKE ?)'
                params.append('%Dowolna%')
                params.append('%Any%')
            else:
                query += ' AND employment_type = ?'
                params.append(employment_type_filter)
        if source_filter:
            query += ' AND source = ?'
            params.append(source_filter)
        if sort_key and sort_order:
            query += f' AND {sort_key} != "Nieujawnione" ORDER BY CAST(REPLACE({sort_key}, " ", "") AS INTEGER) {sort_order}'
            
    conn = db_connection()
    job_offers = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'filter.html', 
        job_offers=job_offers, 
        title_filter=title_filter, 
        company_filter=company_filter,
        requirements_filter=requirements_filter,
        salary_from_filter=salary_from_filter,
        salary_to_filter=salary_to_filter,
        currency_filter=currency_filter,
        undisclosed_salary_and_currency_filter=undisclosed_salary_and_currency_filter,
        city_filter=city_filter,
        employment_type_filter=employment_type_filter,
        source_filter=source_filter,
        sort_key=sort_key, 
        sort_order=sort_order
        )


@app.route('/wizualizacje')
def visualizations():
    '''
    Funkcja wywołująca funkcje wyświetlające wizualizacje z pliku visualizations.py (tam więcej odnośnie poniższych wywołanych funkcji)
    '''
    jobs_per_city_bar_plot()
    highest_max_salaries_per_city_bar_plot()
    lowest_min_salaries_per_city_bar_plot()
    employment_types_pie_chart()
    return render_template('visualizations.html')


@app.route('/eksport', methods=['GET'])
def export_data():
    '''
    Funkcja umożliwiająca eksportowanie pliku job_offers.db jako plik .csv - jest ona podpięta do formularza z przyciskiem w pliku menu.html
    '''
    conn = sqlite3.connect('job_offers.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_offers")
    rows = cursor.fetchall()

    csv_filename = 'job_offers.csv'

    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow([description[0] for description in cursor.description])
        writer.writerows(rows)

    conn.close()
    return send_file(csv_filename, as_attachment=True, download_name=csv_filename)


if __name__ == '__main__':
    app.run(debug=True)