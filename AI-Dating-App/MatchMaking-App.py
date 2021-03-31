# Library Imports
from joblib import load
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import _pickle as pickle
from random import sample
from PIL import Image
from scipy.stats import halfnorm
import sys
# Loading the Profiles
with open("refined_profiles_1.pkl", 'rb') as fp:
    df = pickle.load(fp)

with open("refined_cluster_1.pkl", 'rb') as fp:
    cluster_df = pickle.load(fp)

with open("vectorized_refined_1.pkl", 'rb') as fp:
    vect_df = pickle.load(fp)

# Loading the Classification Model
model = load("refined_model_1.joblib")

# Helper Functions
# --------------------------------------------------------


def string_convert(x):
    """
    First converts the lists in the DF into strings
    """
    if isinstance(x, list):
        return ' '.join(x)
    else:
        return x


def vectorization(df, columns, input_df):
    """
    Using recursion, iterate through the df until all the categories have been vectorized
    """
    print("-----------start----------------------------")
    column_name = columns[0]
    print("----------column name------------")
    print(df[column_name])
    # s = pd.Series(df[column_name], dtype="category")
    # print("s.cat.code")
    # print(s.cat.codes)
    # # Checking if the column name has been removed already
    if column_name not in ['Bios', 'location', 'Specialisation', 'Qualification']:
        print('column_name - column namenot in all')
        print(column_name)
        return df, input_df

    # Encoding columns with respective values
    if column_name in ['location', 'Qualification']:
       # Getting labels for the original df
        df[column_name.lower()] = df[column_name].cat.codes#before this code, column_name is still in string
        print("----------column name lower------------")
        print(df[column_name.lower()])#after .cat.codes, this is been transform to int
        # Dictionary for the codes
        print("----------column name------------")
        column_name = columns[0]
        print(df[column_name])#< ---  issue is here (?? why are you been changed 
        d = dict(enumerate(df[column_name].cat.categories)) #<--- if 
        print("----------------------")

        print("yes, i get the dictionary")
        d = {v: k for k, v in d.items()}
        print(d)
        # Getting labels for the input_df
        input_df[column_name.lower()] = d[input_df[column_name].iloc[0]]

        # Dropping the column names
        input_df = input_df.drop(column_name, 1)

        df = df.drop(column_name, 1)

        return vectorization(df, df.columns, input_df)
    # Vectorizing the other columns
    else:
        print('column_name in bois specialisation')
        print(column_name)
        # Instantiating the Vectorizer
        vectorizer = CountVectorizer()

        # Fitting the vectorizer to the columns
        x = vectorizer.fit_transform(df[column_name].values.astype('U'))

        y = vectorizer.transform(input_df[column_name].values.astype('U'))

        # Creating a new DF that contains the vectorized words
        df_wrds = pd.DataFrame(
            x.toarray(), columns=vectorizer.get_feature_names())

        y_wrds = pd.DataFrame(
            y.toarray(), columns=vectorizer.get_feature_names(), index=input_df.index)

        # Concating the words DF with the original DF
        new_df = pd.concat([df, df_wrds], axis=1)

        y_df = pd.concat([input_df, y_wrds], 1)

        # Dropping the column because it is no longer needed in place of vectorization
        new_df = new_df.drop(column_name, axis=1)

        y_df = y_df.drop(column_name, 1)

        return vectorization(new_df, new_df.columns, y_df)


def scaling(df, input_df):
    """
    Scales the new data with the scaler fitted from the previous data
    """
    scaler = MinMaxScaler()

    scaler.fit(df)

    input_vect = pd.DataFrame(scaler.transform(
        input_df), index=input_df.index, columns=input_df.columns)

    return input_vect


def top_ten(cluster, vect_df, input_vect):
    """
    Returns the DataFrame containing the top 10 similar profiles to the new data
    """
    # Filtering out the clustered DF
    des_cluster = vect_df[vect_df['Cluster #']
                          == cluster[0]].drop('Cluster #', 1)

    # Appending the new profile data
    des_cluster = des_cluster.append(input_vect, sort=False)

    # Finding the Top 10 similar or correlated users to the new user
    user_n = input_vect.index[0]

    # Trasnposing the DF so that we are correlating with the index(users) and finding the correlation
    corr = des_cluster.T.corrwith(des_cluster.loc[user_n])

    # Creating a DF with the Top 10 most similar profiles
    top_10_sim = corr.sort_values(ascending=False)[1:11]

    # The Top Profiles
    top_10 = df.loc[top_10_sim.index]

    # Converting the floats to ints
    top_10[top_10.columns[1:]] = top_10[top_10.columns[1:]]

    return top_10.astype('object')


def example_bios():
    """
    Creates a list of random example bios from the original dataset
    """
    # Example Bios for the user
    st.write("-"*100)
    st.text("Some example Bios:\n(Try to follow the same format)")
    for i in sample(list(df.index), 3):
        st.text(df['Bios'].loc[i])
    st.write("-"*100)

# Creating a List for each Category


