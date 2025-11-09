# Books Scraper

## Цель проекта

Цель проекта — спарсить данные о всех книгах с сайта [Books to Scrape](http://books.toscrape.com) и сохранить их в удобном формате. В рамках проекта реализован сбор информации о каждой книге: название, цена, рейтинг, наличие, описание и технические характеристики.

Данные сохраняются в файл `books_data.txt` в формате JSON, а также сопровождаются автотестами и возможностью регулярного запуска парсера по расписанию.

## Инструкция по запуску

1. Создать виртуальное окружение (рекомендуется):

   ```bash
   python -m venv venv
   source venv/bin/activate     # для Linux/macOS
   venv\\Scripts\\activate        # для Windows
   ```

2. Установить зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Запустить парсер вручную:

   ```bash
   python scraper.py
   ```

   По умолчанию данные собираются каждый день в 19:00 (или в указанное время) автоматически. Также можно вызвать `job()` вручную внутри `scraper.py`.

4. Запустить автотесты:

   ```bash
   pytest -s tests/test_scraper.py
   ```

## Используемые библиотеки

- `requests` — выполнение HTTP-запросов
- `beautifulsoup4` — HTML-парсинг
- `schedule` — планировщик задач
- `pytest` — автотестирование
- `concurrent.futures` — многопоточность для ускорения парсинга
- `json`, `time`, `datetime`, `sys`, `select` — встроенные модули Python

## Структура проекта

```
books_scraper/
├── scraper.py
├── artifacts/
│   └── books_data.txt
├── notebooks/
│   └── HW_03_python_ds_2025.ipynb
├── test/
│   └── test_scraper.py
│   └── __init__.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Автор

Фрейдина Алена Игоревна