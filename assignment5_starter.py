# -*- coding: utf-8 -*-
"""assignment5_starter.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-1XzriPM2E9rtw-QwEHEYCqLeWJKWGzp
"""

import numpy as np
import pandas as pd

from collections import Counter
# Define the KNN class
class KNN:
    def __init__(self, k=3, distance_metric='euclidean'):
        self.k = k
        self.distance_metric = distance_metric
        self.X_train = None
        self.y_train = None

    def fit(self, X, y):
        # TODO: Implement the fit method
        self.X_train = X
        self.y_train = y


    def predict(self, X, return_probabilities=False, weighted=False):
        # TODO: Implement the predict method
      probs = []

    # Get unique classes from the training labels
      classes = np.unique(self.y_train)

      for x in X:
        distances = self.compute_distance(self.X_train, x)
        nearest_neighbors = np.argsort(distances)[:self.k]
        neighbor_labels = self.y_train[nearest_neighbors]
        neighbor_labels = neighbor_labels.astype(int)

        if return_probabilities:
            # Calculate the probability distribution of the neighbors' labels
            class_counts = np.bincount(neighbor_labels, minlength=len(classes))
            probabilities = class_counts / len(neighbor_labels)  # Normalize to get probabilities
            probs.append(probabilities)
        else:
            # Predict the most common label (majority vote)
            predicted_label = np.argmax(np.bincount(neighbor_labels))
            probs.append(predicted_label)

      return np.array(probs)

    def compute_distance(self, X1, X2):
        # TODO: Implement distance computation based on self.distance_metric
        # Hint: Use numpy operations for efficient computation
        if self.distance_metric == 'euclidean':
            X2 = np.array(X2).reshape(1, -1)  # Reshape to a 2D array with one row
            return np.sqrt(np.sum((X1 - X2) ** 2, axis=1))
        elif self.distance_metric == 'manhattan':
            return np.sum(np.abs(X1 - X2), axis=1)

# Define data preprocessing function
def preprocess_data(train_path, test_path):
    train_data = pd.read_csv(train_path)
    test_data = pd.read_csv(test_path)

    # 1. Handle categorical variables using pandas get_dummies
    # 1. Handle Missing Values
    # Impute numerical features with the mean
    numerical_features = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'EstimatedSalary']
    for feature in numerical_features:
        train_data.loc[:, feature] = train_data[feature].fillna(train_data[feature].mean())
        test_data.loc[:, feature] = test_data[feature].fillna(train_data[feature].mean())

        # train_data[feature].fillna(train_data[feature].mean(), inplace=True)
        # test_data[feature].fillna(train_data[feature].mean(), inplace=True)  # Use train mean for test

    # 2. Feature Scaling
    for feature in numerical_features:
        mean = train_data[feature].mean()
        std = train_data[feature].std()
        train_data[feature] = (train_data[feature] - mean) / std
        test_data[feature] = (test_data[feature] - mean) / std

    # 3. Categorical Variable Encoding
    train_data = pd.get_dummies(train_data, columns=['Geography', 'Gender'], drop_first=True)
    test_data = pd.get_dummies(test_data, columns=['Geography', 'Gender'], drop_first=True)

    # Align columns between train and test (handle missing dummy columns)
    train_columns = set(train_data.columns)
    test_columns = set(test_data.columns)
    missing_cols_train = list(test_columns - train_columns)
    missing_cols_test = list(train_columns - test_columns)

    for col in missing_cols_train:
        train_data[col] = 0

    for col in missing_cols_test:
        test_data[col] = 0

    test_data = test_data[train_data.columns]  # Ensure test has same columns as train

    # 4. Feature Selection/Engineering (Example: Correlation-based)
    # You can add more sophisticated feature selection/engineering techniques here
    numerical_features = train_data.select_dtypes(include=np.number).columns.tolist()
    correlations = train_data[numerical_features].corr()['Exited'].abs().sort_values(ascending=False)

    selected_features = correlations[correlations > 0.1].index.tolist()  # Select features with correlation > 0.1
    selected_features.remove('Exited')  # Remove target variable

    X_train = train_data[selected_features].values
    y_train = train_data['Exited'].values
    X_test = test_data[selected_features].values

    return X_train, y_train, X_test

def cross_validate(X, y, knn, n_splits=5):
    # TODO: Implement cross-validation
    # Compute ROC AUC scores

  fold_size = len(X) // n_splits
  scores = []

  for i in range(n_splits):
      val_indices = range(i * fold_size, (i + 1) * fold_size)
      train_indices = list(set(range(len(X))) - set(val_indices))

      X_train, X_val = X[train_indices], X[val_indices]
      y_train, y_val = y[train_indices], y[val_indices]

      knn.fit(X_train, y_train)
      predictions = knn.predict(X_val)

      # Calculate ROC AUC score
      tp = np.sum((predictions == 1) & (y_val == 1))
      fp = np.sum((predictions == 1) & (y_val == 0))
      tn = np.sum((predictions == 0) & (y_val == 0))
      fn = np.sum((predictions == 0) & (y_val == 1))

      if tp + fp > 0 and tp + fn > 0:
          sensitivity = tp / (tp + fn)
          specificity = tn / (tn + fp)
          auc = (sensitivity + specificity) / 2
          scores.append(auc)


  return scores

# Load and preprocess data
X, y, X_test = preprocess_data('/content/train copy.csv.zip', '/content/test copy.csv')

# Create and evaluate model
knn = KNN(k=5, distance_metric='euclidean')

# Perform cross-validation
cv_scores = cross_validate(X, y, knn)

print("Cross-validation scores:", cv_scores)



# TODO: hyperparamters tuning
best_k = 3
best_auc = 0
for k in range(1, 21):
  knn = KNN(k=k)
  cv_scores = cross_validate(X, y, knn)
  mean_auc = np.mean(cv_scores)
  if mean_auc > best_auc:
    best_auc = mean_auc
    best_k = k
print(f"Best k: {best_k}, Best AUC: {best_auc}")
print("Best Cross-Validation AUC:", best_auc)


# TODO: Train on full dataset with optimal hyperparameters and make predictions on test set
knn = KNN(k=best_k)
knn.fit(X, y)
test_predictions = knn.predict(X_test)

# Save test predictions
pd.DataFrame({'id': pd.read_csv('/content/test copy.csv')['id'], 'Exited': test_predictions}).to_csv('submissions.csv', index=False)