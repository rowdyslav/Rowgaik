# Rowgaik
Webview flet app for Study Miigaik

## Android release

GitHub Actions собирает APK при отправке тега в формате `vX.Y.Z` и прикрепляет его к GitHub Release.

```bash
git add .github/workflows/android-release.yml assets/icon.png main.py pyproject.toml README.md
git commit -m "Prepare Android release"
git push origin main
git tag v1.0.2
git push origin v1.0.2
```

После этого APK появится во вкладке **Releases** репозитория. Для проверки сборки без публикации релиза workflow можно запустить вручную во вкладке **Actions**.
