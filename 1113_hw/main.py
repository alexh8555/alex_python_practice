import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error

##############CONFIG################
nStd = 2 # timeDiff that are "N * std" away from the mean will be remove
randomNum = 42
testSize = 0.2

####################################


# df = pd.read_excel("1113_hw//Abandonment data test.xlsx")
df = pd.read_excel("1113_hw//Abandonment data.xlsx")
print(f'df Original, shape is {df.shape}')

# 1. Data Preparation (1.5 Points)
# Clean the Dataset: Address any errors and inconsistencies in the data.
df = df.drop(columns=['Customer ID'])
df = df.drop(columns=['Type of transaction'])
df = df.dropna()

df['Arrival Date'] = df['Arrival Date'].astype(str)
df['Arrival Time'] = df['Arrival Time'].astype(str)
df['Arrival DateTime'] = pd.to_datetime(df['Arrival Date'] + ' ' + df['Arrival Time'])
df = df.drop(columns=['Arrival Time'])
df = df.drop(columns=['Arrival Date'])

df['Status Date'] = df['Status Date'].astype(str)
df['Status Time'] = df['Status Time'].astype(str)
df['Status DateTime'] = pd.to_datetime(df['Status Date'] + ' ' + df['Status Time'])
df = df.drop(columns=['Status Time'])
df = df.drop(columns=['Status Date'])

df['timeDiff'] = df['Status DateTime'] - df['Arrival DateTime']

df = df.drop(columns=['Arrival DateTime'])
df = df.drop(columns=['Status DateTime'])

# Convert timeDiff to numeric (e.g., minutes)
df['timeDiff'] = df['timeDiff'].dt.total_seconds() / 60  # Convert to minutes
print(f'df after Cleaning, shape is {df.shape}')

# Deal with Missing Data: Estimate missing or incorrect entries where feasible, such as Status Time and Status Date for customers who have incomplete information.
# Calculate mean and standard deviation
df = df[(df['timeDiff'] >= 0)]
mean_timeDiff = df['timeDiff'].mean()
std_timeDiff = df['timeDiff'].std()

# Define thresholds (e.g., within N standard deviations of the mean)
lower_limit = mean_timeDiff - nStd * std_timeDiff
upper_limit = mean_timeDiff + nStd * std_timeDiff
lower_limit = 0 if lower_limit < 0 else lower_limit
print(f'mean:{mean_timeDiff}, std:{std_timeDiff}, lower:{lower_limit}, upper:{upper_limit}')

# Filter out rows where timeDiff is outside the normal range
df = df[(df['timeDiff'] >= lower_limit) & (df['timeDiff'] <= upper_limit)]

print(f'df after Removing abnormal timeDiff, shape is {df.shape}')

# 2. Wait Time Estimation (2.5 Points)
# Propose a Model: Develop a method to estimate the wait time for each customer upon arrival, considering whether they were served or abandoned the queue.

# Separate features and target
X = df[['number of visits', 'group size', 'status', 'Position in Queue']]
y = df['timeDiff']

# Preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), ['number of visits', 'group size', 'Position in Queue']),
        ('cat', OneHotEncoder(), ['status'])
    ]
)

# Define the model pipeline
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=randomNum))
])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize, random_state=randomNum)

# Train the model
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print("Root Mean Squared Error:", rmse)
print("Predicted wait times:", y_pred)



# 3. Analysis (4 Points)
# Relationship Examination: Analyze how the estimated wait times relate to the likelihood of a customer reneging.
# Modeling: Use appropriate statistical or machine learning techniques (e.g., logistic regression, Tree-Based) to model this relationship.



