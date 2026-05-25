---
id: l22
order: 22
num: "22"
title: "22. Overfitting и Underfitting"
short: "Overfitting и Underfitting"
---
# 22. Overfitting и Underfitting

## Зачем это нужно

Модель может плохо работать по двум противоположным причинам: слишком простая и не улавливает закономерности — или слишком сложная и зубрит обучающие данные. Это нужно различать, чтобы понимать, в какую сторону её улучшать.

## Простая интуиция

- **Underfitting** — студент, который не открывал учебник. Плохо даже на знакомых задачах.
- **Overfitting** — студент, который зазубрил конкретный вариант. На знакомых вопросах — пятёрка, на похожих новых — двойка.

Идеал — где-то посередине: понял суть, поэтому хорошо отвечает и на знакомые, и на новые задачи.

## Что это такое

**Underfitting**: модель слишком проста и не нашла закономерностей даже в train.
Признак: `train_score` плохой и `val_score` тоже плохой, они близки друг к другу.

**Overfitting**: модель слишком подстроилась под train, запомнила шум вместо паттернов.
Признак: `train_score` отличный, `val_score` заметно хуже (большой gap).

**Good fit**: train и val близки, оба приемлемые.

## Как это работает

| Ситуация | Train score | Val score | Диагноз |
|---|---|---|---|
| Вариант 1 | 0.62 | 0.60 | underfitting |
| Вариант 2 | 0.99 | 0.74 | overfitting |
| Вариант 3 | 0.90 | 0.87 | good fit |

Главное правило — смотреть **на разницу** между train и val, а не только на абсолютные значения.

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# overfit: глубокое дерево без ограничений
deep = DecisionTreeClassifier(random_state=42)
deep.fit(X_train, y_train)
print("train:", accuracy_score(y_train, deep.predict(X_train)))   # ~1.00
print("val:  ", accuracy_score(y_val,   deep.predict(X_val)))     # ~0.70

# borderline: ограничиваем глубину
shallow = DecisionTreeClassifier(max_depth=5, random_state=42)
shallow.fit(X_train, y_train)
print("train:", accuracy_score(y_train, shallow.predict(X_train)))  # ~0.88
print("val:  ", accuracy_score(y_val,   shallow.predict(X_val)))    # ~0.84
```

## Простой пример

Дерево решений без ограничений: train accuracy = 1.0, val accuracy = 0.70. Модель просто запомнила все примеры из train. Решения:
- ограничить `max_depth`;
- увеличить `min_samples_leaf`;
- собрать больше данных;
- использовать ансамбль (Random Forest усредняет шум).

## Практика

1. Как по значениям train_score и val_score отличить overfitting от underfitting? Какой именно показатель диагностирует каждое из двух явлений?
2. `DecisionTreeClassifier` без ограничений: train accuracy = 1.0, val accuracy = 0.68. Что произошло и какие два параметра можно изменить, чтобы это исправить?
3. Ваша модель: train = 0.62, val = 0.60. Назовите два способа улучшить ситуацию.
4. Из урока 16 мы знаем, зачем нужен val. Почему без val-выборки невозможно диагностировать overfitting?
5. Вы обучаете модель и смотрите только на метрику на train-выборке: accuracy = 0.95. Почему это может быть обманчиво и что нужно сделать, чтобы получить честную картину?

## Краткий итог

- Underfitting: и train, и val плохие → модель слишком слабая.
- Overfitting: train отличный, val плохой → модель зазубрила.
- Good fit: train и val близки и оба приемлемые.
- Главный диагностический сигнал — разрыв между train и val.
- Лекарства: для under — усложнить, для over — упростить / больше данных / регуляризация.

## Ключевые термины урока

- **Underfitting** — модель слишком проста: плохо работает и на train, и на val.
- **Overfitting** — модель слишком сложна: отлично на train, плохо на val.
- **Good fit** — train и val метрики близки и оба приемлемы.
- **Разрыв train/val** — главный диагностический сигнал переобучения.