import itertools

import matplotlib as mpl
import pandas as pd

color = mpl.color_sequences['tab20']


def time_bar_plot(data: pd.DataFrame, **kwargs):
    data = data.agg(mean_time=('time', 'mean'), sem_time=('time', 'sem'))
    data['interval'] = data['sem_time'] * 1.96  # 95% confidence interval
    ax = data.unstack().plot(kind='bar', y='mean_time', yerr='interval', rot=kwargs.pop('rot', 0), ylabel='time (s)', color=color, **kwargs)
    data = [c.datavalues for c in ax.containers if isinstance(c, mpl.container.BarContainer)]
    data = zip(data[0::2], data[1::2])
    data = list(itertools.chain.from_iterable((d / e - 1, [None] * len(e)) for d, e in data))
    for i, container in enumerate(filter(lambda x: isinstance(x, mpl.container.BarContainer), ax.containers)):
        ann = ax.bar_label(container, label_type='edge', fontsize=8, padding=3)
        for j, label in enumerate(ann):
            label.set_text(f'{data[i][j]:.1%}' if data[i][j] else '')


def cumulative_traffic_plot(data: pd.DataFrame, **kwargs):
    data = data.groupby(['size']).agg(total_data=('size', 'sum')).cumsum()
    data.plot(kind='line', y='total_data', ylabel='total data (bytes)', rot=kwargs.pop('rot', 0), **kwargs)
