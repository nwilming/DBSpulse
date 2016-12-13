import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from os import path
import cPickle
import pylab as plt
import matplotlib
import seaborn as sns
sns.set_style('ticks')


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


def baseline(df, time=(-1, 0)):
    return df-df.loc[[slice(-0.5, 0), None]].mean()


def timelocked_analysis(df, trigs, field='diameter', bad_trigs=None):
    if bad_trigs is None:
        bad_trigs = array([False]*len(trigs))
    df = df.query('confidence>0.8')
    df.loc[:, field] = (df[field]-df[field].mean())/df[field].std()
    plt.figure(figsize=(10, 5))
    gs = matplotlib.gridspec.GridSpec(6, 1)
    plt.subplot(gs[1:, :])

    oo = time_locked(df, trigs[~bad_trigs], [-2.5, 5])
    oo = oo.groupby(level='Trial').apply(baseline)
    sns.tsplot(oo.reset_index(), time='Time', unit='Trial', value=field, estimator=plt.nanmean)
    plt.axvline(0, color='k')
    plt.ylim([-1, 1])
    sns.despine()
    plt.subplot(gs[0, :])
    plt.plot(df[field])
    plt.plot([df.index[0], df.index[0] + pd.Timedelta(10, unit='s')], [-2, -2], 'r')
    for i, l in enumerate(trigs):
        if bad_trigs[i]:
            plt.axvline(l, color='k', alpha=0.5)
        else:
            plt.axvline(l, color='r', alpha=0.5)
    plt.xticks([])
    plt.yticks([])
    sns.despine()


def foo():
    for i, ds in enumerate(['%03i'%i for i in arange(4, 10)]):
        df, trigs = analysis.get_dataset('/Users/nwilming/recordings/2016_06_01/%s'%ds)
        df.diameter = (df.diameter-df.diameter.mean())/df.diameter.std()
        plt.figure(figsize=(10, 5))
        gs = matplotlib.gridspec.GridSpec(6, 1)
        plt.subplot(gs[1:, :])
        oo = analysis.time_locked(df, trigs, [-2.5, 5])
        sns.tsplot(oo.reset_index(), time='Time', unit='Trial', value='diameter', estimator=nanmean)
        plt.axvline(0, color='k')
        plt.ylim([-1, 1])
        sns.despine()
        plt.subplot(gs[0, :])
        plt.plot(df[field])
        plt.plot([df.index[0], df.index[0] + pd.Timedelta(7.5, unit='s')], [-2, -2], 'r')
        for l in trigs:
            plt/axvline(l, color='k', alpha=0.5)
        xticks([])
        yticks([])
        sns.despine()
        savefig('/Users/nwilming/u/DBSpulse/plots/pilot_1_rec_%s.pdf'%ds, bbox_inches='tight')


def foo2():
    for d in ds[3:]:
        t = d.split('/')[-1]
        try:
            df, trigs = analysis.get_dataset(d)
            bad_trigs = array([False]*len(trigs))
            if t == '004':
                bad_trigs[:10] = True
            elif t == '006':
                bad_trigs[4:6] = True
            else:
                bad_trigs[0] = True
            analysis.timelocked_analysis(df, trigs, field='diameter0', bad_trigs=bad_trigs)
            title('Dataset: %s'%t)
            savefig('/Users/nwilming/Dropbox/Pupillometry/2016_11_25/%s.pdf'%t)
        except ValueError:
            print 'No triggers for ', d
