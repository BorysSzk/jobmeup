import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import io
import os
import base64
import sqlite3
from collections import Counter
from matplotlib import rcParams
from matplotlib import font_manager as fm

custom_font_path = 'static/fonts/Rajdhani-Medium.ttf'
custom_font2_path = 'static/fonts/Rajdhani-SemiBold.ttf'
custom_font = fm.FontProperties(fname=custom_font_path)
custom_font2 = fm.FontProperties(fname=custom_font2_path)
rcParams['font.family'] = custom_font.get_name()
rcParams['font.family'] = custom_font2.get_name()

matplotlib.use('Agg')


def db_connection():
    '''
    Funkcja odpowiadająca z połączenie z bazą danych (lub stworzenie jej jeśli nie istnieje), a także zamianę wierszy na "sqlite3.Row".
    Sqlite3.Row zamienia każdą krotkę wynikową z zapytań SQL na obiekt sqlite3.Row, który pozwala na dostęp do danych za pomocą indeksów liczbowych i konkretnych nazw kolumn.
    '''
    conn = sqlite3.connect('job_offers.db')
    conn.row_factory = sqlite3.Row

    return conn


def jobs_per_city_bar_plot(save_path = 'static/plots/jobs_per_city_bar_plot.png'):
    '''
    Wykres słupkowy liczby ofert pracy na dane miasto z zapisem wykresu, jako obraz .png
    '''
    conn = db_connection()
    cursor = conn.execute("SELECT city, COUNT(title) as job_count FROM job_offers GROUP BY city")
    data = cursor.fetchall()
    conn.close()

    cities = [row['city'] for row in data]
    job_counts = [row['job_count'] for row in data]

    plt.figure(figsize = (8, 4))
    plt.bar(cities, job_counts, color = '#bcfcfc', edgecolor="#8ce4fc")
    plt.xlabel('MIASTA', fontproperties=custom_font2)
    plt.ylabel('LICZBA OFERT', fontproperties=custom_font2)
    plt.title('LICZBA OFERT PRACY W DANYM MIEŚCIE (LUB ZDALNIE)', fontproperties=custom_font2)
    plt.xticks(rotation = 45, ha = 'right', fontproperties=custom_font)
    plt.yticks(fontproperties=custom_font)

    ax = plt.gca()
    ax.set_facecolor('#24241c')

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='png', bbox_inches='tight')
    plt.close()

    return save_path


def highest_max_salaries_per_city_bar_plot(save_path = 'static/plots/highest_max_salaries_per_city_bar_plot.png'):
    '''
    Wykres słupkowy najwyższych maksymalnych wynagrodzeń na dane miasto z zapisem wykresu, jako obraz .png
    '''
    conn = db_connection()
    cursor = conn.execute("""
        SELECT city, MAX(CAST(REPLACE(salary_to, ' ', '') AS INTEGER)) as highest_max_salary 
        FROM job_offers
        WHERE salary_to != 'Nieujawnione' 
        GROUP BY city""")
    data = cursor.fetchall()
    conn.close()

    cities = [row['city'] for row in data]
    highest_max_salaries = [row['highest_max_salary'] for row in data]

    plt.figure(figsize = (8, 3))
    plt.bar(cities, highest_max_salaries, color = '#42fbfb', edgecolor="#8ce4fc")
    plt.xlabel('MIASTA', fontproperties=custom_font2)
    plt.ylabel('NAJWYŻSZE MAKSYMALNE WYNAGRODZENIA', fontproperties=custom_font2)
    plt.title('NAJWYŻSZE MAKSYMALNE WYNAGRODZENIA W DANYM MIEŚCIE (LUB ZDALNIE)', fontproperties=custom_font2)
    plt.xticks(rotation = 45, ha = 'right', fontproperties=custom_font)
    plt.yticks(fontproperties=custom_font)

    ax = plt.gca()
    ax.set_facecolor('#24241c')

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='png', bbox_inches='tight')
    plt.close()

    return save_path


