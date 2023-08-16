import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime as dt
import calendar
import plotly.graph_objects as go
import data_base as db

#----SETTINGS------
incomes = ['Salary','Blog','Other Income']
expenses = ['Housing','Utilities','Groceries','Car','Other Expenses','Saving']
currency = 'USD'
page_title = 'Income and Expense Tracker'
page_icon = ':money_with_wings:' #emoji from webfx
layout = 'centered'
#-------------------

#----Configurations----
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " ")

#----Drop down values for period selection
years = [dt.today().year - 1, dt.today().year]
months = list(calendar.month_name[1:])


# --- Data base interface ---
def get_all_periods():
   
    items = db.fetch_all()
    periods = [a for a in items]
    
    return periods


# --- Hide streamlit style ---
hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)



# --- Navigation Menu ---
selected = option_menu(
    menu_title=None,
    options = ['Data Entry','Data Visualization'],
    icons=['pencil-fill','bar-chart-fill'],
    orientation='horizontal'
)

if selected == 'Data Entry':
    #----Input and save periods----
    st.header(f'Date Entry in {currency}')
    #create form; note: this form has its own key ('entry_form') and the input is cleared once it's been entered by user
    with st.form('entry_form',clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox('Select Month:',months,key='month')
        col2.selectbox('Select Year:',years, key='year')
        #use divider by inserting three dashes
        "---"
        with st.expander('Income'):
            for income in incomes:
                #note: format is set as integer, step size is set on increments/decrements of 10
                st.number_input(f'{income}', min_value=0, format='%i', step=10, key=income)
        
        with st.expander('Expenses'):
            for expense in expenses:
                st.number_input(f'{expense}', min_value=0, format='%i', step=10, key=expense)
        
        with st.expander('Comment'):
            comment = st.text_area("", placeholder="Enter a comment")

        "---"
        submitted = st.form_submit_button('Save Data')
        if submitted:
            # Note: In order to retrieve the data of each input field, access the key of each widget
            period = str(st.session_state['year']) + "_" + str(st.session_state['month'])
            incomes = {income: st.session_state[income] for income in incomes}
            expenses = {expense: st.session_state[expense] for expense in expenses}
            #insert values into database
            st.write('Data Submitted')
            db.insert_period(period, incomes, expenses, comment)


if selected == 'Data Visualization':
    #--- Plot Periods ---
    st.header('Data Visualization')
    with st.form('saved_periods'):
        #retrieve periods from database
        period = st.selectbox('Select Period:',get_all_periods())
        submitted = st.form_submit_button('Plot Period')
        if submitted:
            #retrieve data from databse
            period_data = db.get_period(period)
            # print(type(period_data))
            comment = period_data["comment"]
            expenses = period_data["expenses"]
            incomes = period_data["incomes"]
            
        
            #create metrics
            total_income = sum(incomes.values())
            totral_expense = sum(expenses.values())
            remaining_budget = total_income - totral_expense
            col1, col2, col3 = st.columns(3)
            col1.metric('Total Income',f'{total_income} {currency}')
            col2.metric('Total Expense', f'{totral_expense} {currency}')
            col3.metric('Remaining Budget', f'{remaining_budget} {currency}')
            st.text(f'Comment: {comment}')

            #create a Sankey chart
            label = list(incomes.keys()) + ['Total Income'] + list(expenses.keys())
            source = list(range(len(incomes))) + [len(incomes)] * len(incomes)
            target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
            value = list(incomes.values()) + list(expenses.values())

            #Data to dict, dict to Sankey
            link = dict(source=source, target=target, value=value)
            node = dict(label=label, pad=20, thickness=30, color='#E694FF')
            data = go.Sankey(link=link, node=node)

            #plot graph
            fig = go.Figure(data)
            fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
            st.plotly_chart(fig, use_container_width=True)

