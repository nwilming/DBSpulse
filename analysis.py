import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from os import path
import cPickle


def get_dataset(dir):
    a = cPickle.load(open(path.join(dir,'pupil_data')))
    df = pd.concat([to_df(k) for k in a['gaze_positions']])
    df = regular(df)
    if not 'DBSTrigger' in a.keys():
        return df
    triggers = pd.to_datetime(a['DBSTrigger'], unit='s')
    triggers = pd.DatetimeIndex([df.index.asof(x) for x in triggers])
    return df, triggers


def to_df(datum):
    d = {
         'xc':datum['norm_pos'][0],
         'yc':datum['norm_pos'][1],
         'confidence':datum['confidence']
         }
    for eye in datum['base']:
        id = str(eye['id'])
        d.update({
             'x'+id:eye['norm_pos'][0],
             'y'+id:eye['norm_pos'][1],
             'confidence'+id:eye['confidence'],
             'diameter'+id:eye['diameter']
             })
    for key in datum.keys():
        if key.startswith('realtime gaze'):
            data = datum[key]
            d.update({key+'x':data[0], key+'y':data[0]})

    return pd.DataFrame(d, index=[datum['timestamp']])


def interp(x, y, target):
    f = interp1d(x.values.astype(int), y)
    target = target[target.values.astype(int)>min(x.values.astype(int))]
    return pd.DataFrame({y.name:f(target.values.astype(int))}, index=target)


def regular(df):
    dt = pd.to_datetime(df.index.values, unit='s')
    df = df.set_index(dt)
    target = df.resample('16ms').mean().index
    return pd.concat([interp(dt, df[c], target) for c in df.columns], axis=1)


def time_locked(data, time_points, span):
    data = pd.DataFrame(data)
    return pd.concat(
        [time_lock_series(data[d], time_points, span).set_index(['Time', 'Trial']) for d in data], axis=1)

def time_lock_series(data, time_points, span):
    '''
    data should be a Series!
    '''

    data = pd.Series(data)

    def reindex(x, trig):
        x.index = x.index-trig
        return x

    beg, end = pd.Timedelta(span[0], unit='s'), pd.Timedelta(span[1], unit='s')
    oo = pd.concat(
                    [reindex(data.loc[trig-beg:trig+end], trig) for trig in time_points],
                    axis=1)
    oo.columns = np.arange(oo.shape[1])
    oo.columns.name='Trial'
    oo.index.name='Time'
    oo = oo.set_index(np.linspace(span[0], span[1], oo.shape[0]))
    oo = oo.stack().reset_index()
    oo.columns = ['Time', 'Trial'] + [data.name]
    return oo


def foo():
    for i, ds in enumerate(['%03i'%i for i in arange(4, 10)]):
        df, trigs = analysis.get_dataset('/Users/nwilming/recordings/2016_06_01/%s'%ds)
        df.diameter = (df.diameter-df.diameter.mean())/df.diameter.std()
        figure(figsize=(10, 5))
        gs = matplotlib.gridspec.GridSpec(6, 1)
        subplot(gs[1:, :])
        oo = analysis.time_locked(df, trigs, [-2.5, 5])
        sns.tsplot(oo.reset_index(), time='Time', unit='Trial', value='diameter', estimator=nanmean)
        axvline(0, color='k')
        ylim([-1, 1])
        sns.despine()
        subplot(gs[0, :])
        plot(df.diameter)
        plot([df.index[0], df.index[0] + pd.Timedelta(7.5, unit='s')], [-2, -2], 'r')
        for l in trigs:
            axvline(l, color='k', alpha=0.5)
        xticks([])
        yticks([])
        sns.despine()
        savefig('/Users/nwilming/u/DBSpulse/plots/pilot_1_rec_%s.pdf'%ds, bbox_inches='tight')
