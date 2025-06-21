import pandas as pd

# Import data
df = pd.read_csv("ml_pipeline/personality_dataset.csv")

# first lines
print(" Πρώτες γραμμές:")
print(df.head())

# Info for data type
print("\n Πληροφορίες:")
print(df.info())

# Drop rows with missing values
print("\n Κενές τιμές:")
print(df.isnull().sum())

df = df.dropna()

# Convert "Yes/No" to 1/0
df["Stage_fear"] = df["Stage_fear"].map({"Yes": 1, "No": 0})
df["Drained_after_socializing"] = df["Drained_after_socializing"].map({"Yes": 1, "No": 0})

# Convert "Personality" to 0 (Introvert) and 1 (Extrovert)
df["Personality"] = df["Personality"].map({"Introvert": 0, "Extrovert": 1})

print("\n Μοναδικές τιμές στο Personality:")
print(df["Personality"].value_counts())

print("\n Τύποι δεδομένων μετά την κωδικοποίηση:")
print(df.dtypes)

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Split features (X) and target (y)
X = df.drop("Personality", axis=1)
y = df["Personality"]

# Split to training and testing sets (80% / 20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Prediction of test set
y_pred = model.predict(X_test)

# Evaluate model
print("\n Ακρίβεια (accuracy):", accuracy_score(y_test, y_pred))
print("\n Confusion matrix:\n", confusion_matrix(y_test, y_pred))
print("\n Classification report:\n", classification_report(y_test, y_pred))

import joblib
joblib.dump(model, "personality_model.pkl")