def lowest_min_salaries_per_city_bar_plot(save_path = 'static/plots/lowest_min_salaries_per_city_bar_plot.png'):
    '''
    Wykres słupkowy najniższych minimalnych wynagrodzeń na dane miasto z zapisem wykresu, jako obraz .png
    '''
    conn = db_connection()
    cursor = conn.execute("""
        SELECT city, MIN(CAST(REPLACE(salary_from, ' ', '') AS INTEGER)) as lowest_min_salary 
        FROM job_offers
        WHERE salary_from != 'Nieujawnione' 
        GROUP BY city""")
    data = cursor.fetchall()
    conn.close()

    cities = [row['city'] for row in data]
    lowest_min_salaries = [row['lowest_min_salary'] for row in data]

    plt.figure(figsize = (8, 3))
    plt.bar(cities, lowest_min_salaries, color = '#48e9e9', edgecolor="#8ce4fc")
    plt.xlabel('MIASTA', fontproperties=custom_font2)
    plt.ylabel('NAJNIŻSZE MINIMALNE WYNAGRODZENIA', fontproperties=custom_font2)
    plt.title('NAJNIŻSZE MINIMALNE WYNAGRODZENIA W DANYM MIEŚCIE (LUB ZDALNIE)', fontproperties=custom_font2)
    plt.xticks(rotation = 45, ha = 'right', fontproperties=custom_font)
    plt.yticks(fontproperties=custom_font)

    ax = plt.gca()
    ax.set_facecolor('#24241c')

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='png', bbox_inches='tight')
    plt.close()

    return save_path


def employment_types_pie_chart(save_path = 'static/plots/employment_types_pie_chart.png'):
    '''
    Diagram kołowy rodzajów zatrudnienia w procentach z zapisem wykresu, jako obraz .png
    '''
    conn = db_connection()
    cursor = conn.execute("SELECT employment_type FROM job_offers")
    data = cursor.fetchall()
    conn.close()

    employment_counter = Counter()
    for row in data:
        employment_types = row['employment_type']
        if employment_types != 'Nieujawnione':
            types = [t.strip() for t in employment_types.split(',')]
            employment_counter.update(types)
        else:
            employment_counter['Nieujawnione'] += 1

    group_mapping = {
        'B2B': 'B2B',
        'Permanent': 'Stałe',
        'UoP': 'Umowy o pracę',
        'UZ': 'Umowy o zlecenie',
        'Mandate': 'Umowy o zlecenie',
        'Dowolna': 'Dowolne',
        'Any': 'Dowolne',
        'Nieujawnione': 'Nieujawnione'
    }

    grouped_counts = Counter()
    for key, count in employment_counter.items():
        group_name = group_mapping.get(key)
        grouped_counts[group_name] += count

    total_offers = sum(grouped_counts.values())
    labels = [
        f"{group} {count / total_offers:.1%}" 
        for group, count in grouped_counts.items()
    ]
    sizes = list(grouped_counts.values())

    #explode = (0, 0.1, 0, 0.1, 0, 0.1)

    fig, ax = plt.subplots(figsize=(8, 4), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(sizes,
                           wedgeprops=dict(width=0.5), 
                           #explode=explode,
                           shadow=True,
                           startangle=-88, 
                           colors=['#538795', '#bcfcfc', '#7dc5d9', '#76ffff', '#24241c', '#6dcdcd']
                           )

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops = dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center", fontproperties=custom_font)

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(
            labels[i],
            xy=(x, y),
            xytext=(1.25 * np.sign(x), 1.4 * y),
            horizontalalignment=horizontalalignment,
            **kw
        )

    plt.title("RODZAJE ZATRUDNIENIA W PROCENTACH", y=1.1, fontproperties=custom_font2)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format = 'png', bbox_inches='tight')

    return save_path