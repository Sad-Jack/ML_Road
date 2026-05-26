---
id: hf01
order: 1
num: "01"
title: "01. Hugging Face и MLflow: старт и полезные ссылки"
short: "Hugging Face и MLflow: старт и ссылки"
---
# 01. Hugging Face и MLflow: старт и полезные ссылки

## Зачем это нужно

`Hugging Face` нужен для современного NLP и LLM-стека: модели, токенизаторы, готовые пайплайны, обучение и inference. `MLflow` нужен для трекинга экспериментов, версионирования моделей и воспроизводимости.

## Что важно понять в этом модуле

- как устроен базовый workflow в `transformers`;
- откуда брать модели и как читать model cards;
- как логировать параметры, метрики и артефакты в `MLflow`;
- как не терять результаты экспериментов и версии моделей.

## Что смотреть в первую очередь

- [Transformers Documentation](https://huggingface.co/docs/transformers/en/index)
- [Hugging Face Course: Chapter 1](https://huggingface.co/course/chapter1/1)
- [Hugging Face Learn](https://huggingface.co/learn)
- [MLflow Documentation](https://www.mlflow.org/docs/latest/)
- [MLflow Getting Started for ML](https://www.mlflow.org/docs/latest/ml/getting-started/)
- [MLflow Quickstart](https://mlflow.org/docs/latest/ml/getting-started/quickstart/)

## Как проходить

Сначала разберись с самым простым inference-сценарием в `Hugging Face`, потом посмотри fine-tuning и pipelines. Параллельно стоит сразу приучать себя логировать эксперименты через `MLflow`, даже на маленьких задачах.

## Краткий итог

Это уже не база классического ML, а слой современного production/research-стека. Но чем раньше начнёшь работать с моделями и экспериментами системно, тем легче будет расти дальше.
