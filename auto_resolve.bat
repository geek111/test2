@echo off
REM ------------------------------------------------------------------------
REM Skrypt: auto_resolve_conflicts.bat
REM Autor:  (Twoje imię lub Inżynier AI)
REM Data:   2025-06-xx
REM Opis:   Automatyczne rozwiązywanie konfliktów w Git (merge z gałęzią main)
REM         z użyciem strategii "theirs" lub "ours", a następnie push.
REM
REM Użycie:
REM   auto_resolve_conflicts.bat <branch_name> [<strategy>] [<remote>]
REM
REM   <branch_name> – nazwa Twojej gałęzi roboczej (np. feature/fix-price)
REM   <strategy>    – optional: "theirs" (domyślnie) lub "ours"
REM   <remote>      – optional: nazwa zdalnego repo (domyślnie "origin")
REM
REM Przykład:
REM   auto_resolve_conflicts.bat feature/fix-price theirs upstream
REM ------------------------------------------------------------------------

setlocal EnableExtensions EnableDelayedExpansion

REM ----------------------------------------
REM 1. Sprawdzenie parametrów
REM ----------------------------------------
if "%~1"=="" (
    echo.
    echo Błąd: Nie podano nazwy gałęzi.
    echo Użycie: %~nx0 ^<branch_name^> [^<strategy^>] [^<remote^>]
    echo.
    goto :EOF
)

set "BRANCH_NAME=%~1"

REM Jeśli nie podano strategii, domyślnie "theirs"
if "%~2"=="" (
    set "STRATEGY=theirs"
) else (
    set "STRATEGY=%~2"
)

REM Jeśli nie podano remote, domyślnie "origin"
if "%~3"=="" (
    set "REMOTE=origin"
) else (
    set "REMOTE=%~3"
)

REM Walidacja strategii: musi być "theirs" lub "ours"
if /I not "%STRATEGY%"=="theirs" if /I not "%STRATEGY%"=="ours" (
    echo.
    echo Błąd: Niepoprawna strategia: "%STRATEGY%". Użyj "theirs" lub "ours".
    goto :EOF
)

REM Ustawiamy nazwę głównej gałęzi, względem której scalamy
set "TARGET_BRANCH=main"

REM ----------------------------------------
REM 2. Sprawdzenie, czy aktualny katalog jest repozytorium Git
REM ----------------------------------------
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo.
    echo Błąd: To nie jest repozytorium Git. Upewnij się, że jesteś w katalogu projektu.
    goto :EOF
)

REM ----------------------------------------
REM 3. Fetch z zdalnego
REM ----------------------------------------
echo.
echo ===== Pobieranie najnowszych zmian z "%REMOTE%" =====
git fetch %REMOTE%
if errorlevel 1 (
    echo Błąd: Nie można było pobrać zdalnych zmian z "%REMOTE%".
    goto :EOF
)

REM ----------------------------------------
REM 4. Przełączenie na docelową gałąź
REM ----------------------------------------
echo.
echo ===== Checkout gałęzi "%BRANCH_NAME%" =====
git checkout %BRANCH_NAME%
if errorlevel 1 (
    echo Błąd: Nie można było przełączyć się na gałąź "%BRANCH_NAME%".
    goto :EOF
)

REM ----------------------------------------
REM 5. Merge z główną gałęzią z wybraną strategią
REM ----------------------------------------
echo.
echo ===== Scalanie "%REMOTE%/%TARGET_BRANCH%" do "%BRANCH_NAME%" z opcją -X %STRATEGY% =====
git merge %REMOTE%/%TARGET_BRANCH% -X %STRATEGY% --no-edit
if errorlevel 1 (
    echo.
    echo Uwaga: Merge zgłosił konflikt lub inny błąd. Próbuję dodać pliki i zrobić commit ręcznie...
    git add -A
    git commit -m "Auto-resolved conflicts (%STRATEGY%) against %TARGET_BRANCH%"
    if errorlevel 1 (
        echo Błąd: Nie udało się wykonać commit-a po rozwiązaniu konfliktów.
        goto :EOF
    ) else (
        echo Konflikty rozwiązane i zatwierdzone commit-em.
    )
) else (
    echo Merge zakończony bez konfliktów.
)

REM ----------------------------------------
REM 6. Push na zdalne
REM ----------------------------------------
echo.
echo ===== Wypychanie gałęzi "%BRANCH_NAME%" do "%REMOTE%" =====
git push %REMOTE% %BRANCH_NAME%
if errorlevel 1 (
    echo Błąd: Nie udało się wypchnąć gałęzi "%BRANCH_NAME%" do "%REMOTE%".
    goto :EOF
)

echo.
echo ===== Gotowe! Konflikty zostały automatycznie rozwiązane (strategia: %STRATEGY%) i wypchnięte. =====
endlocal
