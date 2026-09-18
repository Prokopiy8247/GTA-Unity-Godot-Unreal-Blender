# Как запустить Port Meridian

Одиночная песочница на Unreal Engine 5.8.2. Реализованные системы и ограничения: [FEATURE_MATRIX.md](FEATURE_MATRIX.md). Интернет и регистрация внутри игры не нужны.

## Windows — готовая игра без Unreal

1. Откройте [релиз](https://github.com/Prokopiy8247/GTA-Unity-Godot-Unreal-Blender/releases/tag/port-meridian-v0.1.0).
2. В **Assets** скачайте **PortMeridian-Windows-x64.zip**. Пункты «Source code» содержат исходники, а не готовую игру.
3. Нажмите на ZIP правой кнопкой → **Извлечь всё**.
4. В распакованной папке откройте **Играть.cmd** или **Unreal_GTA.exe**. Не запускайте игру прямо из архива.
5. При ошибке MSVCP/VCRUNTIME запустите **Engine/Extras/Redist/en-us/vc_redist.x64.exe** из архива и повторите запуск.

Нужны Windows 10/11 x64 и видеокарта с DirectX 12 / Shader Model 6. Ориентир для комфортной работы: 16 ГБ ОЗУ и дискретная видеокарта с 6–8 ГБ видеопамяти; это рекомендация, а не измеренная гарантия. В F1 можно снизить качество. Формат сборки — Windows x64 Shipping.

У приложения нет платного сертификата издателя. При предупреждении Windows проверьте источник загрузки и SHA-256 из релиза. Не отключайте защиту компьютера глобально.

## macOS — автоматическая сборка из исходников

**Готовой проверенной .app-версии в этом релизе нет.** После установки инструментов один файл автоматически соберёт и откроет игру.

1. Этот сценарий рассчитан на **Apple Silicon M2 или новее**: проект использует Nanite и Virtual Shadow Maps. Желательно 32 ГБ ОЗУ и достаточно места для Unreal и сборки. Intel и M1 не проверены.
2. Установите [Epic Games Launcher](https://www.unrealengine.com/download), затем **Unreal Engine 5.8.2**.
3. Установите полный **Xcode**, запустите его и завершите первоначальную настройку. Epic рекомендует для UE 5.8 Xcode **26.1.1**, минимум — 26.0; **26.4 несовместим**. ОС должна соответствовать требованиям и UE, и Xcode: [Epic](https://dev.epicgames.com/documentation/en-us/unreal-engine/macos-development-requirements-for-unreal-engine), [Apple](https://developer.apple.com/xcode/system-requirements).
4. На [странице репозитория](https://github.com/Prokopiy8247/GTA-Unity-Godot-Unreal-Blender) выберите **Code → Download ZIP**, распакуйте и откройте папку **Unreal Engine 5 GTA**.
5. Дважды нажмите **Launch_PortMeridian.command**. Оставьте Terminal открытым. Первая компиляция и подготовка шейдеров могут занять длительное время.
6. В следующий раз запускайте тот же файл: он откроет уже собранную игру из **Packaged/Mac**.

Если macOS блокирует скрипт, разрешите конкретный файл через контекстное меню «Открыть» или «Системные настройки → Конфиденциальность и безопасность». Не отключайте Gatekeeper целиком.

Если файл открылся как текст или не имеет права исполнения: откройте Terminal, напишите `bash ` с пробелом, перетащите **Launch_PortMeridian.command** в окно и нажмите Return.

Если установлен Xcode, но выбран CommandLineTools, в **Xcode → Settings → Locations → Command Line Tools** выберите полный Xcode и повторите запуск.

Mac-скрипт проверен на синтаксис. Нативная компиляция, графика, управление и производительность на Mac ещё не проверены. Скрипт не заменяет готовую проверенную Mac-игру.

## Управление

| Кнопка | Действие |
| --- | --- |
| WASD / мышь | Движение и камера; управление транспортом |
| Shift / Space | Бег / прыжок; Space в машине — ручной тормоз |
| F / E | Войти в транспорт / магазин, ремонт, безопасный дом |
| ЛКМ / ПКМ / R | Выстрел / прицел / перезарядка |
| 1–9 / колесо | Выбор оружия |
| Tab + колесо | Замедленное переключение снаряжения |
| Q / C / V | Укрытие / приседание / камера от первого лица |
| H / L | Клаксон или сирена / фары |
| Space / Ctrl | Набор высоты / снижение в авиации |
| P | Парашют |
| M | Карта; щелчок ставит точку маршрута |
| F1 / Escape | Меню и настройки |
| F5 / F9 | Сохранить / загрузить |

На Mac удобнее мышь с двумя кнопками. Если F-клавиши меняют громкость и яркость, используйте Fn + F1/F5/F9.

## Открыть проект в редакторе

Карты, модели, материалы и Blueprints уже включены. Blender и Blender MCP для игры и обычной сборки не требуются. Ручной импорт и сборка сцены не нужны.

**Windows:** установите UE 5.8.2 и Visual Studio 2022 с **Game development with C++**, MSVC v143 и Windows SDK. Откройте **Open_Editor.cmd**: он соберёт модуль и откроет проект. Нажмите Play. **Launch_PortMeridian.cmd** создаёт готовую сборку автоматически, если её ещё нет в Packaged/Windows.

**Mac:** установив UE и Xcode, откройте **Open_Editor.command**. Он соберёт C++-модуль и откроет проект. Нативная работа пока не проверена.

Скачивайте весь каталог, включая **Content/__ExternalActors__** — это части открытого мира. Не создавайте новый проект и не переносите отдельные .uasset вручную.

При нестандартном расположении Unreal укажите переменную окружения **UE_ROOT**, содержащую путь к папке **UE_5.8**. Запускатели также проверяют стандартные каталоги и, на Windows, реестр и настройки Epic Games Launcher.

Технические команды из папки проекта:

- Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File Tools/Launch_Windows.ps1 -Mode Build` — собрать; `-Mode Check` — проверить наличие движка.
- Mac: `bash Tools/launch_macos.sh build` — собрать; `bash Tools/launch_macos.sh check` — проверить инструменты.

## Содержимое

Unreal_GTA.uproject, Source, Config и Content — проект. UnrealGTA.blend и SourceAssets — исходные модели и аудио. **GPT-6-Astra_UnrealEngine5_GTA_BlenderMCP_Prompt.md** — сохранённый исходный промпт. [ASTRA_FINAL_REPORT.md](ASTRA_FINAL_REPORT.md) — отчёт и измерения; [QA_RESULTS.md](QA_RESULTS.md) — проверки; [SECURITY_PUBLICATION.md](SECURITY_PUBLICATION.md) — очистка перед публикацией.
