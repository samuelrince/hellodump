import os.path
from datetime import date, datetime, timedelta
from math import ceil

import pandas as pd
import plotly.graph_objects as go
import pytz
import streamlit as st


APPLIANCE_COLORS = {
    'dishwasher': 'rgba(239, 85, 59, 0.5)',
    'washing_machine': 'rgba(0, 204, 150, 0.5)',
    'oven': 'rgba(171, 99, 250, 0.5)',
    'hotplates': 'rgba(255, 161, 90, 0.5)'
}


def date_picker_component():
    col1, _ = st.columns([0.5, 0.5])
    default_from = datetime.now() - timedelta(days=1)
    dates = col1.date_input('Select a date range:',
                            (default_from, default_from + timedelta(days=1)))
    if len(dates) == 1:
        date_from = dates[0]
        date_to = date_from + timedelta(days=1)
    else:
        date_from, date_to = dates
        if date_to == date_from:
            date_to = date_from + timedelta(days=1)

    from_ = datetime.combine(date_from, datetime.min.time(), tzinfo=pytz.timezone('CET'))
    to_ = datetime.combine(date_to, datetime.min.time(), tzinfo=pytz.timezone('CET'))
    return from_, to_


st.title('HelloDump ⚡️')

df = pd.read_csv('./data/consumption.csv', converters={'datetime': datetime.fromisoformat})
df.sort_values('datetime')


dt_from, dt_to = date_picker_component()

sub = df[(df['datetime'] >= dt_from) & (df['datetime'] < dt_to)]

col1, col2 = st.columns(2)
total_energy = sub['energy'].sum()
col1.metric('Energy (kWh)', round(total_energy, 3))
low_energy = sub[sub['energy'] < 0.05].energy
base_energy = low_energy.sum() + low_energy.mean() * len(sub[sub['energy'] >= 0.05])
col2.metric('Base energy (kWh)', round(base_energy, 3))

fig = go.Figure()
fig.add_trace(go.Bar(
    name='Energy',
    x=sub['datetime'],
    y=sub['energy'],
    # marker=dict(color='#636EFA')
))

fig.add_hline(y=0.05, line_color='orange', annotation_text='Base')


if os.path.exists('./data/labels.csv'):
    labels_df = pd.read_csv('./data/labels.csv', converters={
        'start_datetime': datetime.fromisoformat,
        'end_datetime': datetime.fromisoformat
    })
    sub_labels = labels_df[(labels_df['start_datetime'] >= dt_from) & (labels_df['end_datetime'] < dt_to)]

    max_ = ceil(sub['energy'].max())
    for _, row in sub_labels.iterrows():
        color = APPLIANCE_COLORS.get(row['appliance'], 'rgba(25, 211, 243, 0.5)')
        fig.add_trace(go.Scatter(
            name=row['appliance'],
            x=[row['start_datetime'], row['end_datetime']],
            y=[max_, max_],
            fill='tozeroy',
            # fillcolor=color,
            mode='none',
        ))


fig.update_layout(
    title=f'Energy consumption from {dt_from.date()} to {dt_to.date()}',
    xaxis=dict(title='Datetime'),
    yaxis=dict(title='Energy (kWh)')
)

st.plotly_chart(fig)
