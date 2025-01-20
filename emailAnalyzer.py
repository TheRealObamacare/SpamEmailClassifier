import pandas as pd
import random
import sklearn.model_selection as train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

v = CountVectorizer()
model = MultinomialNB()

df = pd.read_csv('emails.csv')

print(df.head())

# Split the data into training and test sets
train, test = train_test_split.train_test_split(df, test_size=0.2)

x = df['text']
y = df['spam']

x_train, x_test, y_train, y_test = train_test_split.train_test_split(x, y, test_size=0.2)

print(df.groupby('spam').describe())

x_train_count = v.fit_transform(x_train.values)
model.fit(x_train_count, y_train)

x_test_count = v.transform(x_test)
print(model.score(x_test_count, y_test))

print(model.predict(input('Enter a message to test: ')))