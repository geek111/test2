@echo off
chcp 65001 >nul

echo ===== Twarda aktualizacja repozytorium z GitHub =====

:: Przełącz na main
git checkout main

:: Wycofaj WSZYSTKIE lokalne zmiany (UWAGA: to nadpisuje wszystko!)
git reset --hard

:: Pobierz najnowsze dane z GitHuba
git fetch origin

:: Ściągnij aktualizacje do gałęzi main (fast-forward)
git pull origin main

echo.
echo ✅ Repozytorium zostało NADPISANE najnowszą wersją z GitHuba.
echo.
pause
