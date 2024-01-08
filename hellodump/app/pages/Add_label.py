import os.path
from datetime import datetime, timedelta
from functools import partial

import pandas as pd
import pytz
import streamlit as st


APPLIANCES = {
    'Dishwasher 🍽️': 'dishwasher',
    'Washing machine 👕': 'washing_machine',
    'Oven ♨️': 'oven',
    'Hotplates 🍳': 'hotplates'
}

APPLIANCES_DEFAULT_DURATION = {
    'dishwasher': 135,
    'washing_machine': 130
}

if 'duration' not in st.session_state:
    st.session_state['duration'] = 0


def update_duration(minutes: int) -> None:
    new_duration = st.session_state['duration']
    new_duration += minutes
    if new_duration < 0:
        new_duration = 0
    st.session_state['duration'] = new_duration


def display_duration(duration: int) -> str:
    if duration >= 60:
        hours = duration // 60
        duration -= hours * 60
        if duration > 0:
            return f'{hours}h{duration:02d}'
        else:
            return f'{hours}h'
    elif duration >= 0:
        return str(duration) + 'min'
    else:
        return 'Negative duration'


st.title('Add a label')

appliance = st.selectbox(label='Appliance:', options=APPLIANCES)
appliance_id = APPLIANCES[appliance]

start_date = st.date_input('Date:')
start_time = st.time_input('Start time:')

st.markdown(f'Duration: <code><span style="font-size: 18px; font-weight: bold;">{display_duration(st.session_state["duration"])}</span></code>', unsafe_allow_html=True)
cols = st.columns(5)
cols[0].button('+5min', on_click=partial(update_duration,  5), use_container_width=True)
cols[1].button('+10min', on_click=partial(update_duration,  10), use_container_width=True)
cols[2].button('+30min', on_click=partial(update_duration,  30), use_container_width=True)
cols[3].button('+1h', on_click=partial(update_duration,  60), use_container_width=True)
cols[4].button('+2h', on_click=partial(update_duration,  120), use_container_width=True)

cols = st.columns(5)
cols[0].button('-5min', on_click=partial(update_duration,  -5), use_container_width=True)
cols[1].button('-10min', on_click=partial(update_duration,  -10), use_container_width=True)
cols[2].button('-30min', on_click=partial(update_duration,  -30), use_container_width=True)
cols[3].button('-1h', on_click=partial(update_duration,  -60), use_container_width=True)
cols[4].button('-2h', on_click=partial(update_duration,  -120), use_container_width=True)

if st.button('Submit', type='primary'):
    duration_min = st.session_state['duration']
    if duration_min > 0:
        start_dt = datetime.combine(start_date, start_time, tzinfo=pytz.timezone('CET'))
        end_dt = start_dt + timedelta(minutes=duration_min)
        row = {
            'appliance': appliance_id,
            'start_datetime': start_dt,
            'duration_minutes': duration_min,
            'end_datetime': end_dt
        }
        df = pd.DataFrame([row])
        if os.path.exists('./data/labels.csv'):
            pre_df = pd.read_csv('./data/labels.csv')
            df = pd.concat([pre_df, df])
        df.to_csv('./data/labels.csv', index=False)
        del df
        st.success(f'Successfully added **{appliance}** for **{display_duration(duration_min)}**')
        st.session_state['duration'] = 0
    else:
        st.error(f'Cannot add label because it was used for 0 minute.')
