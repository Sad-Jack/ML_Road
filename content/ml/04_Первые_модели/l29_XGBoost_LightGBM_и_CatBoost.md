---
id: l29
order: 29
num: "29"
title: "29. XGBoost, LightGBM и CatBoost"
short: "XGBoost, LightGBM и CatBoost"
---
# 29. XGBoost, LightGBM и CatBoost

## Зачем это нужно

`GradientBoostingClassifier` из sklearn — учебный вариант. В реальных проектах используют три библиотеки: **XGBoost**, **LightGBM**, **CatBoost**. Они быстрее, имеют встроенный early stopping, обработку пропусков и категорий, и почти всегда выигрывают на табличных данных в продакшене и на Kaggle.

## Простая интуиция

Все три — это «прокачанный» Gradient Boosting (урок 28). Различия — в инженерии:
- **XGBoost** — первый, кто сделал бустинг быстрым и регуляризованным; промышленный стандарт.
- **LightGBM** — ещё быстрее, особенно на больших данных и с большим числом признаков; растит деревья «leaf-wise».
- **CatBoost** — нативно работает с категориальными признаками (без one-hot), очень устойчив к настройкам по умолчанию.

## Что это такое

Все три — реализации gradient boosting с собственной оптимизацией:

| | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| Скорость | быстрая | очень быстрая | средняя |
| Большие данные | хорошо | отлично | хорошо |
| Категории | one-hot вручную | через `categorical_feature` | нативно, лучшая |
| Пропуски (NaN) | да | да | да |
| Дефолты | требуют настройки | требуют настройки | хорошие из коробки |
| GPU | да | да | да |
| API | sklearn-like | sklearn-like | sklearn-like |

## Как это работает

```python
# XGBoost
from xgboost import XGBClassifier

xgb = XGBClassifier(
    n_estimators=2000,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    early_stopping_rounds=50,
    random_state=42,
)
xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

# LightGBM
from lightgbm import LGBMClassifier

lgbm = LGBMClassifier(
    n_estimators=2000, learning_rate=0.05, num_leaves=63,
    subsample=0.8, colsample_bytree=0.8, random_state=42,
)
lgbm.fit(X_train, y_train,
         eval_set=[(X_val, y_val)],
         callbacks=[__import__("lightgbm").early_stopping(50)])

# CatBoost — умеет принимать категории как есть
from catboost import CatBoostClassifier

cat = CatBoostClassifier(
    iterations=2000, learning_rate=0.05, depth=6,
    cat_features=["city", "device"],   # имена категориальных колонок
    early_stopping_rounds=50, verbose=False, random_seed=42,
)
cat.fit(X_train, y_train, eval_set=(X_val, y_val))
```

Ключевые гиперпараметры везде похожи: `n_estimators` / `iterations`, `learning_rate`, `max_depth` / `num_leaves` / `depth`, регуляризация (`reg_alpha`, `reg_lambda`, `l2_leaf_reg`), стохастичность (`subsample`, `colsample_bytree`).

## Простой пример

Когда что брать на старте:
- **много категориальных признаков, мало времени на настройку → CatBoost.** Часто работает «из коробки» лучше, чем тюненный XGBoost.
- **очень большой датасет (миллионы строк) → LightGBM.** Самый быстрый и легче на памяти.
- **классика, есть готовый пайплайн с one-hot → XGBoost.** Зрелая экосистема, много документации.

Если данных мало (< 10к строк) — Random Forest или CatBoost обычно ничем не хуже и стабильнее.

## Практика

1. В чём главное преимущество CatBoost перед XGBoost при работе с категориальными признаками?
2. Зачем нужны `early_stopping_rounds` и `eval_set` при обучении XGBoost или LightGBM?
3. Вы работаете с датасетом из 5 миллионов строк и 300 признаков. Какую из трёх библиотек вы бы выбрали в первую очередь и почему?
4. Как `early_stopping_rounds` решает эту проблему автоматически?
5. У вас данные с 20 категориальными колонками. Вы хотите попробовать XGBoost. Что нужно сделать с категориальными признаками перед обучением, и как CatBoost упрощает этот шаг?

## Краткий итог

- Выбор конкретного бустинга обычно не принципиален: важнее правильный early stopping и подбор параметров.
- Все наследуют идею gradient boosting (урок 28), но различаются скоростью и удобством.
- CatBoost — лучший дефолт для данных с категориями.
- LightGBM — самый быстрый на больших данных.
- XGBoost — зрелая классика и большая экосистема.
- Обязательно используй `early_stopping_rounds` и отдельный `eval_set`.

## Ключевые термины урока

- **XGBoost** — промышленная реализация бустинга с регуляризацией и параллельным обучением.
- **LightGBM** — быстрая реализация бустинга, особенно эффективная на больших датасетах.
- **CatBoost** — бустинг с нативной поддержкой категориальных признаков без ручного кодирования.
- **Промышленный бустинг** — текущий стандарт качества для табличных данных.