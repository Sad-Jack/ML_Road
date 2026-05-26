---
id: pt01
order: 1
num: "01"
title: "01. PyTorch: старт и полезные ссылки"
short: "PyTorch: старт и ссылки"
---
# 01. PyTorch: старт и полезные ссылки

## Зачем это нужно

`PyTorch` нужен там, где начинается deep learning: нейронные сети, tensors, autograd, обучение на GPU, кастомные архитектуры и исследовательский код.

## Что важно понять в этом модуле

- чем tensor отличается от `ndarray`;
- как работает `autograd`;
- как устроен цикл обучения: forward, loss, backward, optimizer step;
- зачем нужны `Dataset` и `DataLoader`.

## Что смотреть в первую очередь

- [PyTorch Get Started](https://pytorch.org/get-started/locally/)
- [PyTorch Tutorials](https://docs.pytorch.org/tutorials/index.html)
- [Learn the Basics](https://docs.pytorch.org/tutorials/beginner/basics/intro)
- [Quickstart Tutorial](https://docs.pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html)

## Как проходить

Сначала закрой tensors и autograd, потом собери маленькую сеть и руками пройди полный train loop. После этого переходи к `torch.nn`, `DataLoader` и GPU.

## Краткий итог

`PyTorch` лучше учить не как набор API, а как способ думать про обучение нейросетей через tensors, вычислительный граф и цикл оптимизации.
