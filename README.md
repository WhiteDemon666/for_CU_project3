# Панель управления прогнозом погоды

Это веб-приложение, созданное с использованием Dash, которое позволяет пользователям вводить названия городов и получать прогнозы погоды. Приложение визуализирует данные о погоде на графиках и картах, соединяя города линиями для лучшего географического представления.

## Ответы на вопросы
1. Линейные графики хорошо подходят для отображения изменений погодных параметров (таких как температура, влажность и скорость ветра) с течением времени. Линейные графики позволяют легко увидеть закономерности в данных, что позволяет делать правильные выводы на основе этих данных.
2. Интерактивные графики позволяют пользователю выбирать то, что именно он хочет видеть на графике и в каком временном промежутике. Это позволяет ему удобно сравнивать различные погодные параметры(условия)

## Особенности

- Ввод нескольких городов для получения данных о погоде.
- Визуализация температуры, влажности, скорости ветра и осадков для выбранных городов.
- Отображение данных о погоде за последние 2-5 дней.
- Интерактивная карта, показывающая города с линиями, соединяющими их.

## Требования

Для запуска этого приложения вам понадобятся следующие компоненты:

- Python 3.x
- Ключ API от сервиса погоды AccuWeather
- Необходимые пакеты Python:
  - Dash
  - Plotly
  - Pandas
  - Requests
  - Dash Bootstrap Components
