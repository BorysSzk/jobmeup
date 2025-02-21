# Job Me Up

## What is Job Me Up?
Job Me Up is a Python web scraper for IT job boards using BeautifulSoup & Selenium, storing data in an SQLite3 database, with a user-friendly Flask web app for filtering and a few example Pyplot visualizations. Scrape job offers, save them in a database and familiarize
yourself with the scraped data through viewing and filtering the data with the addition of a couple of sample visualizations that will give you a general view of job offer analysis.

## Build Prerequisites
Job Me Up's build environment requires a couple of libraries in order to work, but before that make sure that you have downloaded and using:
- Python 3.11.9 or newer from [here](https://www.python.org/downloads/).
- Firefox browser, required for Selenium with GeckoDriver.

## Installation
Clone the repository to your computer with:
```sh
git clone https://github.com/your_username/your_repo.git
```
If you don't have Git installed, you can download the repository as a ZIP file from the repository page.
<br>
After cloning/downloading the repository, navigate to the project directory (`project` folder) in your terminal and run the following command to install the libraries:
```sh
pip install -r requirements.txt
```

## Running Job Me Up
1. Make sure you are in the project directory.
2. To start the scraper, run:
```sh
python webscraping.py
```
This will begin the process of web scraping job offers from JustJoinIT, NoFluffJobs and RocketJobs websites. Scraped data will be saved to a newly created SQLite3 database.<br>
> [!NOTE]
> This might take some time, from a couple of seconds to a couple of minutes depending on your computer's RAM.
3. Next, start the web app by running:
```sh
python web-app.py
```
The app will launch at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Tech Stack
* Python
* BeautifulSoup
* Selenium
* GeckoDriver
* SQLite3
* Flask
* Pandas
* Matplotlib (Pyplot)
* NumPy
* Requests
* HTML, CSS, JavaScript (structure, styling and interaction)
