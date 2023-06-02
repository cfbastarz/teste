#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import xarray as xr
import numpy as np
import pandas as pd
import panel as pn
from panel_modal import Modal
import hvplot.xarray
import hvplot.pandas
import hvplot as hv
#import cartopy.crs as ccrs
#import cartopy.feature as cfeature

#pn.extension(sizing_mode='stretch_width')


# In[2]:


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

Regs = ['gl', 'hn', 'tr', 'hs', 'as']
Exps = ['DTC', 'BAMH', 'BAMH0', 'X666']
StatsE = ['VIES', 'RMSE', 'MEAN']
StatsT = ['VIES', 'RMSE', 'ACOR']
Tests = ['T1', 'T2', 'T3']
Refs = ['Análise GFS', 'Reanálise Era5', 'Própria Análise']

data = '20230216002023030300'

burl = 'https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SCANTEC-2.1.0/dataout/periodo'


# In[3]:


#%%time

# Cria um dicionário com todos os arquivos zarr
ds_lst = {}

for reg in Regs:
    for exp in Exps:
        for stat in StatsE:
            for test in Tests:
                kname = test + '_' + reg + '_' + stat + '_' + exp
                ds_lst[kname] = xr.open_dataset(os.path.join(burl, test, reg, stat + exp + '_' + data + 'F.zarr'), engine='zarr', chunks='auto')
                #ds_lst[kname] = xr.open_dataset(os.path.join(burl, test, reg, stat + exp + '_' + data + 'F.zarr'), engine='zarr', chunks={})
                #ds_lst[kname] = xr.open_dataset(os.path.join(burl, test, reg, stat + exp + '_' + data + 'F.zarr'), engine='zarr', chunks={'time': 1})


# In[4]:


#%%time

# Cria um dicionário com todos os arquivos csv
df_lst = {}

for reg in Regs:
    for test in Tests:
        kname = test + '_' + reg
        df_lst[kname] = pd.read_csv(os.path.join(burl, test, reg, 'scantec_df_' + test + '_' + reg + '.csv'), index_col=[0,1])


# In[5]:


df_gl_T1 = df_lst['T1_gl']
df_hn_T1 = df_lst['T1_hn']
df_tr_T1 = df_lst['T1_tr']
df_hs_T1 = df_lst['T1_hs']
df_as_T1 = df_lst['T1_as']

df_gl_T2 = df_lst['T2_gl']
df_hn_T2 = df_lst['T2_hn']
df_tr_T2 = df_lst['T2_tr']
df_hs_T2 = df_lst['T2_hs']
df_as_T2 = df_lst['T2_as']

df_gl_T3 = df_lst['T3_gl']
df_hn_T3 = df_lst['T3_hn']
df_tr_T3 = df_lst['T3_tr']
df_hs_T3 = df_lst['T3_hs']
df_as_T3 = df_lst['T3_as']


# In[6]:


# Constrói as widgets e apresenta o dashboard

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
    
@pn.depends(varlev, reg, expe, state, ref)
def plotFields(varlev, reg, expe, state, ref):
   
    var = varlev.replace(':', '').lower()
    
    for i in Vars:
        if i[0] == varlev:
            nexp_ext = i[1]
    
    nref = getRef(ref)
    
    kname = nref + '_' + reg + '_' + state + '_' + expe
    ds = globals()['ds_lst'][kname]
    
    cmap='tab20c_r'
    
    if reg == 'as': 
        frame_width=500
    else: 
        frame_width=550
  
    #ax = ds[var].hvplot(groupby='time', frame_width=frame_width, cmap=cmap, 
    #                         projection=ccrs.PlateCarree(), coastline=True,
    #                        title=str(state) + ' - ' + str(nexp_ext))    

    ax = ds[var].hvplot(groupby='time', frame_width=frame_width, cmap=cmap, title=str(state) + ' - ' + str(nexp_ext))     
    
    return pn.panel(ax, widget_location='bottom')

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

#################3

text_info = """
# SMNA Dashboard - SCANTEC

Visualização da avaliação objetiva das análises e previsões do Sistema de Modelagem Numérica e Assimilação de dados - **SMNA**.

## Experimentos:

* **DTC**: análises e previsões do experimento com o SMNA utilizando a matriz de covariâncias (**B**) do DTC na resolução TQ0299L064 (parâmetros originais dos arquivos `gsiparm.anl` e `anavinfo`);
* **BAMH0**: análises e previsões do experimento com o SMNA utilizando a matriz de covariâncias do BAM em coordenada híbrida na resolução TQ0299L064 (parâmetros originais dos arquivos `gsiparm.anl` e `anavinfo` - exp. **T0**);
* **BAMH**: análises e previsões do experimento com o SMNA utilizando a matriz de covariâncias do BAM em coordenada híbrida na resolução TQ0299L064 (parâmetros ajustados dos arquivos `gsiparm.anl` e `anavinfo` - exp. **GT4AT2**);
* **X666**: análises e previsões do modelo BAM em coordenada híbrida na resolução TQ0666L064.

## Avaliação:

O SCANTEC foi utilizado para a avaliação objetiva dos experimentos com os seguintes ajustes:

* Interpolação de todos os campos atmosféricos para a resolução 0,4 graus (lat/lon);
* Utilização das seguintes referências:
    * Análise do GFS (análises pós-processadas em níveis de pressão utilizadas pelo modelo BAM);
    * Reanálise Era5;
    * Própria análise (para o modelo BAM - experimento **X666**, devem ser observados os mesmos resultados quando utilizada a análise do GFS como referência).
* Para o cálculo da correlação de anomalia (**ACOR**), considerou-se a média temporal da referência escolhida como climatologia.

---

Atualizado em: 02/06/2023 ([carlos.bastarz@inpe.br](mailto:carlos.bastarz@inpe.br))

"""

show_text = Modal(pn.panel(text_info, width=850))

card_info = pn.Column(show_text.param.open, show_text)

#card_parameters = pn.Card('**Geral**', pn.layout.Divider(margin=(-15, 0, 0, 0)),
#                          varlev, reg, ref, 
#                          '**Espacial**', pn.layout.Divider(margin=(-15, 0, 0, 0)), 
#                          state, expe, 
#                          '**Temporal**', pn.layout.Divider(margin=(-15, 0, 0, 0)), 
#                          statt, pn.Column(expt, height=240), 
#                          title='Ajustes', collapsed=False)

card_parameters = pn.Column('**Informações**', pn.layout.Divider(margin=(-15, 0, 0, 0)), card_info,
                          '**Geral**', pn.layout.Divider(margin=(-15, 0, 0, 0)), varlev, reg, ref, 
                          '**Espacial**', pn.layout.Divider(margin=(-15, 0, 0, 0)), state, expe, 
                          '**Temporal**', pn.layout.Divider(margin=(-15, 0, 0, 0)), statt, pn.Column(expt, height=240))

pn.template.FastListTemplate(
    site='SMNA Dashboard', title='SCANTEC', sidebar=[card_parameters],
    main=['Avaliação objetiva **SMNA**.', 
          pn.Row(pn.Column('###Série Temporal', pn.layout.Divider(margin=(-20, 0, 0, 0)), plotCurves), 
                 pn.Column('###Distribuição Espacial', pn.layout.Divider(margin=(-20, 0, 0, 0)), plotFields))], 
#).show();
).servable();


# In[ ]:




