# Aplikacja do śledzenia cen produktów

Przykładowa aplikacja w Pythonie pozwalająca na monitorowanie cen w różnych sklepach internetowych.

## Uruchomienie

Najpierw zainstaluj zależności:

```bash
pip install -r requirements.txt
```

Uruchomienie aplikacji w trybie śledzenia cen:

```bash
python3 main.py run
```

Domyślnie lista produktów znajduje się w pliku `products.json`. Zarejestrowane sklepy przechowywane są w pliku `shops.json`.
Moduły sklepów znajdują się w katalogu `price_tracker/shops` i dziedziczą po klasie `ShopModule`.

### Zarządzanie sklepami

Dodanie sklepu (należy podać pełną ścieżkę do klasy modułu):

```bash
python3 main.py add-shop shopa price_tracker.shops.shop_a:ShopA
```

Usunięcie sklepu:

```bash
python3 main.py remove-shop shopa
```

### Dodawanie produktów

```bash
python3 main.py add-product "Nazwa" "http://adres/produktu" shopa
```

### Ręczna edycja ceny

```bash
python3 main.py set-price "http://adres/produktu" 123.45
```
