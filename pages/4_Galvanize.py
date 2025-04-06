import streamlit as st
import pandas as pd

st.set_page_config(page_title='Galvanize Input', layout='wide')
st.title('Galvanize Data Input Form')


empty_df = pd.DataFrame(columns=['course', 'cohort', 'first_name', 'last_name', 'status'])
empty_df = empty_df.astype({
    'course': 'object',
    'cohort': 'object',
    'first_name': 'object',
    'last_name': 'object',
    'status': 'object'
})

edited_df = st.data_editor(
    empty_df,
    num_rows='dynamic',
    use_container_width=True,
    column_config={
        'course': st.column_config.TextColumn(
            'Galvanize Course Type',
            help='Enter the Galvanize Course Attended (e.g. SDI, DDI)',
            required=True
        ),
        'cohort': st.column_config.TextColumn(
            'Cohort Number',
            help='Enter Cohort Attended',
            required=True
        ),
        'first_name': st.column_config.TextColumn(
            'Student First Name',
            help="Students First Name",
            required=True
        ),
        'last_name': st.column_config.TextColumn(
            'Student Last Name',
            help='Students Last Name',
            required=True
        ),
        'status': st.column_config.TextColumn(
            'Status of Student (e.g. Graduated, Inprogress, etc)',
            help='Enter Student Status',
            default='Applying',
            required=True
        )
    }
)

st.divider()
st.write('Data Entered')

if not edited_df.empty:
    st.dataframe(edited_df)
else:
    st.write('The table is currently empty.')