import polars as pl
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# pl.read_parquet("logs/*.parquet").write_parquet("data.parquet")

df = pl.read_parquet("data.parquet").to_pandas()

features = [
    f"{type_}_{i}"
    for type_ in ['played_cards', 'hand', 'trick', 'valid_cards']
    for i in range(1, 53)
]

targets = [
    f"card_{i}"
    for i in range(1, 53)
]

X = df[features]
y_onehot = df[targets]

y = y_onehot.to_numpy().argmax(axis=1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

joblib.dump(model, "random_forest.pkl")