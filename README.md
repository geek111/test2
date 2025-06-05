# Aplikacja do śledzenia cen produktów

Przykładowa aplikacja w Pythonie pozwalająca na monitorowanie cen w różnych sklepach internetowych.

## Uruchomienie

```bash
python3 main.py
```

Można również skorzystać z prostego interfejsu WWW opartego na Flasku:

```bash
python3 web.py
```

Domyślnie lista produktów znajduje się w pliku `products.json`. Moduły sklepów znajdują się w katalogu `price_tracker/shops` i dziedziczą po klasie `ShopModule`.

### Zarządzanie przez Web GUI

- Dodawanie i usuwanie produktów odbywa się z poziomu listy produktów. Każdy wiersz ma przycisk **Delete**.
- Ceny można sprawdzić ręcznie przez link **Check prices now**.
- Automatyczne sprawdzanie można tymczasowo wstrzymać lub wznowić przyciskami **Pause checking** i **Resume checking**.
  Stan wstrzymania przechowywany jest w atrybucie ``PriceTracker.paused``.
