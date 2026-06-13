import streamlit as st
import datetime

def init_timeline():
    """Initializes the timeline dictionary in session state if it doesn't exist."""
    if 'investigation_timeline' not in st.session_state:
        st.session_state['investigation_timeline'] = {}

def record_timeline_event(event_name: str, meta: str = ""):
    """Records the timestamp of an event only if it hasn't been recorded yet."""
    init_timeline()
    if event_name not in st.session_state['investigation_timeline']:
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        st.session_state['investigation_timeline'][event_name] = {
            'time': now_str,
            'meta': meta
        }

def get_timeline_event(event_name: str) -> dict:
    """Gets the timestamp and metadata for a given event, or None if not completed."""
    init_timeline()
    return st.session_state['investigation_timeline'].get(event_name)

def reset_timeline():
    """Resets the timeline when a new dataset is uploaded."""
    st.session_state['investigation_timeline'] = {}
