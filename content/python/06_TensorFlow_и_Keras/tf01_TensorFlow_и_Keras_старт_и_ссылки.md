---
id: tf01
order: 1
num: "01"
title: "01. TensorFlow и Keras: старт и полезные ссылки"
short: "TensorFlow и Keras: старт и ссылки"
---
# 01. TensorFlow и Keras: старт и полезные ссылки

## Зачем это нужно

`TensorFlow` и `Keras` часто встречаются в продовых пайплайнах, обучении и деплое нейросетей. `Keras` даёт более высокий уровень абстракции, `TensorFlow` — экосистему и инфраструктурный слой.

## Что важно понять в этом модуле

- как быстро собрать и обучить сеть в `Keras`;
- как устроены tensors, layers, model, compile, fit;
- где заканчивается удобный high-level API и начинается более низкий уровень `TensorFlow`;
- как экспортировать и переиспользовать модель.

## Что смотреть в первую очередь

- [TensorFlow Quickstart for Beginners](https://www.tensorflow.org/tutorials/quickstart/beginner)
- [TensorFlow Learn](https://www.tensorflow.org/learn)
- [Keras Getting Started](https://keras.io/getting_started/)
- [Keras Examples](https://keras.io/examples/)

## Как проходить

Сначала собери минимальную модель в `Keras`, затем разбери `compile / fit / evaluate / predict`. После этого уже имеет смысл идти в callbacks, functional API и сохранение моделей.

## Краткий итог

Этот стек полезен, когда нужен более инфраструктурный deep learning-подход. Даже если основным фреймворком позже станет `PyTorch`, знать `TensorFlow/Keras` всё равно полезно.
