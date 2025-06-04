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
