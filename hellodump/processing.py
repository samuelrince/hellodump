import json
import os
from datetime import datetime

import pandas as pd


def process_raw_data():
    data = []
    for root, _, files in os.walk('./data/raw/'):
        for file in files:
            if file.endswith('.json'):
                fp = os.path.join(root, file)

                with open(fp, 'r') as fd:
                    day_data = json.load(fd)
                    for val in day_data['values']:
                        data.append({
                            'datetime': datetime.fromisoformat(val['datetime']),
                            'energy': val['valueKwh']
                        })
    df = pd.DataFrame(data)
    df.to_csv('./data/consumption.csv', index=False)


if __name__ == '__main__':
    process_raw_data()
