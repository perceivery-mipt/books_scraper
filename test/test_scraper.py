from scraper import scrape_books
import pytest
import sys
import os
import requests
from bs4 import BeautifulSoup
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="session")
def all_books():
    """
    pytest.fixture, которая вызывает scrape_books() один раз за всю
    сессию тестирования и кэширует результат, чтобы не выполнять
    парсинг повторно при каждом тесте.

    Returns:
        list: Список словарей с данными о книгах.
    """
    return scrape_books(is_save=False)

def get_expected_total_books() -> int:
    """
    Извлекает общее количество книг, указанных на сайте Books to Scrape
    (с главной страницы).

    Дополнительная функция для проверок

    :returns
        int(number_str): Количество книг на сайте.

    """
    url = "http://books.toscrape.com/index.html"
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # Находим строку вроде "1,000 results"
    result_text = soup.select_one("form.form-horizontal").text
    match = re.search(r"([\d,]+)\s+results", result_text)

    if match:
        number_str = match.group(1).replace(",", "")
        return int(number_str)
    else:
        raise ValueError("Не удалось определить количество книг с сайта.")


def test_get_book_data_keys(all_books):
    """
    Проверяет корректность структуры данных, возвращаемых scrape_books.

    Args:
        all_books (list): Список словарей с данными о книгах,
        получаемый из fixture pytest.

    Проверки:
        1. Результат — это список.
        2. Список не пустой.
        3. Каждая книга — это словарь.
        4. В каждой книге присутствуют все обязательные ключи.
    """

    books = all_books
    print(f"Найдено книг: {len(books)}")

    expected_keys = [
        "title", "price", "rating", "availability", "description",
        "upc", "product_type", "price_excl_tax", "price_incl_tax",
        "tax", "num_reviews"
    ]

    # Проверка типа
    assert isinstance(
        books, list), (f"ОШИБКА: scrape_books должна возвращать list, а вернулся {
            type(books)}")
    print("Тип данных: list — OK")

    # Проверка, что список не пустой
    assert len(books) > 0, "ОШИБКА: Список книг пуст!"
    print("Список книг не пустой — OK")

    # Проверка структуры каждой книги
    for idx, book in enumerate(books, start=1):
        assert isinstance(book, dict), (
            f"ОШИБКА: Книга №{idx} имеет тип {type(book)}, ожидается dict"
        )

        missing_keys = [key for key in expected_keys if key not in book]
        assert not missing_keys, (
            f"ОШИБКА: В книге №{idx} отсутствуют ключи: {missing_keys}"
        )

    print("Тип данных: dict — OK")
    print("Все ключи присутствуют — OK")

    print("Ключи книги:")
    for k in books[0].keys():
        print(f"   - {k}")


def test_total_number_of_books(all_books):
    """
    Проверяет, что общее количество собранных книг соответствует числу,
    указанному на главной странице сайта Books to Scrape.

    Args:
        all_books (list): Список словарей с данными о книгах,
        получаемый из fixture pytest.

    Проверки:
        1. Общее количество собранных книг совпадает с числом,
           полученным с сайта (функция get_expected_total_books()).
    """

    expected_total = get_expected_total_books()
    actual_total = len(all_books)

    print(f"Ожидаемое количество книг на сайте: {expected_total}")

    assert actual_total == expected_total, (
        f"ОШИБКА: Ожидалось {expected_total} книг, получено: {actual_total}"
    )

    print(f"Количество книг совпадает: {actual_total} — OK")


def test_title_is_valid(all_books):
    """
    Проверяет корректность поля 'title' у всех книг, собранных функцией scrape_books.

    Args:
        all_books (list): Список словарей с данными о книгах, предоставленный через pytest fixture.

    Проверки:
        - Поле 'title' присутствует у каждой книги.
        - Значение поля 'title' имеет тип str.
        - Строка 'title' не является пустой или пробельной.
    """

    for idx, book in enumerate(all_books, start=1):
        title = book.get("title", "")

        assert isinstance(title, str), (
            f"ОШИБКА: У книги №{idx} заголовок не строка: {type(title)}"
        )

        assert title.strip(), (
            f"ОШИБКА: У книги №{idx} заголовок пустой!"
        )

    print("Заголовки книг корректны — OK")
