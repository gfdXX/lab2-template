# РСОИ, ЛР2: микросервисы сервиса аренды автомобилей

![Python](https://img.shields.io/badge/Python-FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-SQLAlchemy-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)

Лабораторная работа №2 по курсу «Распределённые системы обработки информации», МГТУ им. Н.Э. Баумана (осень 2025).

> **Код решения — в ветке [`test`](https://github.com/gfdXX/lab2-template/tree/test).**
> В `master` лежит исходный шаблон курса, условие задания — в [ASSIGNMENT.md](ASSIGNMENT.md).

## Что сделано

Система аренды автомобилей из четырёх сервисов на **FastAPI + SQLAlchemy**:

| Сервис | Порт | Ответственность |
|---|---|---|
| Gateway | 8080 | единая точка входа: оркестрирует запросы к остальным сервисам, сами сервисы друг к другу не ходят |
| Cars | 8070 | каталог автомобилей и их доступность |
| Rental | 8060 | аренды пользователей |
| Payment | 8050 | оплаты |

Через Gateway доступны список автомобилей, оформление аренды (бронирование машины + оплата), просмотр, завершение и отмена аренды — `/api/v1/cars`, `/api/v1/rental`, `/api/v1/rental/{uid}/finish`.
У каждого сервиса своя логическая база в общем PostgreSQL, endpoint `GET /manage/health` и unit-тесты на `pytest`. Всё поднимается через `docker-compose`, API проверяется тестами Postman в GitHub Actions.

![Схема сервисов](https://raw.githubusercontent.com/gfdXX/lab2-template/test/images/services.png)

## Запуск

```bash
git clone -b test https://github.com/gfdXX/lab2-template.git
cd lab2-template
docker compose up --build        # Gateway на http://localhost:8080
```

## Продолжение

[ЛР3: отказоустойчивость](https://github.com/gfdXX/lab3-template) · [ЛР4: деплой в Kubernetes](https://github.com/gfdXX/lab4-template) · [ЛР5: OAuth2, курсовая](https://github.com/gfdXX/lab5-template)

## Автор

Салженикин Даниил, МГТУ им. Н.Э. Баумана.
