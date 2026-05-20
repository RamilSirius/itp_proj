# Book Analyzer CLI — Presentation Script

**Project**: Book Analyzer CLI — анализатор книг на Python (readability, sentiment, top phrases)

Распределение: Member 1 объясняет части 1, 3, 5, 7 — Member 2 объясняет части 2, 4, 6.

---

## Member 1 — Part 1: Foundation & Logic (10 pts)

**Файлы**: `main.py`, `utils/validators.py`

### Что объяснять:

**Control Flow** — вся логика меню находится в `main.py`.

```python
# main.py — главный цикл меню
while True:
    choice = input("Choice: ").strip()
    if choice == "1":
        action_load(library)
    elif choice == "2":
        action_list(library)
    elif choice == "0":
        break
```

Программа запускается и держит пользователя в цикле `while True`, пока он не выберет `0`. Каждый пункт меню — отдельная функция (`action_load`, `action_list` и т.д.), это делает код читаемым.

**Conditional statements и logical operators** — в `utils/validators.py` есть функция `parse_menu_choice`, которая проверяет ввод:

```python
def parse_menu_choice(raw: str, valid: set) -> str | None:
    choice = raw.strip()
    if not choice or choice not in valid:
        return None
    return choice
```

**User-friendly CLI** — меню выводит все доступные варианты, сообщения об ошибках понятные ("Book not found", "Invalid choice"), есть `--demo` режим для быстрой демонстрации.

**Loops** — цикл `for` используется чтобы запускать несколько анализаторов по очереди:

```python
for analyzer in analyzers:
    result = analyzer.analyze(book)
    report.add_result(analyzer.name, result)
```

---

## Member 2 — Part 2: Data Management & Collections (8 pts)

**Файлы**: `core/library.py`, `core/book.py`, `core/report.py`, `utils/storage.py`, `utils/stopwords.py`

### Что объяснять:

**Collections** — проект использует все четыре типа коллекций:

| Тип | Где используется | Зачем |
|-----|-----------------|-------|
| `dict` | `Library._books` | Хранит книги по названию (быстрый поиск) |
| `list` | Результаты анализаторов (top_words, top_bigrams) | Упорядоченный список слов |
| `set` / `frozenset` | `STOPWORDS`, `POSITIVE_WORDS`, `NEGATIVE_WORDS` в `utils/stopwords.py` | Быстрая проверка принадлежности O(1) |
| `tuple` | Пары слов в биграммах `(word1, word2)` | Неизменяемые пары |

Пример из `core/library.py`:
```python
self._books: dict[str, Book] = {}  # title → Book object
```

Пример `frozenset` из `utils/stopwords.py`:
```python
STOPWORDS: frozenset[str] = frozenset({"the", "a", "an", "and", "is", ...})
```

**Data Persistence** — `utils/storage.py` отвечает за сохранение отчётов.

- **JSON** через `report_to_json()` — сохраняет полный отчёт со всеми метриками
- **CSV** через `report_to_csv()` — плоская таблица (analyzer, key, value)
- **OS module** — `os.makedirs()`, `os.path.join()` для создания директорий и путей

```python
import json, csv, os

def report_to_json(report, output_dir):
    ensure_dir(output_dir)
    path = os.path.join(output_dir, _make_filename(report, "json"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)
    return path
```

Библиотека (`Library`) тоже умеет сохранять своё состояние:
```python
# core/library.py
def save_state(self, path):
    data = {title: {"author": b.author, "filepath": b.filepath} ...}
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
```

---

## Member 1 — Part 3: Core & Advanced OOP (27 pts)

**Файлы**: `analyzers/base.py`, `analyzers/readability.py`, `analyzers/sentiment.py`, `analyzers/phrases.py`, `core/book.py`, `core/library.py`, `core/report.py`

### Что объяснять:

**Core OOP (15 pts)** — все доменные сущности — классы с инкапсуляцией.

Класс `Book` в `core/book.py`:
```python
class Book:
    def __init__(self, title, author, filepath):
        self._title = title      # приватный атрибут
        self._author = author
        self._filepath = filepath
        self._text = None        # загружается лениво

    @property
    def title(self) -> str:      # доступ через property
        return self._title
```

Все атрибуты с `_` — приватные. Доступ к ним только через `@property` геттеры — это **инкапсуляция**.

**Inheritance (Наследование)** — `BaseAnalyzer → ReadabilityAnalyzer / SentimentAnalyzer / PhraseAnalyzer`:

```
BaseAnalyzer (analyzers/base.py)
    ├── ReadabilityAnalyzer  (analyzers/readability.py)
    ├── SentimentAnalyzer    (analyzers/sentiment.py)
    └── PhraseAnalyzer       (analyzers/phrases.py)
```

```python
# analyzers/base.py
from abc import ABC, abstractmethod

class BaseAnalyzer(ABC):
    NAME = "base"

    @abstractmethod
    def analyze(self, book) -> dict:
        ...

# analyzers/readability.py
class ReadabilityAnalyzer(BaseAnalyzer):
    NAME = "readability"

    def analyze(self, book) -> dict:
        # реализация Flesch score
        ...
```

