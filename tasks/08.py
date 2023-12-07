import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

draft_df = pd.read_csv('../nhl_draft.csv', encoding='unicode_escape')
# Select the desired columns for the subset
selected_columns = ['NATIONALITY_CAT', 'POSITION', 'AGE', 'DRAFT_ROUND', 'HEIGHT_CAT',
                    'WEIGHT_CAT', 'SHOOTS', 'AMATEUR_LEAGUE_CAT', 'LAST_JUNIOR_YEAR_PPG_CAT',
                    'AVERAGE_JUNIOR_PPG_CAT']

# Create the subset DataFrame
rf_subset = draft_df[selected_columns]

label_encoder = LabelEncoder()

# Encode the categorical columns
rf_subset['NATIONALITY_CAT'] = label_encoder.fit_transform(rf_subset['NATIONALITY_CAT'])
rf_subset['POSITION'] = label_encoder.fit_transform(rf_subset['POSITION'])
rf_subset['HEIGHT_CAT'] = label_encoder.fit_transform(rf_subset['HEIGHT_CAT'])
rf_subset['WEIGHT_CAT'] = label_encoder.fit_transform(rf_subset['WEIGHT_CAT'])
rf_subset['SHOOTS'] = label_encoder.fit_transform(rf_subset['SHOOTS'])
rf_subset['AMATEUR_LEAGUE_CAT'] = label_encoder.fit_transform(rf_subset['AMATEUR_LEAGUE_CAT'])
rf_subset['LAST_JUNIOR_YEAR_PPG_CAT'] = label_encoder.fit_transform(rf_subset['LAST_JUNIOR_YEAR_PPG_CAT'])
rf_subset['AVERAGE_JUNIOR_PPG_CAT'] = label_encoder.fit_transform(rf_subset['AVERAGE_JUNIOR_PPG_CAT'])

rf_subset['NATIONALITY_CAT'] = rf_subset['NATIONALITY_CAT'].fillna(123)
rf_subset['POSITION'] = rf_subset['POSITION'].fillna(123)
rf_subset['HEIGHT_CAT'] = rf_subset['HEIGHT_CAT'].fillna(123)
rf_subset['WEIGHT_CAT'] = rf_subset['WEIGHT_CAT'].fillna(123)
rf_subset['SHOOTS'] = rf_subset['SHOOTS'].fillna(123)
rf_subset['AMATEUR_LEAGUE_CAT'] = rf_subset['AMATEUR_LEAGUE_CAT'].fillna(123)
rf_subset['LAST_JUNIOR_YEAR_PPG_CAT'] = rf_subset['LAST_JUNIOR_YEAR_PPG_CAT'].fillna(123)
rf_subset['AVERAGE_JUNIOR_PPG_CAT'] = rf_subset['AVERAGE_JUNIOR_PPG_CAT'].fillna(123)

rf_subset['AGE'] = rf_subset['AGE'].fillna(123)
rf_subset['DRAFT_ROUND'] = rf_subset['DRAFT_ROUND'].fillna(123)


# Display the first few rows of the subset
print(rf_subset.head())

# Split the data into training and testing sets
train, test = train_test_split(rf_subset, test_size=0.2, random_state=420)
X_train = train.drop('DRAFT_ROUND', axis=1)
y_train = train['DRAFT_ROUND']
X_test = test.drop('DRAFT_ROUND', axis=1)
y_test = test['DRAFT_ROUND']

# Initialize the Random Forest classifier.
rf_clf = RandomForestClassifier(random_state=42)

# Train the classifier on the training data.
rf_clf.fit(X_train, y_train)

# Make predictions on the test data.
rf_y_pred = rf_clf.predict(X_test)

# Evaluate the Random Forest model
rf_accuracy = accuracy_score(test["DRAFT_ROUND"], rf_y_pred)
print("Random Forest Accuracy:", rf_accuracy)
rf_report = classification_report(test["DRAFT_ROUND"], rf_y_pred,  zero_division=1)
print(rf_report)
rf_confmatrix = confusion_matrix(test["DRAFT_ROUND"], rf_y_pred)
class_labels = sorted(set(test["DRAFT_ROUND"]))

# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(rf_confmatrix, annot=True, fmt="d", cmap="Blues", xticklabels=class_labels, yticklabels=class_labels)
plt.title("Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.show()
print(rf_confmatrix)
