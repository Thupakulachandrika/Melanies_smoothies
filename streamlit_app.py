# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """choose the fruits you want in your custom smoothie!
    """
)


name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be", name_on_order)

cnx= st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select (col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list=st.multiselect('choose up to 5 ingredients:',my_dataframe,max_selections=5)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')
        
        try:
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            fruityvice_response.raise_for_status()  # Check if the request was successful
            fv_data = fruityvice_response.json()  # Parse JSON response
            fv_df = st.dataframe(data=fv_data, use_container_width=True)
        except requests.exceptions.HTTPError as http_err:
            st.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            st.error(f"Request error occurred: {req_err}")
        except json.JSONDecodeError:
            st.error("Error decoding JSON response. The response might be empty or not in JSON format.")

    #st.write(ingredients_string) 
     
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.write(my_insert_stmt)
    #st.stop()
    time_to_insert=st.button('submit order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅") 