**Polymorphism (Полиморфизм)** — `main.py` вызывает `analyze()` одинаково для всех трёх анализаторов, не зная их конкретный тип:

```python
# main.py
for analyzer in analyzers:          # [Readability, Sentiment, Phrase]
    result = analyzer.analyze(book) # один и тот же вызов — разный результат
```

**Association (Связи между классами)**:
- `Library` **manages** много `Book` объектов (one-to-many)
- `Report` **references** один `Book` объект (one-to-one)

---

## Member 2 — Part 4: Functions & Functional Programming (8 pts)

**Файлы**: `analyzers/readability.py`, `analyzers/sentiment.py`, `analyzers/phrases.py`, `utils/validators.py`

### Что объяснять:

**Modular Logic** — каждая функция делает одно дело, принимает позиционные и keyword аргументы.

`PhraseAnalyzer` принимает `top_n` как keyword argument:
```python
class PhraseAnalyzer(BaseAnalyzer):
    def __init__(self, top_n: int = 10):  # keyword arg с дефолтом
        self._top_n = top_n
```

**`lambda`** — используется для сортировки слов по частоте:
```python
# analyzers/phrases.py
sorted_words = sorted(
    counter.items(),
    key=lambda pair: (-pair[1], pair[0])  # сначала по частоте↓, потом алфавит↑
)
```

**`map()`** — используется в `ReadabilityAnalyzer` для подсчёта слогов:
```python
# analyzers/readability.py
syllable_counts = map(self._count_syllables, words)
total_syllables = sum(syllable_counts)
```

**`filter()`** — используется в `SentimentAnalyzer` для поиска эмоциональных слов:
```python
# analyzers/sentiment.py
positive = list(filter(lambda w: w in POSITIVE_WORDS, tokens))
negative = list(filter(lambda w: w in NEGATIVE_WORDS, tokens))
```

И в `PhraseAnalyzer` для удаления стоп-слов:
```python
# analyzers/phrases.py
content_words = list(filter(lambda w: w not in STOPWORDS, tokens))
```

Все три инструмента (`lambda`, `map`, `filter`) — функциональное программирование без изменения состояния (no side effects).

---

## Member 1 — Part 5: Modules, Packages & Organization (10 pts)

**Файлы**: `core/__init__.py`, `analyzers/__init__.py`, `utils/__init__.py`, `tests/__init__.py`, все `__init__.py` файлы

### Что объяснять:

**Package Structure** — проект разбит на 4 пакета (4 директории с `__init__.py`):

```
itp_proj/
├── core/           # Доменный слой — сущности (Book, Library, Report)
│   └── __init__.py
├── analyzers/      # Слой анализа — 3 анализатора
│   └── __init__.py
├── utils/          # Вспомогательный слой — декораторы, validators, storage
│   └── __init__.py
└── tests/          # Тесты
    └── __init__.py
```

Каждый `__init__.py` экспортирует публичный API пакета:

```python
# core/__init__.py
from .book import Book
from .library import Library
from .report import Report

__all__ = ["Book", "Library", "Report"]
```

```python
# analyzers/__init__.py
from .base import BaseAnalyzer
from .readability import ReadabilityAnalyzer
from .sentiment import SentimentAnalyzer
from .phrases import PhraseAnalyzer

__all__ = ["BaseAnalyzer", "ReadabilityAnalyzer", "SentimentAnalyzer", "PhraseAnalyzer"]
```

**Imports** — в `main.py` все импорты чистые:
```python
from core import Book, Library, Report
from analyzers import ReadabilityAnalyzer, SentimentAnalyzer, PhraseAnalyzer
from utils.storage import report_to_json, report_to_csv
from utils.validators import is_valid_filename
```

**Built-in modules** используются во всём проекте:

| Модуль | Где | Зачем |
|--------|-----|-------|
| `os` | `utils/storage.py`, `main.py` | Пути, создание директорий |
| `json` | `utils/storage.py`, `core/library.py` | Сериализация данных |
| `csv` | `utils/storage.py` | Экспорт отчётов |
| `re` | `utils/validators.py` | Регулярные выражения |
| `math` | `analyzers/readability.py` | Формула Flesch score |
| `sys` | `main.py` | `sys.argv` для `--demo` режима |
| `collections` | `analyzers/phrases.py` | `Counter` для подсчёта слов |
| `datetime` | `core/report.py` | Временная метка отчёта |
| `unittest` | `tests/test_analyzers.py` | Unit тесты |

---

## Member 2 — Part 6: Testing, Decorators & Iterators (16 pts)

**Файлы**: `tests/test_analyzers.py`, `utils/decorators.py`, `core/book.py`, `utils/validators.py`

### Что объяснять:

**Unit Tests (8 pts)** — файл `tests/test_analyzers.py` содержит 8 тестов в 6 классах:

