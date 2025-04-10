import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title='Galvanize Input', layout='wide')
st.title('Galvanize Data Input Form')

empty_df = pd.DataFrame(columns=[
    'course', 
    'cohort', 
    'first_name', 
    'last_name', 
    'status', 
    'in_utilization'
    ])

empty_df = empty_df.astype({
    'course': 'object',
    'cohort': 'object',
    'first_name': 'object',
    'last_name': 'object',
    'status': 'object',
    'in_utilization': 'bool'
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
        ),
        'in_utilization': st.column_config.CheckboxColumn(
            'In Utilization',
            help='Is student currently being utlizized by the AI Division',
            default=False,
            required=True
        )
    }
)

st.divider()
st.write('Data Entered')

if not edited_df.empty:
    status_counts = edited_df.groupby(['course', 'status']).size().reset_index(name='count')
    unique_statuses = status_counts['status'].unique().tolist()

    color_palette = {
        'Graduated': '#1f77b4',
        'In-Progress': '#2ca02c',
        'Applying': '#ff7f0e',  
    }
    status_colors = [color_palette.get(status, '#808080') for status in unique_statuses] 

    chart = alt.Chart(status_counts).mark_bar().encode(
        x=alt.X('course:N', title='Course Type', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('count:Q', title='Number of Students', axis=alt.Axis(format='d')),
        color=alt.Color('status:N',
                        scale=alt.Scale(domain=unique_statuses, range=status_colors),
                        title='Status'),
        xOffset='status:N',
        tooltip=['course', 'status', 'count']
    ).properties(
        title='Student Statuses'
    )

    st.altair_chart(chart, use_container_width=True)

    st.write('Data For Chart:')
    st.dataframe(status_counts)
else:
    st.write('The table is currently empty.')