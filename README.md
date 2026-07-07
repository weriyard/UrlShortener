# UrlShortener

Prosty skracacz URL-i oparty o Django + Django REST Framework.


## Dodatkowe założenia:
- dla kolejnych wywołań API generowany jest nowy short link nawet dla tego samego oryginalnego URL-a
- brak statystyk kliknięć itp.
- użycie `mypy` do statycznej analizy typów w Pythonie

## Uruchomienie aplikacji

```bash
cd urlshortener
python manage.py migrate
python manage.py runserver
```

Domyślnie lokalny adres aplikacji: `http://localhost:8000`.

## Konfiguracja

Ustawienia w `urlshortener/settings.py`:

| Ustawienie          | Domyślnie                          | Opis                                 |
|---------------------|------------------------------------|--------------------------------------|
| `SHORT_LINK_PREFIX` | `"shrt"`                           | Prefiks ścieżki krótkich linków.     |
| `SHORT_URL_CODE_LENGTH` | `7`                            | Długość generowanego short kodu.     |
| `ALPHABET`          | `a-zA-Z0-9` (base62)               | Znaki użyte do budowania short kodu. |

## API

### 1. Skrócenie URL-a

```
POST /shrt/links/
Content-Type: application/json

{"original_url": "http://example.com/very-very/long/url/even-longer"}
```

Odpowiedź `201 Created` — zwraca krótki link:

```json
{"short_link": "http://localhost:8000/shrt/I2iMRRK/"}
```

Przykład:

```bash
curl -X POST http://localhost:8000/shrt/links/ \
     -H "Content-Type: application/json" \
     -d '{"original_url": "http://example.com/very/long/url"}'
```

Kod jest generowany po stronie serwera i jest unikalny (przy kolizji API
ponawia próbę do 5 razy; po wyczerpaniu prób zwraca `500`).

### 2. Rozwinięcie krótkiego URL

Do pobrania oryginalnego URL-a na podstawie skróconego URL są dwa sposoby:

#### a) Redirect (cały link)

Wklejenie **całego** krótkiego linku w przeglądarkę (lub `curl -L`) kieruje na
oryginał — HTTP `302` z nagłówkiem `Location`:

```
GET /shrt/<code>/   →   302 Found, Location: <original_url>
```

```bash
curl -i http://localhost:8000/shrt/I2iMRRK/
# HTTP/1.1 302 Found
# Location: http://example.com/very/long/url
```

Wystarczy krótki link by uzyskać przekierowanie do oryginału.

#### b) Odczyt JSON

Zwraca oryginalny URL jako dane — przydatne w skryptach:

```
GET /shrt/links/<code>/   →   200 OK
```

```bash
curl http://localhost:8000/shrt/links/I2iMRRK/
```

```json
{"original_url": "http://example.com/very/long/url"}
```

Uwaga: tutaj wymagany jest **sam kod** (`I2iMRRK`), a nie cały link.


## Kontrola typów - `mypy`


```shell
cd urlshortener
mypy urlshortener --strict
```

## Inne rozważane możliwości (niezaimplementowane)

1. Uzyskanie oryginalnego linka na podstawie skróconego można by uzyskać na inne sposoby
- `GET /shrt/links/resolve/?url=<cały short link>` — serwer wycina kod z końca
  ścieżki i zwraca `{"original_url": ...}`.
- `POST /shrt/links/resolve/` z ciałem `{"short_link": "..."}` — omija problem
  URL-encodingu pełnego URL-a w query paramie.

2. Samą aplikację "skracacza" linków można by rozbudować o dodatkowe funkcje, np.:
- statystyki kliknięć (ile razy dany link został użyty),
- rozważyć czy wklejenie tego samego długiego linku powinno zwracać już raz wygenerowany short link

3. Dla zapewnienia wysokiej wydajności w produkcji można by rozważyć:
- cache w Redisie dla mapowania short link → original URL,
- użycie produkcyjnej bazy danych typu PostgreSQL zamiast SQLite.

4. W systemie produkcyjnym `SECRET_KEY` i inne klucze/tokeny itp. powinny być wstrzykiwane przez zmienne środowiskowe
  środowiska uruchomieniowego zamiast trzymania ich w repozytorium kodu.

5. Uruchomić aplikację w kontenerze Docker.  

## Testy

```bash
cd urlshortener
python manage.py test
```

Testy podzielone są na:

- `tests/test_unit.py` — testy jednostkowe np. funkcja generująca kod, ograniczenia modelu.
- `tests/test_e2e.py` — testy scenariuszy API: skrócenie, rozwinięcie (redirect + JSON), logika unikalności kodu.
