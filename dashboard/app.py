import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json

# Set page config
st.set_page_config(
    page_title="Exam Anxiety Reduction Dashboard",
    page_icon="📊",
    layout="wide"
)

# API base URL
API_BASE_URL = "http://localhost:8000/api/v1"

# Title
st.title("🧠 AI-Driven Exam Anxiety Reduction Dashboard")

# Sidebar for student selection
st.sidebar.header("Student Selection")
student_id = st.sidebar.number_input("Enter Student ID", min_value=1, value=1, step=1)

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Daily Goals", "📈 Progress", "😊 Encouragement", "📊 Analytics"])

with tab1:
    st.header(f"Today's Micro-Goals for Student {student_id}")
    
    # Generate daily goals
    if st.button("Generate Daily Goals"):
        try:
            response = requests.post(f"{API_BASE_URL}/micro-goals/generate?student_id={student_id}")
            if response.status_code == 200:
                goals = response.json()
                if goals:
                    for goal in goals:
                        st.write(f"• {goal['goal_text']} (Time: {goal['estimated_time']} mins)")
                        # Add completion button
                        if st.button(f"Mark Complete - Goal {goal['id']}", key=f"complete_{goal['id']}"):
                            complete_response = requests.put(f"{API_BASE_URL}/micro-goals/{goal['id']}/complete")
                            if complete_response.status_code == 200:
                                st.success("Goal marked as completed!")
                                st.rerun()  # Refresh the page to update the display
                            else:
                                st.error("Error marking goal as complete")
                else:
                    st.info("No goals generated. Try again later.")
            else:
                st.error(f"Error generating goals: {response.text}")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
    
    # Show existing goals
    try:
        response = requests.get(f"{API_BASE_URL}/micro-goals/{student_id}")
        if response.status_code == 200:
            goals = response.json()
            if goals:
                df_goals = pd.DataFrame(goals)
                df_goals['completed'] = df_goals['completed'].map({True: '✅ Completed', False: '⏳ Pending'})
                df_goals['created_at'] = pd.to_datetime(df_goals['created_at'], format='ISO8601')
                
                st.subheader("Your Goals")
                for _, goal in df_goals.iterrows():
                    status = "✅" if goal['completed'] == '✅ Completed' else "⏳"
                    completion_text = "Completed" if goal['completed'] == '✅ Completed' else "Pending"
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"{status} **{goal['goal_text']}** - Est. {goal['estimated_time']} mins - {completion_text}")
                    with col2:
                        if not goal['completed'].startswith('✅'):
                            if st.button(f"Complete", key=f"complete_inline_{goal['id']}"):
                                complete_response = requests.put(f"{API_BASE_URL}/micro-goals/{goal['id']}/complete")
                                if complete_response.status_code == 200:
                                    st.success("Goal marked as completed!")
                                    st.rerun()
                                else:
                                    st.error("Error marking goal as complete")
                    with col3:
                        if st.button(f"Delete", key=f"delete_{goal['id']}"):
                            delete_response = requests.delete(f"{API_BASE_URL}/micro-goals/{goal['id']}")
                            if delete_response.status_code == 200:
                                st.success("Goal deleted!")
                                st.rerun()
                            else:
                                st.error("Error deleting goal")
            else:
                st.info("No goals found. Generate some daily goals!")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
    
    # Add performance input form
    st.subheader("Log Performance Data")
    with st.form(key='performance_form'):
        topic_id = st.number_input("Topic ID", min_value=1, value=1, step=1)
        score = st.slider("Score (%)", min_value=0, max_value=100, value=50, step=1)
        time_spent = st.slider("Time Spent (minutes)", min_value=1, max_value=120, value=30, step=5)
        mistakes = st.text_area("Mistakes Made (optional)", placeholder="Describe any mistakes or difficulties encountered...")
        completed = st.checkbox("Completed", value=True)
        submit_performance = st.form_submit_button(label='Log Performance')
        
        if submit_performance:
            try:
                performance_data = {
                    "student_id": student_id,
                    "topic_id": int(topic_id),
                    "score": float(score),
                    "time_spent": int(time_spent),
                    "mistakes": mistakes if mistakes.strip() else None,
                    "completed": completed
                }
                response = requests.post(f"{API_BASE_URL}/performance-records", json=performance_data)
                if response.status_code == 200:
                    st.success("Performance data logged successfully!")
                else:
                    st.error(f"Error logging performance: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
    
    # Add custom goal input form
    st.subheader("Create Custom Goal")
    with st.form(key='custom_goal_form'):
        goal_text = st.text_input("Goal Description", placeholder="e.g., Revise Chapter 3 formulas for 20 minutes")
        estimated_time = st.slider("Estimated Time (minutes)", min_value=5, max_value=60, value=20, step=5)
        priority = st.selectbox("Priority Level", options=[1, 2, 3, 4, 5], index=2, help="1 = Lowest, 5 = Highest priority")
        topic_id = st.number_input("Topic ID", min_value=1, value=1, step=1, help="Select the topic this goal relates to")
        submit_goal = st.form_submit_button(label='Add Custom Goal')
        
        if submit_goal:
            if goal_text.strip():
                try:
                    goal_data = {
                        "student_id": student_id,
                        "topic_id": int(topic_id),
                        "goal_text": goal_text,
                        "estimated_time": int(estimated_time),
                        "priority": int(priority)
                    }
                    response = requests.post(f"{API_BASE_URL}/micro-goals", json=goal_data)
                    if response.status_code == 200:
                        st.success("Custom goal added successfully!")
                    else:
                        st.error(f"Error adding goal: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
            else:
                st.warning("Please enter a goal description")

with tab2:
    st.header("Progress & Confidence Tracking")
    
    # Get confidence score
    try:
        response = requests.get(f"{API_BASE_URL}/confidence-score/{student_id}")
        if response.status_code == 200:
            confidence_score = response.json()
            st.metric(label="Confidence Score", value=f"{confidence_score}/100", delta=None)
            
            # Visualize confidence level
            if confidence_score >= 70:
                st.success("High confidence level! Keep up the great work!")
            elif confidence_score >= 40:
                st.info("Moderate confidence. Consistent effort will improve this!")
            else:
                st.warning("Low confidence. Focus on small wins to build momentum.")
        else:
            st.error("Could not fetch confidence score")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
    
    # Refresh button to update scores
    if st.button("Refresh Progress Data"):
        st.rerun()
    
    # Get anxiety signals
    try:
        response = requests.get(f"{API_BASE_URL}/anxiety-signals/{student_id}")
        if response.status_code == 200:
            signals = response.json()
            if signals:
                st.subheader("Recent Anxiety Signals")
                df_signals = pd.DataFrame(signals)
                df_signals['detected_at'] = pd.to_datetime(df_signals['detected_at'], format='ISO8601')
                
                for _, signal in df_signals.iterrows():
                    if signal['signal_type'] == 'stress':
                        st.warning(f"⚠️ {signal['description']}")
                    elif signal['signal_type'] in ['improvement_streak', 'consistency']:
                        st.success(f"✅ {signal['description']}")
                    else:
                        st.info(f"ℹ️ {signal['description']}")
            else:
                st.info("No anxiety signals detected recently.")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")

with tab3:
    st.header("Encouragement Messages")
    
    # Get daily encouragement
    if st.button("Get Daily Encouragement"):
        try:
            response = requests.post(f"{API_BASE_URL}/encouragements/daily/{student_id}")
            if response.status_code == 200:
                message = response.json()
                st.success(f"💬 {message}")
            else:
                st.error(f"Error getting encouragement: {response.text}")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
    
    # Show all encouragements
    try:
        response = requests.get(f"{API_BASE_URL}/encouragements/{student_id}")
        if response.status_code == 200:
            encouragements = response.json()
            if encouragements:
                st.subheader("Recent Encouragements")
                for msg in encouragements[:5]:  # Show last 5 messages
                    viewed_status = "👁️" if msg['viewed'] else "🆕"
                    st.write(f"{viewed_status} **{msg['message_type'].title()}**: {msg['message']}")
            else:
                st.info("No encouragement messages yet. Generate some!")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")

with tab4:
    st.header("Analytics Dashboard")
    
    try:
        # Get performance data
        performance_response = requests.get(f"{API_BASE_URL}/micro-goals/{student_id}")
        if performance_response.status_code == 200:
            goals = performance_response.json()
            if goals:
                df_goals = pd.DataFrame(goals)
                df_goals['created_at'] = pd.to_datetime(df_goals['created_at'], format='ISO8601')
                
                # Goal completion chart
                completion_counts = df_goals['completed'].value_counts()
                # Ensure names and values have the same length
                names = []
                values = []
                if '✅ Completed' in completion_counts.index:
                    names.append('Completed')
                    values.append(completion_counts['✅ Completed'])
                if '⏳ Pending' in completion_counts.index:
                    names.append('Pending')
                    values.append(completion_counts['⏳ Pending'])
                
                if len(names) > 0 and len(values) > 0:
                    fig = px.pie(
                        values=values,
                        names=names,
                        title='Goal Completion Status'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No goals to display in chart")
                
                # Goals over time
                df_goals['date'] = df_goals['created_at'].dt.date
                goals_by_date = df_goals.groupby('date').size().reset_index(name='count')
                
                fig2 = px.line(
                    goals_by_date,
                    x='date',
                    y='count',
                    title='Goals Generated Over Time'
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Performance by priority
                if 'priority' in df_goals.columns:
                    priority_counts = df_goals.groupby('priority')['completed'].value_counts().unstack(fill_value=0)
                    st.bar_chart(priority_counts)
                
                # Get performance records to analyze study time
                performance_response = requests.get(f"{API_BASE_URL}/performance-records/student/{student_id}")
                if performance_response.status_code == 200:
                    performance_data = performance_response.json()
                    if performance_data:
                        df_perf = pd.DataFrame(performance_data)
                        
                        # Convert date column to datetime if it exists
                        if 'date' in df_perf.columns:
                            df_perf['date'] = pd.to_datetime(df_perf['date'], format='ISO8601')
                            
                            # Study time over time
                            study_time_by_date = df_perf.groupby(df_perf['date'].dt.date)['time_spent'].sum().reset_index()
                            study_time_by_date.columns = ['date', 'total_time_spent']
                            
                            fig_study_time = px.line(
                                study_time_by_date,
                                x='date',
                                y='total_time_spent',
                                title='Total Study Time Per Day (Minutes)'
                            )
                            st.plotly_chart(fig_study_time, use_container_width=True)
                            
                            # Average study time per session
                            avg_study_time = df_perf['time_spent'].mean()
                            st.metric(label="Average Study Time Per Session", value=f"{avg_study_time:.1f} minutes")
                            
                            # Total study time
                            total_study_time = df_perf['time_spent'].sum()
                            st.metric(label="Total Study Time", value=f"{total_study_time} minutes")
                            
                            # Time spent by topic
                            if 'topic_id' in df_perf.columns:
                                topic_time = df_perf.groupby('topic_id')['time_spent'].sum().reset_index()
                                topic_time = topic_time.sort_values('time_spent', ascending=False)
                                
                                fig_topic_time = px.bar(
                                    topic_time,
                                    x='topic_id',
                                    y='time_spent',
                                    title='Time Spent by Topic (Minutes)'
                                )
                                st.plotly_chart(fig_topic_time, use_container_width=True)
        
        # Get confidence trend
        # Note: In a real implementation, we'd want historical confidence data
        # For now, we'll just display the current confidence score again
        confidence_response = requests.get(f"{API_BASE_URL}/confidence-score/{student_id}")
        if confidence_response.status_code == 200:
            current_confidence = confidence_response.json()
            st.subheader(f"Current Confidence Level: {current_confidence}/100")
            
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
    
    # Refresh button to update analytics
    if st.button("Refresh Analytics"):
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*Remember: Consistency matters more than perfection. Every small step builds confidence.*")