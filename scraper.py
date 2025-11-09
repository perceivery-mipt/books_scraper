import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import schedule
import time
import json
import select
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed



def get_book_data(book_url: str) -> dict:
    """
    Извлекает полную информацию о книге со страницы Books to Scrape.

    Args:
        book_url (str): URL страницы книги.

    Returns:
        dict: Словарь с информацией о книге:
            - title (str): Название книги.
            - price (str): Цена (с налогом).
            - rating (float): Рейтинг по 5-балльной шкале.
            - availability (str): Наличие на складе.
            - description (str): Описание книги.
            - upc (str): Уникальный код товара.
            - product_type (str): Тип продукта.
            - price_excl_tax (str): Цена без налога.
            - price_incl_tax (str): Цена с налогом.
            - tax (str): Налог.
            - num_reviews (str): Количество отзывов.
    """
    response = requests.get(book_url)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        print('ERROR REQUEST')

    # Название книги
    title = soup.find("div", class_="col-sm-6 product_main").h1.text.strip()

    # Цена
    price = soup.select_one("p.price_color").text.strip()

    # Рейтинг (в виде float)
    rating_class = soup.select_one("p.star-rating")["class"]
    rating_text = [cls for cls in rating_class if cls != "star-rating"][0]
    rating_map = {
        "One": 1.0,
        "Two": 2.0,
        "Three": 3.0,
        "Four": 4.0,
        "Five": 5.0
    }
    rating = rating_map.get(rating_text, None)

    # Наличие
    availability = soup.select_one("p.instock.availability").text.strip()

    # Описание (если есть)
    description_tag = soup.select_one("#product_description")
    if description_tag:
        description = description_tag.find_next_sibling("p").text.strip()
    else:
        description = "No description"

    # Таблица характеристик
    table = soup.select_one("table.table.table-striped")
    data = {row.th.text.strip(): row.td.text.strip()
            for row in table.select("tr")}

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "availability": availability,
        "description": description,
        "upc": data.get("UPC"),
        "product_type": data.get("Product Type"),
        "price_excl_tax": data.get("Price (excl. tax)"),
        "price_incl_tax": data.get("Price (incl. tax)"),
        "tax": data.get("Tax"),
        "num_reviews": data.get("Number of reviews"),
    }


def scrape_books(is_save: bool = False) -> list:
    """
    Собирает данные о всех книгах с сайта Books to Scrape.

    Args:
        is_save (bool): Если True, сохраняет данные в файл books_data.txt.

    Returns:
        list: Список словарей с данными о книгах.
    """
    catalogue_root = "http://books.toscrape.com/catalogue/"
    page_url_template = "http://books.toscrape.com/catalogue/page-{}.html"
    page_num = 1
    books = []
    max_threads = 20  # многопоточный парсинг

    while True:
        url = page_url_template.format(page_num)
        response = requests.get(url)
        if response.status_code == 404:
            print(f"Проблема обработки страницы {page_num}"
                  f"(не существует или ошибка доступа)")
            break

        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")

        book_links = soup.select("article.product_pod h3 a")
        urls = []
        for link in book_links:
            relative_url = link.get("href").replace('../../../', '')
            if not relative_url:
                continue  # защита от отсутствующих ссылок
            full_url = urljoin(catalogue_root, relative_url)
            urls.append(full_url)

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_url = {executor.submit(get_book_data, url):
                             url for url in urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    book_data = future.result()
                    books.append(book_data)
                except Exception as e:
                    print(f"Ошибка при обработке {url}: {e}")

        # print(f"[PAGE {page_num}]
        # Parsed {len(urls)} books,
        # total = {len(books)}")

        page_num += 1

    if is_save:
        with open("artifacts/books_data.txt", "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=2)

    return books


def job():
    """
    Запускает сбор данных о книгах и сохраняет результат в файл.
    Вызывает функцию scrape_books с флагом сохранения данных.
    Выводит сообщение в консоль до и после выполнения.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Выполняется сбор данных...")
    scrape_books(is_save=True)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Сбор данных завершён!")


if __name__ == "__main__":
    schedule.every().day.at("21:28").do(job)
    print('Задача запланирована.')
    print('Чтобы прервать задачу, нажмите s/S и нажмите Enter.')
    try:
        while True:
            schedule.run_pending()
            if select.select([sys.stdin], [], [], 0.1)[0]:
                if sys.stdin.readline().strip().lower() in ['S', 's']:
                    print("Загрузка данных останавливается..")
                    break
            time.sleep(1)

    except KeyboardInterrupt:
        print('\nОстановка выполнена!')
