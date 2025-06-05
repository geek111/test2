# Aplikacja do śledzenia cen produktów

Przykładowa aplikacja w Pythonie pozwalająca na monitorowanie cen w różnych sklepach internetowych.

## Instalacja zależności

Wymagane biblioteki (m.in. Flask, requests i BeautifulSoup) są zdefiniowane w pliku `requirements.txt`. Przed uruchomieniem aplikacji zainstaluj je poleceniem:

```bash
pip install -r requirements.txt
```

## Uruchomienie

```bash
python3 main.py
```

Można również skorzystać z prostego interfejsu WWW opartego na Flasku:

```bash
python3 web.py
```

Domyślnie lista produktów znajduje się w pliku `products.json`. Moduły sklepów znajdują się w katalogu `price_tracker/shops` i dziedziczą po klasie `ShopModule`.
Konfiguracja sklepów przechowywana jest w pliku `shops.json` i może być modyfikowana z poziomu interfejsu WWW.

### Format cen

Aplikacja obsługuje ceny zapisywane w formacie europejskim, np. `1 234,56 zł`.
Funkcja `parse_price` usuwa symbole walut oraz separatory tysięcy (spacje lub
kropki), zamienia przecinek na kropkę i usuwa ewentualne znaki interpunkcyjne
po wartości. Dzięki temu poprawnie działa zarówno dla notacji amerykańskiej,
jak i europejskiej. Dodatkowo aplikacja potrafi pobrać cenę zapisaną w
skryptach JSON‑LD (`<script type="application/ld+json">`).

### Zarządzanie przez Web GUI

- Dodawanie i usuwanie produktów odbywa się z poziomu listy produktów. Każdy wiersz ma przycisk **Delete**.
- Dodawanie i edycja sklepów dostępna jest poprzez link **Manage shops**.
- Ceny można sprawdzić ręcznie przez link **Check prices now**.
- Automatyczne sprawdzanie można tymczasowo wstrzymać lub wznowić przyciskami **Pause checking** i **Resume checking**.
  Stan wstrzymania przechowywany jest w atrybucie ``PriceTracker.paused``.

### Rozwiązywanie problemów

Jeśli podczas uruchamiania interfejsu WWW pojawi się błąd

```
AttributeError: 'PriceTracker' object has no attribute 'paused'
```

upewnij się, że Python importuje moduł z tego repozytorium. W interpreterze można sprawdzić ścieżkę poleceniami:

```python
import price_tracker
print(price_tracker.__file__)
```

Jeżeli wskazana zostanie inna lokalizacja (np. moduł zainstalowany globalnie),
 odinstaluj kolidujący pakiet lub zmień nazwę folderu projektu.
