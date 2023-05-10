#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import hvplot.pandas
import panel as pn
import numpy as np

pn.extension(sizing_mode="stretch_width", notifications=True)


# In[2]:


df_gl = pd.read_csv('https://raw.githubusercontent.com/cfbastarz/teste/main/data/scantec_df_gl.csv', index_col=[0,1])
df_hn = pd.read_csv('https://raw.githubusercontent.com/cfbastarz/teste/main/data/scantec_df_hn.csv', index_col=[0,1])
df_tr = pd.read_csv('https://raw.githubusercontent.com/cfbastarz/teste/main/data/scantec_df_tr.csv', index_col=[0,1])
df_hs = pd.read_csv('https://raw.githubusercontent.com/cfbastarz/teste/main/data/scantec_df_hs.csv', index_col=[0,1])
df_as = pd.read_csv('https://raw.githubusercontent.com/cfbastarz/teste/main/data/scantec_df_as.csv', index_col=[0,1])


# In[3]:


Vars = [('VTMP:925', 'Virtual Temperature @ 925 hPa [K]'),
 ('VTMP:850', 'Virtual Temperature @ 850 hPa [K]'),
 ('VTMP:500', 'Virtual Temperature @ 500 hPa [K]'),
 ('TEMP:850', 'Absolute Temperature @ 850 hPa [K]'),
 ('TEMP:500', 'Absolute Temperature @ 500 hPa [K]'),
 ('TEMP:250', 'Absolute Temperature @ 250 hPa [K]'),
 ('PSNM:000', 'Pressure reduced to MSL [hPa]'),
 ('UMES:925', 'Specific Humidity @ 925 hPa [g/Kg]'),
 ('UMES:850', 'Specific Humidity @ 850 hPa [g/Kg]'),
 ('UMES:500', 'Specific Humidity @ 500 hPa [g/Kg]'),
 ('AGPL:925', 'Inst. Precipitable Water @ 925 hPa [Kg/m2]'),
 ('ZGEO:850', 'Geopotential height @ 850 hPa [gpm]'),
 ('ZGEO:500', 'Geopotential height @ 500 hPa [gpm]'),
 ('ZGEO:250', 'Geopotential height @ 250 hPa [gpm]'),
 ('UVEL:850', 'Zonal Wind @ 850 hPa [m/s]'),
 ('UVEL:500', 'Zonal Wind @ 500 hPa [m/s]'),
 ('UVEL:250', 'Zonal Wind @ 250 hPa [m/s]'),
 ('VVEL:850', 'Meridional Wind @ 850 hPa [m/s]'),
 ('VVEL:500', 'Meridional Wind @ 500 hPa [m/s]'),
 ('VVEL:250', 'Meridional Wind @  250 hPa [m/s]')]

Regs = ['gl', 'hn', 'tr', 'hs', 'as']

Stats = ['ACOR', 'RMSE', 'VIES']

Exps = ['X666', 'DTC', 'BAMH']

exps = pn.widgets.MultiChoice(name='Experimentos', value=[Exps[0]], options=Exps, solid=False)
varlev = pn.widgets.Select(name='Variável', value=[i[0] for i in Vars][0], options=[i[0] for i in Vars])
stat = pn.widgets.Select(name='Estatística', value=Stats[0], options=Stats)
reg = pn.widgets.Select(name='Região', value=Regs[0], options=Regs)

@pn.depends(stat, exps, varlev, reg)
def plot_curves_hvplot(stat, exps, varlev, reg):

    if reg == 'gl': df = df_gl
    if reg == 'hn': df = df_hn
    if reg == 'tr': df = df_tr
    if reg == 'hs': df = df_hs
    if reg == 'as': df = df_as

    for i in Vars:
        if i[0] == varlev:
            nexp_ext = i[1]
    
    varlev = varlev.lower()

    if stat == 'ACOR':
        axline = pd.DataFrame([0.6 for i in range(12)], columns=[varlev])
    elif stat == 'VIES':
        axline = pd.DataFrame([0.0 for i in range(12)], columns=[varlev])   
    else:
        axline = pd.DataFrame([np.nan for i in range(12)], columns=[varlev])  
    
    for count, i in enumerate(exps):
        if count == 0:
            exp = exps[count]
            fname = stat + exp + '_20230216002023030300T.scan'
            ax = df.loc[fname].loc[:,[varlev]].hvplot(xlabel='Dias', ylabel=str(stat) + '\n' + str(nexp_ext), 
                                                      grid=True, line_width=3, label=str(exp),
                                                     fontsize={'ylabel': '12px', 'ticks': 10})
            ax *= axline.hvplot(line_width=1, line_color='black', line_dash='dashed')
        else:
            exp = exps[count]
            fname = stat + exp + '_20230216002023030300T.scan'
            ax *= df.loc[fname].loc[:,[varlev]].hvplot(xlabel='Dias', ylabel=str(stat) + "\n" + str(nexp_ext), grid=True, line_width=3, label=str(exp))  
            ax *= axline.hvplot(line_width=1, line_color='black', line_dash='dashed')
            
    return ax

card_parameters = pn.Card(stat, varlev, reg, pn.Column(exps, height=240), title="Parâmetros", collapsed=False)

settings = pn.Column(card_parameters, width_policy='max')

pn.template.FastListTemplate(
    site="SMNA Dashboard", title="Avaliação Objetiva", sidebar=[settings],
    main=["Visualização da avaliação objetiva das previsões do **SMNA**.", plot_curves_hvplot],
#).show();
).servable();

# In[ ]:




