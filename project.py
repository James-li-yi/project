import pandas as pd
import plotly.express as px
import streamlit as st

# dashboard page and title creation
st.set_page_config(page_title="USCrime", page_icon=":seedling:", layout="wide")
st.title(":seedling: US Crime in 2016")



# data import and prep
dfcrime = pd.read_csv(r"C:\Users\admin\USCrime.csv")
dfcrime_2016 = dfcrime.loc[dfcrime['year']==2016]
df = dfcrime_2016.loc[~(dfcrime_2016['State'] == 'DC') & ~(dfcrime_2016['State'] == 'All')]
df.drop("year", axis=1, inplace=True)
df.rename(columns={'State':'code'}, inplace=True)
df.drop("population", axis=1, inplace=True)
df.reset_index(inplace=True)
df.drop("index", axis=1, inplace=True)
link = "https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv"

df_compare = pd.read_csv(link)
df_compare_2 = df_compare[['code','state']].copy()
df_new = pd.merge(left=df, right=df_compare_2, how='inner', on=['code'])
df_new.rename(columns={'rape_revised':'rape','Total':'total'}, inplace=True)
categories =['violent_crime','homicide','rape','robbery','aggravated_assault','property_crime','burglary','larceny','motor_vehicle_theft']
df_cat = pd.melt(frame=df_new, id_vars=['code', 'state'], 
                 value_vars=categories, var_name='category', value_name='count')







# Create a new list of categories with 'total exports' as the first element
choropleth_categories = ['total'] + categories

# Sidebar for choropleth category selection
st.sidebar.header("Filter Data by Criminal Category: ")

# Filter functionality for choropleth using a select box in the side bar
choropleth_category = st.sidebar.selectbox("Select Category for Choropleth Map:",
                                            choropleth_categories,
                                            index=0  # this is my default setting; first element is total imports
                                          )

    
# figure 1: total exports by state in a choropleth

# create a title for the first figure
st.subheader(f"US crimes by State  - {choropleth_category.title()}")

st.download_button(label="Download Data", data=df_new.to_csv(), file_name='us_crime.csv')

# create the choropleth figure
fig = px.choropleth(data_frame=df_new,
                    locationmode='USA-states',
                    locations='code',
                    scope="usa",
                    color=choropleth_category,
                    hover_name="state",
                    hover_data= choropleth_category,
                    color_continuous_scale=px.colors.sequential.algae,
                    width=1700,
                    height=800
                    )

# creating a dynamic title
coro_title = choropleth_category.title()+' count'

# customization of choropleth color bar
fig.update_layout(coloraxis_colorbar= dict(title=coro_title, len=0.7, thickness=50))
                  
# display figure in dashboard
st.plotly_chart(fig, use_container_width=True)





# Create a new list of states with 'All States' as the first element
#df.sort_values('code', inplace=True) # just sorting alphabetically acc. to state
states = ['All States'] + df_new['state'].tolist()

# Add another side bar header
st.sidebar.header("Filter Data by State(s): ")

# Add multi-select filter for states
state_list = st.sidebar.multiselect("Choose State(s) for Bar and Donut Charts", options=states, default=['All States'])

# logic for the state selection
if state_list==['All States']:
    df_states=df_new.copy()
    df_cat_states = df_cat.copy()
else:
    df_states=df_new.loc[df_new["state"].isin(state_list)]
    df_cat_states = df_cat.loc[df_cat['state'].isin(state_list)]

df_states.sort_values('total', ascending=False, inplace=True) # sorting for the bar chart

# dasboard columns creation
col1, col2 = st.columns((2))


# Figure 2: total exports by state in a bar chart for chosen states
with col1:

    formatted_states = ", ".join(state_list)
    st.subheader("Total count - "+formatted_states)
    
    fig=px.bar(data_frame=df_states, x='code', y="total", hover_name="state",
               color_continuous_scale=px.colors.sequential.algae,
               color="total",
               labels={'code': 'State', 'total':'Total crime'},
               height=600)
    
    fig.update_layout(coloraxis_colorbar= dict(len=0.7, thickness=30))
    
    st.plotly_chart(fig, use_container_width=True)


# Figure 3: categories breakdown for chosen states
with col2:
    st.subheader("Categories Breakdown - "+formatted_states)
    cat_states_agg = df_cat_states.groupby("category")[['count']].sum().reset_index()
    fig = px.pie(data_frame=cat_states_agg, names='category', values='count', 
             color='category', color_discrete_sequence=px.colors.qualitative.Prism,               
             hole=0.3,
             height=600, width=600)

    # Set the legend title
    fig.update_layout(legend_title=dict(text="Crime Categories"))

    st.plotly_chart(fig, use_container_width=False)