```python
class ReadabilityTests(unittest.TestCase):
    def test_simple_sentence(self):
        book = _make_book("The cat sat on the mat. It was a sunny day.")
        result = ReadabilityAnalyzer().analyze(book)
        self.assertIn("score", result)             # assertIn
        self.assertGreater(result["score"], 0)     # assertGreater

class SentimentTests(unittest.TestCase):
    def test_positive_text(self):
        book = _make_book("I love this wonderful happy joyful beautiful place.")
        result = SentimentAnalyzer().analyze(book)
        self.assertEqual(result["label"], "positive")  # assertEqual

    def test_negative_text(self):
        book = _make_book("I hate this terrible awful sad miserable place.")
        result = SentimentAnalyzer().analyze(book)
        self.assertNotEqual(result["label"], "positive")  # assertNotEqual
```

Запуск тестов: `python -m pytest tests/` или `python -m unittest discover`.

**Decorator (3 pts)** — `@log_action` в `utils/decorators.py`:

```python
def log_action(func):
    def wrapper(*args, **kwargs):
        class_name = args[0].__class__.__name__ if args else ""
        print(f"[log_action] -> {class_name}.{func.__name__} starting")
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            print(f"[log_action] <- {class_name}.{func.__name__} done in {elapsed:.4f}s")
            return result
        except Exception as e:
            print(f"[log_action] !! {class_name}.{func.__name__} failed: {e}")
            raise
    return wrapper
```

Применяется к каждому методу `analyze()`:
```python
class ReadabilityAnalyzer(BaseAnalyzer):
    @log_action          # ← декоратор
    def analyze(self, book):
        ...
```

**Generator / Iterator (3 pts)** — `Book.iter_lines()` в `core/book.py`:

```python
def iter_lines(self):
    """Generator: yields one line at a time without loading entire file."""
    with open(self._filepath, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")
```

Вместо загрузки всей книги в память — читаем построчно. Это важно для больших файлов.

**Regex (2 pts)** — `utils/validators.py` использует модуль `re`:

```python
import re

_FILENAME_RE = re.compile(r"^[\w\- ]+\.txt$")   # безопасное имя файла
_WORD_RE     = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+)?")  # токенизация слов
_SENTENCE_RE = re.compile(r"[.!?]+\s+")          # разбивка на предложения

def is_valid_filename(name: str) -> bool:
    return bool(_FILENAME_RE.match(name))

def tokenize_words(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())
```

---

## Member 1 — Part 7: Planning & Real-World Application (16 pts)

**Файлы**: `README.md`, весь проект целиком

### Что объяснять:

**Project Planning (4 pts)** — `README.md` содержит:
- Описание архитектуры (4 слоя: CLI, Core, Analyzers, Utils)
- Иерархию классов (BaseAnalyzer → 3 subclasses)
- Логику потока данных (User → CLI → Library → Analyzers → Report → Storage)
- Инструкцию по запуску

**Architecture Overview** (для объяснения):

```
User Input
    ↓
main.py  (CLI Layer)
    ↓                      ↓
core/Book             utils/validators
core/Library          (input validation)
core/Report
    ↓
analyzers/
├── ReadabilityAnalyzer  → Flesch score
├── SentimentAnalyzer    → polarity label
└── PhraseAnalyzer       → top words
    ↓
utils/storage
├── report_to_json()  → reports/*.json
└── report_to_csv()   → reports/*.csv
```

**Collaboration (4 pts)** — проект разделён по слоям:
- Member 1 отвечал за: `main.py` (CLI), `analyzers/` (логика анализа), `core/` (domain entities)
- Member 2 отвечал за: `utils/` (decorators, validators, storage, stopwords), `tests/` (unit tests), `core/` (persistence методы)

**Quality Assurance (4 pts)**:
- **PEP8**: все файлы следуют стандарту (4 пробела, snake_case, 79 символов в строке)
- **Docstrings**: каждый класс и публичный метод задокументирован
  ```python
  def analyze(self, book: Book) -> dict:
      """Compute Flesch Reading Ease score for the given book."""
  ```
- **Error handling**: try/except везде где возможны ошибки
  ```python
  try:
      book.load()
  except FileNotFoundError as e:
      print(f"Error: {e}")
      return
  ```

**Execution (4 pts)** — все 8 тестов проходят, программа запускается без ошибок:
```
python main.py --demo    # демо режим
python -m unittest discover tests/   # все тесты
```

---

## Краткая шпаргалка: кто что объясняет

| Часть | Member | Ключевые файлы |
|-------|--------|---------------|
| 1. Foundation & Logic | **Member 1** | `main.py`, `utils/validators.py` |
| 2. Data Management | **Member 2** | `core/library.py`, `utils/storage.py`, `utils/stopwords.py` |
| 3. OOP | **Member 1** | `analyzers/base.py` + 3 subclasses, `core/*.py` |
| 4. Functional Programming | **Member 2** | `analyzers/phrases.py`, `analyzers/sentiment.py`, `analyzers/readability.py` |
| 5. Modules & Packages | **Member 1** | все `__init__.py`, import структура |
| 6. Testing, Decorators, Iterators | **Member 2** | `tests/test_analyzers.py`, `utils/decorators.py`, `core/book.py` |
| 7. Planning & Real-World App | **Member 1** | `README.md`, общая архитектура |
