import pandas as pd
import numpy as np

class FlowData(object):
  
    def __init__(self):
        super(FlowData, self).__init__()

    
    @staticmethod
    def combine_flowcytometry_records(session, ls_sampleid, ls_bin_columns=None):
        ls_df = []
        for sid in ls_sampleid:
            df = session.get_sample(sid).as_dataframe()
            df[('sid', 'sid')] = sid
            ls_df.append(df)
        dfc = pd.concat(ls_df, axis=0)
        if ls_bin_columns:
            for colname in ls_bin_columns:
                dfc[colname] = 1
        dfc.columns = dfc.columns.droplevel(0)
        dfc = dfc.reset_index()
        return dfc.copy()


    @staticmethod
    def assign_abuduance(distribution:str='gamma', 
                        a:int=3, 
                        scale:int=5, 
                        size:int=10):
        
        rng=np.random.default_rng()
        if distribution == 'gamma':
            abundances = rng.gamma(a, scale=scale, size=size)
    
        abundances = abundances/abundances.sum()
        return abundances
    
    @staticmethod
    def assign_sampling_probability(df, 
                              colname_strain='sid', 
                              strain2P:dict=None,
                               ):
        ret = {}

        # assign probabilities to strain
        dftmp = df.groupby(colname_strain)[colname_strain].count().rename('count').reset_index()
        ret['strain2count'] = dict(zip(dftmp[colname_strain], dftmp['count']))

        if not strain2P:
            dftmp['P_sampling_{}'.format(colname_strain)] = dftmp['count']/dftmp['count'].sum()
            df = df.merge(dftmp[[colname_strain, 'P_sampling_{}'.format(colname_strain)]],
                        on=colname_strain, how='left')
            ret['strain2P'] = dict(zip(dftmp[colname_strain], dftmp['P_sampling_{}'.format(colname_strain)]))
        else:
            df['P_sampling_{}'.format(colname_strain)] = df[colname_strain].apply(lambda x: strain2P[x])
            ret['strain2P'] = strain2P


        # assign probabilities to each event
        df['P_sampling_index'] = df.apply(
            lambda x: ret['strain2P'][x[colname_strain]]/ret['strain2count'][x[colname_strain]],
            axis=1)
        ret['df'] = df.copy()

        return ret