# Probability dictionary
p = {}


location = ['Jakata',
            'Sumatra',
            'Java',
            'Bali',
            'Kalimantan',
            'Palangkaraya',
            'Samarinda',
            'Banjarmasin',
            'Bandung']

p['location'] = [0.28,
                 0.01,
                 0.16,
                 0.14,
                 0.09,
                 0.06,
                 0.04,
                 0.01,
                 0.21]

# TV Genres
Qualification = ['High School',
                 'Diploma',
                 'Bachelors Degree',
                 'Professional Mechanic',
                 'Junior Mechanic',
                 'Mechanic',
                 'Master',
                 'Doctorate',
                 'Associate']

p['Qualification'] = [0.30,
                      0.23,
                      0.12,
                      0.12,
                      0.09,
                      0.08,
                      0.03,
                      0.02,
                      0.01]

# Religions (could potentially create a spectrum)
Specialisation = ['Advanced Auto Diagnostic Techniques',
                  'Advanced Vehicle Diagnostics and Management',
                  'Automotive Maintenance and Repair',
                  'Motor Vehicle Engineering',
                  'Heavy Vehicle Service',
                  'Maintenance Technian',
                  'Automotive Apprenticeships',
                  'Rail Apprenticeships',
                  'Rail Engineering Operative',
                  'Light Vehicle Service']

p['Specialisation'] = [0.16,
                       0.16,
                       0.01,
                       0.19,
                       0.11,
                       0.05,
                       0.10,
                       0.09,
                       0.07,
                       0.06]


age = None
year_of_experience = None
# Lists of Names and the list of the lists
categories = [location, Specialisation, Qualification, age, year_of_experience]

names = ['location', 'Specialisation',
         'Qualification', 'age', 'year of experience']

combined = dict(zip(names, categories))


# Interactive Section

# Creating the Titles and Image
st.title("AI-MatchMaker")

st.header("Testing Matching system")
st.write("Using Machine Learning to Find the Top matching mechanic for you")

image = Image.open('robot_matchmaker.jpg')

st.image(image, use_column_width=True)

# Instantiating a new DF row to classify later
new_profile = pd.DataFrame(columns=df.columns, index=[df.index[-1]+1])

# Asking for new profile data
new_profile['Bios'] = st.text_input("Enter job description: ")

# Printing out some example bios for the user
example_bios()

# Checking if the user wants random bios instead
random_vals = st.checkbox(
    "Check here if you would like random values for yourself instead")

# Entering values for the user
if random_vals:
    # Adding random values for new data
    for i in new_profile.columns[1:]:
        if i in ['location', 'Qualification']:
            new_profile[i] = np.random.choice(combined[i], 1, p=p[i])

        elif i == 'Age':
            new_profile[i] = halfnorm.rvs(loc=18, scale=8, size=1).astype(int)
        elif i == 'year of experience':
            new_profile[i] = halfnorm.rvs(loc=3, scale=5, size=1).astype(int)

        else:
            new_profile[i] = list(np.random.choice(
                combined[i], size=(1, 3), p=p[i]))

            new_profile[i] = new_profile[i].apply(
                lambda x: list(set(x.tolist())))

else:
    # Manually inputting the data
    for i in new_profile.columns[1:]:
        if i in ['location', 'Qualification']:
            new_profile[i] = st.selectbox(
                f"Enter your choice for {i}:", combined[i])

        elif i == 'Age':
            new_profile[i] = st.slider("What is your prefered age?", 18, 60)
        elif i == 'year of experience':
            new_profile[i] = st.slider(
                "What is your prefered year of experience?", 3, 30)

        else:
            options = st.multiselect(
                f"What is your relevant to your job {i}? (Pick up to 3)", combined[i])

            # Assigning the list to a specific row
            new_profile.at[new_profile.index[0], i] = options

            new_profile[i] = new_profile[i].apply(lambda x: list(set(x)))


# Looping through the columns and applying the string_convert() function (for vectorization purposes)
for col in df.columns:
    df[col] = df[col].apply(string_convert)

    new_profile[col] = new_profile[col].apply(string_convert)


# Displaying the User's Profile
st.write("-"*1000)
st.write("Your profile:")
st.table(new_profile)

# Push to start the matchmaking process
button = st.button("Click to find matching mechanic")

if button:
    # try:
    with st.spinner('Finding your Top 10 Matches...'):
        # Vectorizing the New Data
        df_v, input_df = vectorization(df, df.columns, new_profile)

        # Scaling the New Data
        new_df = scaling(df_v, input_df)

        # Predicting/Classifying the new data
        cluster = model.predict(new_df)

        # Finding the top 10 related profiles
        top_10_df = top_ten(cluster, vect_df, new_df)

        # Success message
        st.success("Found your Top 10 Most Relevant mechanic")
        st.balloons()

        # Displaying the Top 10 similar profiles
        st.table(top_10_df)
    # except Exception as e:
    #     print(e)
    #     print("Next entry.")
    #     print()
