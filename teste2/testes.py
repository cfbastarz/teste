#!/usr/bin/env python
# coding: utf-8

import os
import xarray as xr
import numpy as np
import pandas as pd
import panel as pn
import hvplot.xarray
import hvplot.pandas
import hvplot as hv
import cartopy.crs as ccrs
import cartopy.feature as cfeature

Vars = [('VTMP:925', 'Temperatura Virtual @ 925 hPa [K]'),
('VTMP:850', 'Temperatura Virtual @ 850 hPa [K]'),
('VTMP:500', 'Temperatura Virtual @ 500 hPa [K]'),
('TEMP:850', 'Temperatura Absoluta @ 850 hPa [K]'),
('TEMP:500', 'Temperatura Absoluta @ 500 hPa [K]'),
('TEMP:250', 'Temperatura Absoluta @ 250 hPa [K]'),
('PSLC:000', 'Pressão em Superfície [hPa]'),
('UMES:925', 'Umidade Específica @ 925 hPa [g/Kg]'),
('UMES:850', 'Umidade Específica @ 850 hPa [g/Kg]'),
('UMES:500', 'Umidade Específica @ 500 hPa [g/Kg]'),
('ZGEO:850', 'Altura Geopotencial @ 850 hPa [gpm]'),
('ZGEO:500', 'Altura Geopotencial @ 500 hPa [gpm]'),
('ZGEO:250', 'Altura Geopotencial @ 250 hPa [gpm]'),
('UVEL:850', 'Vento Zonal @ 850 hPa [m/s]'),
('UVEL:500', 'Vento Zonal @ 500 hPa [m/s]'),
('UVEL:250', 'Vento Zonal @ 250 hPa [m/s]'),
('VVEL:850', 'Vento Meridional @ 850 hPa [m/s]'),
('VVEL:500', 'Vento Meridional @ 500 hPa [m/s]'),
('VVEL:250', 'Vento Meridional @ 250 hPa [m/s]')]

Regs = ['as']
Exps = ['DTC', 'BAMH', 'BAMH0', 'X666']
StatsE = ['VIES', 'RMSE', 'MEAN']
StatsT = ['VIES', 'RMSE', 'ACOR']
Tests = ['T1']
Refs = ['Análise GFS', 'Reanálise Era5', 'Própria Análise']

data = '20230216002023030300'

burl = 'https://raw.githubusercontent.com/cfbastarz/teste/main/teste2/data/'

df_lst = {}

for reg in Regs:
    for test in Tests:
        kname = test + '_' + reg
        df_lst[kname] = pd.read_csv(os.path.join(burl, test, reg, 'scantec_df_' + test + '_' + reg + '.csv'), index_col=[0,1])


df_as_T1 = df_lst['T1_as']

expt = pn.widgets.MultiChoice(name='Experimentos', value=[Exps[0]], options=Exps, solid=True)
expe = pn.widgets.Select(name='Experimento', value=Exps[0], options=Exps)
varlev = pn.widgets.Select(name='Variável', value=[i[0] for i in Vars][0], options=[i[0] for i in Vars])
statt = pn.widgets.Select(name='Estatística', value=StatsT[0], options=StatsT)
state = pn.widgets.Select(name='Estatística', value=StatsE[0], options=StatsE)
ref = pn.widgets.Select(name='Referência', value=Refs[0], options=Refs)
reg = pn.widgets.Select(name='Região', value=Regs[0], options=Regs)

def getRef(ref):
    if ref == 'Análise GFS': nref = 'T1'
    if ref == 'Reanálise Era5': nref = 'T2'
    if ref == 'Própria Análise': nref = 'T3'
    return nref
    
def getDF(reg, nref):
    if (reg == 'gl' and nref == 'T1'): df = df_gl_T1
    if (reg == 'gl' and nref == 'T2'): df = df_gl_T2
    if (reg == 'gl' and nref == 'T3'): df = df_gl_T3   
    if (reg == 'hn' and nref == 'T1'): df = df_hn_T1
    if (reg == 'hn' and nref == 'T2'): df = df_hn_T2
    if (reg == 'hn' and nref == 'T3'): df = df_hn_T3
    if (reg == 'tr' and nref == 'T1'): df = df_tr_T1
    if (reg == 'tr' and nref == 'T2'): df = df_tr_T2
    if (reg == 'tr' and nref == 'T3'): df = df_tr_T3    
    if (reg == 'hs' and nref == 'T1'): df = df_hs_T1
    if (reg == 'hs' and nref == 'T2'): df = df_hs_T2
    if (reg == 'hs' and nref == 'T3'): df = df_hs_T3    
    if (reg == 'as' and nref == 'T1'): df = df_as_T1
    if (reg == 'as' and nref == 'T2'): df = df_as_T2
    if (reg == 'as' and nref == 'T3'): df = df_as_T3
    return df
    
@pn.depends(statt, expt, varlev, reg, ref)
def plotCurves(statt, expt, varlev, reg, ref):

    nref = getRef(ref)
    
    df = getDF(reg, nref)
               
    for i in Vars:
        if i[0] == varlev:
            nexp_ext = i[1]

    varlev = varlev.lower()

    if statt == 'ACOR':
        axline = pd.DataFrame([0.6 for i in range(12)], columns=[varlev])
    elif statt == 'VIES':
         axline = pd.DataFrame([0.0 for i in range(12)], columns=[varlev])
    else:
         axline = pd.DataFrame([np.nan for i in range(12)], columns=[varlev])

    frame_width=550            
            
    for count, i in enumerate(expt):
        if count == 0:
            exp = expt[count]
            fname = statt + exp + '_20230216002023030300T.scan'
            ax = df.loc[fname].loc[:,[varlev]].hvplot(xlabel='Dias', ylabel=str(statt),
                    grid=True, line_width=3, label=str(exp),
                    fontsize={'ylabel': '12px', 'ticks': 10}, frame_width=frame_width,
                                                     title=str(statt) + ' - ' + str(nexp_ext))
            ax *= axline.hvplot(line_width=1, line_color='black', line_dash='dashed')
        else:
            exp = expt[count]
            fname = statt + exp + '_20230216002023030300T.scan'
            ax *= df.loc[fname].loc[:,[varlev]].hvplot(xlabel='Dias', ylabel=str(statt), 
                                                       grid=True, line_width=3, label=str(exp), frame_width=frame_width,
                                                      title=str(statt) + ' - ' + str(nexp_ext))
            ax *= axline.hvplot(line_width=1, line_color='black', line_dash='dashed')
            
    return ax

card_parameters = pn.Column('**Geral**', pn.layout.Divider(margin=(-15, 0, 0, 0)), varlev, reg, ref, 
                          '**Espacial**', pn.layout.Divider(margin=(-15, 0, 0, 0)), state, expe, 
                          '**Temporal**', pn.layout.Divider(margin=(-15, 0, 0, 0)), statt, pn.Column(expt, height=240))

pn.template.FastListTemplate(
    site='SMNA Dashboard', title='SCANTEC', sidebar=[card_parameters],
    main=['Avaliação objetiva **SMNA**.', 
          pn.Row(pn.Column('###Série Temporal', pn.layout.Divider(margin=(-20, 0, 0, 0)), plotCurves), 
                )],
).servable();
