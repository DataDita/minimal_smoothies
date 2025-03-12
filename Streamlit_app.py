import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# App Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# User Input
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Retrieve Fruit Options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()  # Convert to Pandas DataFrame

# Multi-Select Dropdown for Ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Process Selection
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Concatenated ingredients

    for fruit_chosen in ingredients_list:
        search_value = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].values
        if search_value.size > 0:
            search_on = search_value[0]
            st.write(f"The search value for **{fruit_chosen}** is **{search_on}**.")

            # Fetch Nutrition Info
            api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            try:
                response = requests.get(api_url)
                response.raise_for_status()  # Raise error for failed requests
                st.subheader(f"{fruit_chosen} Nutrition Information")
                st.dataframe(response.json(), use_container_width=True)
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching nutrition info: {e}")

    # Order Submission
    if st.button("Submit Order"):
        session.sql(
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)",
            params=(ingredients_string, name_on_order)
        ).collect()
        st.success('Your Smoothie is ordered! ✅')
