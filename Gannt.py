import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from dateutil.rrule import rrule, WEEKLY, MONTHLY, FR

# Set wide mode and page title
st.set_page_config(layout="wide", page_title="Advanced Project Management Tool")

# Add "Made By Ashwin Nair" on top of the sidebar
st.sidebar.markdown("### **Made By Ashwin Nair**")

# User Guide at the top of the sidebar
with st.sidebar.expander("User Guide", expanded=True):
    st.write("### User Guide")
    st.write("""
    **Task Management:**
    - Use the sidebar to manage tasks and subtasks.
    - You can add new subtasks under an existing task or create recurring tasks.

    **File Upload:**
    - Upload your project data using the file uploader.
    - Supported formats: CSV, Excel.

    **Project Visualizations:**
    - Explore the Gantt chart for task dependencies.
    - Use the Burn-Down chart to track progress over time.
    - Check resource allocation with the Resource Load Balancing chart.

    **Data Editing:**
    - Edit project details directly within the table.
    - Your changes will be saved automatically.

    **Export:**
    - You can download the current project data as a CSV file for backup or further analysis.
    """)

# Function to load data from file and ensure date formatting
def load_data(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file format. Please upload a CSV or Excel file.")
        return None
    
    # Ensure the date columns are correctly formatted as datetime
    df['Start Date'] = pd.to_datetime(df['Start Date'], format='%m/%d/%Y', errors='coerce')
    df['End Date'] = pd.to_datetime(df['End Date'], format='%m/%d/%Y', errors='coerce')
    return df

# Sidebar for file upload
st.sidebar.header("Upload Project Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.session_state.df = df
else:
    # Initialize DataFrames with dummy data if no file is uploaded
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame({
            "Task": [
                "Design", "Design", "Design", 
                "Development", "Development", 
                "Testing", "Testing", 
                "Deployment"
            ],
            "Subtask": [
                "Requirement Gathering", "UI/UX Design", "Approval",
                "Backend Development", "Frontend Development",
                "Unit Testing", "Integration Testing",
                "Go Live"
            ],
            "Start Date": [
                datetime(2024, 8, 1), datetime(2024, 8, 3), datetime(2024, 8, 7),
                datetime(2024, 8, 10), datetime(2024, 8, 15),
                datetime(2024, 8, 20), datetime(2024, 8, 25),
                datetime(2024, 9, 1)
            ],
            "End Date": [
                datetime(2024, 8, 2), datetime(2024, 8, 6), datetime(2024, 8, 9),
                datetime(2024, 8, 14), datetime(2024, 8, 20),
                datetime(2024, 8, 24), datetime(2024, 8, 30),
                datetime(2024, 9, 5)
            ],
            "Assignee": [
                "Alice", "Bob", "Charlie",
                "David", "Eve",
                "Frank", "Grace",
                "Heidi"
            ],
            "Status": [
                "Completed", "In Progress", "Not Started",
                "In Progress", "Not Started",
                "Not Started", "Not Started",
                "Not Started"
            ],
            "Progress": [
                100, 60, 0,
                50, 0,
                0, 0,
                0
            ],
            "Priority": [
                "High", "Medium", "Medium",
                "High", "Medium",
                "High", "Medium",
                "High"
            ],
            "Time Spent": [
                16, 24, 0,
                40, 0,
                0, 0,
                0
            ],
            "Comments": [
                "Requirements finalized", "UI/UX in progress", "",
                "Backend API development ongoing", "", "", "", ""
            ],
            "Dependencies": [
                "", "Requirement Gathering", "UI/UX Design",
                "Approval", "Backend Development",
                "Frontend Development", "Unit Testing",
                "Integration Testing"
            ],
            "Budget": [
                5000, 8000, 2000,
                15000, 12000,
                5000, 8000,
                10000
            ],
            "Cost": [
                4800, 4000, 0,
                6000, 0,
                0, 0,
                0
            ]
        })

# Task Dependencies Visualization: Gantt Chart with dependencies
def create_gantt_chart_with_dependencies(df):
    # Ensure the Dependencies column is filled with empty strings where there are NaN values
    df['Dependencies'] = df['Dependencies'].fillna('')

    fig = px.timeline(
        df,
        x_start="Start Date",
        x_end="End Date",
        y="Task",
        color="Status",
        hover_data=['Dependencies']
    )
    
    # Add arrows to represent dependencies
    for i, row in df.iterrows():
        if row['Dependencies']:
            for dep in row['Dependencies'].split(','):
                dep = dep.strip()  # Strip any leading or trailing whitespace
                dep_task = df[df['Task'] == dep]
                if not dep_task.empty:
                    fig.add_shape(
                        type="line",
                        x0=dep_task['End Date'].values[0],
                        y0=i,
                        x1=row['Start Date'],
                        y1=i,
                        line=dict(color="red", width=2, dash="dot")
                    )
    
    fig.update_layout(showlegend=True, title="Gantt Chart with Dependencies")
    return fig

# Advanced Recurring Task Management
def add_recurring_task_advanced(task_name, recurrence_type, start_date, end_date):
    if recurrence_type == 'Weekly on Monday':
        rule = rrule(freq=WEEKLY, byweekday=0, dtstart=start_date, until=end_date)
    elif recurrence_type == 'Last Friday of the Month':
        rule = rrule(freq=MONTHLY, byweekday=FR(-1), dtstart=start_date, until=end_date)
    
    for dt in rule:
        # Properly handle datetime when adding timedelta
        end_date = dt + timedelta(days=1)
        st.session_state.df = st.session_state.df.append({
            "Task": task_name,
            "Start Date": dt,
            "End Date": end_date,  
            "Status": "Not Started",
            "Progress": 0,
        }, ignore_index=True)
    st.experimental_rerun()

# Task Prioritization Matrix (Eisenhower Matrix)
def create_prioritization_matrix(df):
    df['Urgency'] = np.random.randint(1, 5, df.shape[0])  # Mock urgency values
    df['Importance'] = np.random.randint(1, 5, df.shape[0])  # Mock importance values

    fig = px.scatter(df, x='Urgency', y='Importance', text='Task', color='Priority',
                     size='Progress', title="Eisenhower Matrix: Task Prioritization",
                     labels={"Urgency": "Urgency (1-4)", "Importance": "Importance (1-4)"})
    return fig

# Project Health Dashboard
def create_project_health_dashboard(df):
    burn_rate = df['Cost'].sum() / df['Budget'].sum()
    budget_vs_actuals = df.groupby('Task').agg({'Budget': 'sum', 'Cost': 'sum'})
    overall_progress = df['Progress'].mean()

    st.subheader("Project Health Dashboard")
    st.metric("Burn Rate", f"{burn_rate:.2f}")
    st.metric("Overall Progress", f"{overall_progress:.2f}%")
    
    st.subheader("Budget vs. Actuals")
    st.bar_chart(budget_vs_actuals)

# Resource Load Balancing
def create_resource_load_chart(df):
    load_df = df.groupby('Assignee').agg({'Time Spent': 'sum', 'Task': 'count'}).reset_index()
    fig = px.bar(load_df, x='Assignee', y='Time Spent', title='Resource Load Balancing', color='Task')
    return fig

# Check if the project is delayed
def check_project_delay(df):
    today_pd = pd.to_datetime(datetime.now()).normalize()

    # Convert 'End Date' to pandas datetime format and normalize both dates
    df['End Date'] = pd.to_datetime(df['End Date']).dt.normalize()

    delayed_tasks = df[df['End Date'] < today_pd]
    if not delayed_tasks.empty:
        st.warning("Warning: The following tasks are delayed:")
        st.dataframe(delayed_tasks[['Task', 'Subtask', 'End Date', 'Assignee']])
    else:
        st.success("All tasks are on schedule!")

# Interactive Onboarding
def show_onboarding():
    st.write("### Welcome to the Project Management App!")
    st.write("""
    This tutorial will guide you through the key features.

    - **Upload Data**: Upload a CSV or Excel file with your project tasks using the sidebar. This allows you to work with your own data within the app.

    - **Manage Tasks**: Use the "Task Management" section in the sidebar to add, update, or delete tasks and subtasks. You can also create recurring tasks to automate task creation.

    - **Visualizations**: Explore various charts and dashboards available in the main view:
      - **Gantt Chart**: Visualize task timelines and dependencies.
      - **Burn-Down Chart**: Track the cumulative progress over time.
      - **Resource Load Balancing**: Check how tasks are distributed among team members.
      - **Kanban Board View**: See tasks categorized by status (To Do, In Progress, Done).
      - **Calendar View**: Get a timeline overview of tasks.

    - **Data Editing**: Directly edit your project data within the table, and your changes will be saved automatically.

    - **Export Options**: Download your current project data or a template CSV file for backup or further analysis using the export options in the sidebar.
    """)

# Initialize onboarding_complete in session state
if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = False

if not st.session_state.onboarding_complete:
    show_onboarding()
    if st.button("Finish Onboarding"):
        st.session_state.onboarding_complete = True
        st.experimental_rerun()

if st.session_state.onboarding_complete:
    st.sidebar.success("Onboarding Complete!")

# Display the DataFrame
st.session_state.df['Subtask'] = st.session_state.df['Subtask'].fillna('')
st.session_state.df['Priority'] = st.session_state.df['Priority'].replace("", "Medium")
st.session_state.df['Progress'] = st.session_state.df['Progress'].replace("", 0)
st.session_state.df['Time Spent'] = st.session_state.df['Time Spent'].replace("", 0)

# Ensure date columns are in correct format
st.session_state.df['Start Date'] = pd.to_datetime(st.session_state.df['Start Date'], errors='coerce')
st.session_state.df['End Date'] = pd.to_datetime(st.session_state.df['End Date'], errors='coerce')

# Convert dates back to strings for display and exporting
st.session_state.df['Start Date'] = st.session_state.df['Start Date'].dt.strftime('%m/%d/%Y')
st.session_state.df['End Date'] = st.session_state.df['End Date'].dt.strftime('%m/%d/%Y')

# Editable DataFrame
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
st.session_state.df = edited_df

# Sidebar for Task Management
with st.sidebar.expander("Task Management", expanded=True):
    # Adding Subtasks
    if st.button("Add Subtask"):
        task_name = st.selectbox("Select Task", st.session_state.df['Task'].unique())
        subtask_name = st.text_input("Subtask Name")
        if subtask_name:
            st.session_state.df = st.session_state.df.append({
                "Task": task_name,
                "Subtask": subtask_name,
                "Status": "Not Started",
                "Progress": 0,
                "Assignee": "Unassigned",
                "Start Date": None,
                "End Date": None
            }, ignore_index=True)
            st.success(f"Subtask '{subtask_name}' added under '{task_name}'")
            st.experimental_rerun()

    # Advanced Recurring Task Management
    recurrence_options = ["Weekly on Monday", "Last Friday of the Month"]
    recurrence_type = st.selectbox("Select Recurrence Type", recurrence_options)
    task_name = st.text_input("Task Name for Recurrence")
    recurrence_interval = st.number_input("Recurrence Interval (days)", min_value=1, value=7)
    start_date = st.date_input("Start Date for Recurrence")
    end_date = st.date_input("End Date for Recurrence")
    if st.button("Add Advanced Recurring Task"):
        add_recurring_task_advanced(task_name, recurrence_type, start_date, end_date)
        st.success(f"Recurring task '{task_name}' added")

# Project Visualizations and Dashboards
st.header("Project Visualizations")

col1, col2, col3 = st.columns(3)

# Gantt Chart with Dependencies
# Convert date columns back to datetime for plotting
st.session_state.df['Start Date'] = pd.to_datetime(st.session_state.df['Start Date'], format='%m/%d/%Y')
st.session_state.df['End Date'] = pd.to_datetime(st.session_state.df['End Date'], format='%m/%d/%Y')

fig_gantt = create_gantt_chart_with_dependencies(st.session_state.df)
st.plotly_chart(fig_gantt, use_container_width=True)

# Burn-Down Chart
burn_down_df = st.session_state.df.groupby('End Date')['Progress'].sum().cumsum().reset_index()
fig_burndown = px.line(burn_down_df, x='End Date', y='Progress', title='Burn-Down Chart')
fig_burndown.update_xaxes(tickformat="%m/%d/%Y")
st.plotly_chart(fig_burndown, use_container_width=True)

# Resource Load Balancing
fig_resource_load = create_resource_load_chart(st.session_state.df)
st.plotly_chart(fig_resource_load, use_container_width=True)

col4, col5, col6 = st.columns(3)

# Task Progress Over Time
completion_df = st.session_state.df.groupby('End Date')['Progress'].sum().reset_index()
fig_progress = px.line(completion_df, x='End Date', y='Progress', title='Task Progress Over Time')
fig_progress.update_xaxes(tickformat="%m/%d/%Y")
st.plotly_chart(fig_progress, use_container_width=True)

# Kanban Board View
with col5:
    st.subheader("Kanban Board View")
    st.write("**To Do**")
    st.write(st.session_state.df[st.session_state.df['Status'] == "Not Started"][['Task', 'Subtask', 'Assignee', 'Start Date', 'End Date']])
    st.write("**In Progress**")
    st.write(st.session_state.df[st.session_state.df['Status'] == "In Progress"][['Task', 'Subtask', 'Assignee', 'Start Date', 'End Date']])
    st.write("**Done**")
    st.write(st.session_state.df[st.session_state.df['Status'].isin(["Completed", "Done"])][['Task', 'Subtask', 'Assignee', 'Start Date', 'End Date']])

# Calendar View
with col6:
    st.subheader("Calendar View")
    fig_calendar = px.timeline(st.session_state.df, x_start="Start Date", x_end="End Date", y="Task", title="Calendar View")
    fig_calendar.update_xaxes(tickformat="%m/%d/%Y")
    st.plotly_chart(fig_calendar, use_container_width=True)

# Project Health Dashboard
create_project_health_dashboard(st.session_state.df)

# Check if the project is delayed
check_project_delay(st.session_state.df)

# Finalizing the layout
st.sidebar.subheader("Layout Customization")
show_timeline = st.sidebar.checkbox("Show Gantt Chart", value=True)
show_burndown = st.sidebar.checkbox("Show Burn-Down Chart", value=True)
show_kanban = st.sidebar.checkbox("Show Kanban Board", value=True)
show_calendar = st.sidebar.checkbox("Show Calendar View", value=True)

if show_timeline:
    st.plotly_chart(fig_gantt)  # Gantt chart
if show_burndown:
    st.plotly_chart(fig_burndown)  # Burn-down chart
if show_kanban:
    st.plotly_chart(fig_resource_load)  # Kanban Board
if show_calendar:
    st.plotly_chart(fig_calendar)  # Calendar View

# Export Data Options
with st.sidebar.expander("Export Options", expanded=True):
    if st.button("Download Current View as CSV"):
        st.session_state.df.to_csv("current_project_view.csv", index=False)
        st.success("Current data view downloaded as 'current_project_view.csv'")

    if st.button("Download Data Template as CSV"):
        template_df = st.session_state.df.copy()
        template_df.to_csv("project_template.csv", index=False)
        st.success("Template downloaded as 'project_template.csv'")
