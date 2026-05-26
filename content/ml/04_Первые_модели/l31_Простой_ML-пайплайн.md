---
id: l31
order: 31
num: "31"
title: "31. Простой ML-пайплайн"
short: "Простой ML-пайплайн"
---
# 30. Простой ML-пайплайн

## Зачем это нужно

В реальном проекте модель — это маленький кусочек большой цепочки: загрузить данные, обработать пропуски, закодировать категории, масштабировать числа, обучить, предсказать, оценить. Если делать всё руками по шагам, очень легко допустить утечку (train → val) или забыть применить трансформацию на test. Pipeline в sklearn собирает все шаги в один объект, который ведёт себя как обычная модель.

## Простая интуиция

Pipeline — это как сборочный конвейер. Заготовка (сырые признаки) едет по ленте: сначала StandardScaler что-то с ней делает, потом OneHotEncoder, потом LogisticRegression обучается. На выходе — готовое предсказание. И главное — точно тот же конвейер автоматически прокатит test через те же преобразования.

## Что это такое

`Pipeline` в sklearn — последовательность шагов вида `(name, transformer_or_model)`. У всех шагов кроме последнего должны быть методы `.fit()` и `.transform()`. Последний шаг — обычно модель с `.fit()` и `.predict()`.

`ColumnTransformer` — соседний инструмент: разные преобразования для разных колонок (числовые → scaler, категориальные → one-hot).

## Как это работает

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

df = pd.read_csv("clients.csv")
y = df["bought"]
X = df.drop(columns=["bought", "client_id"])

num_cols = ["age", "orders_count"]
cat_cols = ["city"]

# Преобразования для числовых колонок
num_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler",  StandardScaler()),
])

# Преобразования для категориальных колонок
cat_pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("ohe",     OneHotEncoder(handle_unknown="ignore")),
])

preprocess = ColumnTransformer([
    ("num", num_pipe, num_cols),
    ("cat", cat_pipe, cat_cols),
])

pipe = Pipeline([
    ("prep",  preprocess),
    ("model", LogisticRegression(max_iter=1000)),
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pipe.fit(X_train, y_train)
print(accuracy_score(y_test, pipe.predict(X_test)))
```

Главное: `pipe.fit(X_train, ...)` сам обучит scaler/encoder **только на train**, а `pipe.predict(X_test)` применит уже готовые преобразования к test. Утечки не будет.

## Простой пример

Без pipeline лёгкая утечка:

```python
# ПЛОХО: scaler выучил статистики по всему датасету, включая test
scaler = StandardScaler().fit(X)  # ← test тоже сюда попал
X_train_s = scaler.transform(X_train)
X_test_s  = scaler.transform(X_test)
```

С pipeline такая ошибка невозможна — он умеет «учиться только на той части, которую ему дали в fit».

## Практика

1. Что такое `Pipeline` в sklearn и какую главную проблему он решает по сравнению с ручным вызовом шагов по очереди?
2. Чем `ColumnTransformer` отличается от `Pipeline`? Когда нужны оба вместе?
3. У вас числовые колонки `age`, `salary` и категориальная `city`. Опишите словами, какие шаги войдут в пайплайн перед `LogisticRegression`.
4. Как Pipeline автоматически защищает от утечки данных при каждом fold `cross_val_score`?
5. Вы обучаете `StandardScaler` на всём X (включая test), а потом делаете split. Что именно нарушается, и как Pipeline это исправляет?

## Краткий итог

- Pipeline собирает все шаги (предобработка + модель) в один объект.
- `ColumnTransformer` применяет разные шаги к разным колонкам.
- Защищает от утечек: scaler/encoder учится только на train.
- Идеально дружит с `cross_val_score` и `GridSearchCV`.
- Один сохранённый pipeline = вся логика инференса в проде.

## Ключевые термины урока

- **Pipeline** — гарантирует правило «fit только на train»: при cross-validation scaler обучается только на fold-train, не видя fold-val. Без Pipeline — scaler.fit(X_all) перед split — data leakage.
- **ColumnTransformer** — вместо двух отдельных трансформаций (числовые → scaler, категориальные → OHE) создаёт один шаг; оба шага учатся и применяются синхронно. Без него — ручное разделение колонок = ошибки.
- **fit_transform** — вызывается только на train: вычисляет статистики и сразу применяет. Применять к test — data leakage. В Pipeline вызывается автоматически только для промежуточных шагов на train.
- **Сохранение pipeline** — один .pkl файл содержит scaler + encoder + модель с параметрами; при inference не нужно отдельно хранить и воссоздавать preprocessing. Pipeline.predict() автоматически прогоняет через все шаги.