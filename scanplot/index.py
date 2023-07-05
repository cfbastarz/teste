#!/usr/bin/env python
# coding: utf-8

# Usar o ambiente SCANTEC_DASHBOARD

import os
import intake
import requests
import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
import seaborn as sns
import panel as pn
import hvplot.xarray
import hvplot.pandas
import hvplot as hv
import holoviews as hvs
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from datetime import datetime
from matplotlib import pyplot as plt

hvs.extension('bokeh')

pn.extension('katex')
pn.extension('floatpanel')
pn.extension(notifications=True)
pn.extension(sizing_mode='stretch_width')

# @cfbastarz, Jun/2023 (carlos.bastarz@inpe.br)

Vars = [('VTMP:925', 'Temperatura Virtual @ 925 hPa [K]'),
('VTMP:850', 'Temperatura Virtual @ 850 hPa [K]'),
('VTMP:500', 'Temperatura Virtual @ 500 hPa [K]'),
('TEMP:850', 'Temperatura Absoluta @ 850 hPa [K]'),
('TEMP:500', 'Temperatura Absoluta @ 500 hPa [K]'),
('TEMP:250', 'Temperatura Absoluta @ 250 hPa [K]'),
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

list_var = [ltuple[0].lower() for ltuple in Vars]

Regs = ['gl', 'hn', 'tr', 'hs', 'as']
Exps = ['EXP18', 'X666']
StatsE = ['VIES', 'RMSE', 'MEAN']
StatsT = ['VIES', 'RMSE', 'ACOR']

Refs = ['ref_era5_no_clim', 'ref_panl_no_clim', 'ref_panl_cfsr_clim', 'ref_panl_agcm_clim']

bpath = '/extra2/SCANTEC_EGEON/SCANTEC-2.1.0/dataout/periodo'

date_range = '20191115122020020100'


# Download dos catálogos a partir do script (catálogos locais com dados remotos)
url = 'https://s0.cptec.inpe.br/pesquisa/das/dist/carlos.bastarz/SCANTEC-2.1.0/dataout/periodo/EXP18/catalog-scantec-s0.yml'
r = requests.get(url, allow_redirects=True)
open('catalog-scantec-s0.yml', 'wb').write(r.content)
ds_catalog = intake.open_catalog('catalog-scantec-s0.yml')

colormaps = ['Accent',  'Blues',  'BrBG',  'BuGn',  'BuPu',  'CMRmap',  'Dark2',  'GnBu', 
             'Greens',  'Greys',  'OrRd',  'Oranges',  'PRGn',  'Paired',  'Pastel1', 
             'Pastel2',  'PiYG',  'PuBu', 'PuBuGn',   'PuOr',  'PuRd',  'Purples', 
             'RdBu',  'RdGy',  'RdPu',  'RdYlBu',  'RdYlGn',  'Reds',  'Set1', 
             'Set2',  'Set3',  'Spectral',  'Wistia',  'YlGn', 'YlGnBu',   'YlOrBr', 
             'YlOrRd',  'afmhot',  'autumn',  'binary',  'bone',  'brg',  'bwr', 
             'cet_CET_C1', 'cet_CET_C10',  'cet_CET_C10s',  'cet_CET_C11',  'cet_CET_C11s',  
             'cet_CET_C1s',  'cet_CET_C2',  'cet_CET_C2s',  'cet_CET_C3',  
             'cet_CET_C3s',  'cet_CET_C4',  'cet_CET_C4s',  'cet_CET_C5',  'cet_CET_C5s', 
             'cet_CET_C6',  'cet_CET_C6s',  'cet_CET_C7',  'cet_CET_C7s', 
             'cet_CET_C8',  'cet_CET_C8s',  'cet_CET_C9',  'cet_CET_C9s',  'cet_CET_CBC1', 
             'cet_CET_CBC2',  'cet_CET_CBD1',  'cet_CET_CBD2',  'cet_CET_CBL1', 
             'cet_CET_CBL2',  'cet_CET_CBL3',  'cet_CET_CBL4',  'cet_CET_CBTC1',
             'cet_CET_CBTC2',  'cet_CET_CBTD1',  'cet_CET_CBTL1',  'cet_CET_CBTL2',
             'cet_CET_CBTL3',  'cet_CET_CBTL4',  'cet_CET_D1', 'cet_CET_D10',  'cet_CET_D11',
             'cet_CET_D12',  'cet_CET_D13',  'cet_CET_D1A',   'cet_CET_D2',
             'cet_CET_D3',  'cet_CET_D4',  'cet_CET_D6',  'cet_CET_D7',  'cet_CET_D8',
             'cet_CET_D9',  'cet_CET_I1',  'cet_CET_I2',  'cet_CET_I3',  'cet_CET_L1', 
             'cet_CET_L10',  'cet_CET_L11',  'cet_CET_L12',  'cet_CET_L13',  'cet_CET_L14', 
             'cet_CET_L15',  'cet_CET_L16',  'cet_CET_L17',  'cet_CET_L18',  
             'cet_CET_L19',   'cet_CET_L2', 'cet_CET_L20',   'cet_CET_L3',  'cet_CET_L4',
             'cet_CET_L5',  'cet_CET_L6',  'cet_CET_L7',  'cet_CET_L8',  'cet_CET_L9', 
             'cet_bgy', 
             'cet_bgyw',  'cet_bjy',  'cet_bkr',  'cet_bky',  'cet_blues',  'cet_bmw',
             'cet_bmy',  'cet_bwy',  'cet_circle_mgbm_67_c31',  'cet_circle_mgbm_67_c31_s25',
             'cet_colorwheel',  'cet_coolwarm',  'cet_cwr',  
             'cet_cyclic_bgrmb_35_70_c75',  'cet_cyclic_bgrmb_35_70_c75_s25',  
             'cet_cyclic_grey_15_85_c0',  'cet_cyclic_grey_15_85_c0_s25',  'cet_cyclic_isoluminant',
             'cet_cyclic_mrybm_35_75_c68',  'cet_cyclic_mrybm_35_75_c68_s25', 
             'cet_cyclic_mybm_20_100_c48',  'cet_cyclic_mybm_20_100_c48_s25',
             'cet_cyclic_mygbm_30_95_c78',  'cet_cyclic_mygbm_30_95_c78_s25', 
             'cet_cyclic_mygbm_50_90_c46',  'cet_cyclic_mygbm_50_90_c46_s25',
             'cet_cyclic_protanopic_deuteranopic_bwyk_16_96_c31',  
             'cet_cyclic_protanopic_deuteranopic_wywb_55_96_c33',   
             'cet_cyclic_tritanopic_cwrk_40_100_c20', 
             'cet_cyclic_tritanopic_wrwc_70_100_c20',  
             'cet_cyclic_wrkbw_10_90_c43',  'cet_cyclic_wrkbw_10_90_c43_s25', 
             'cet_cyclic_wrwbw_40_90_c42',  'cet_cyclic_wrwbw_40_90_c42_s25',  
             'cet_cyclic_ymcgy_60_90_c67',  'cet_cyclic_ymcgy_60_90_c67_s25',  
             'cet_dimgray',  'cet_diverging_bkr_55_10_c35',  'cet_diverging_bky_60_10_c30',
             'cet_diverging_bwg_20_95_c41',  'cet_diverging_bwr_20_95_c54', 
             'cet_diverging_bwr_40_95_c42',  'cet_diverging_bwr_55_98_c37', 
             'cet_diverging_cwm_80_100_c22',  'cet_diverging_gkr_60_10_c40',
             'cet_diverging_gwr_55_95_c38',  'cet_diverging_gwv_55_95_c39', 
             'cet_diverging_isoluminant_cjm_75_c23',  'cet_diverging_isoluminant_cjm_75_c24', 
             'cet_diverging_isoluminant_cjo_70_c25',  
             'cet_diverging_linear_bjr_30_55_c53',  'cet_diverging_linear_bjy_30_90_c45', 
             'cet_diverging_linear_protanopic_deuteranopic_bjy_57_89_c34',
             'cet_diverging_protanopic_deuteranopic_bwy_60_95_c32',
             'cet_diverging_tritanopic_cwr_75_98_c20',  'cet_fire',  'cet_glasbey', 'cet_glasbey_bw', 
             'cet_glasbey_bw_minc_20', 'cet_glasbey_bw_minc_20_hue_150_280',  'cet_glasbey_bw_minc_20_hue_330_100',
             'cet_glasbey_bw_minc_20_maxl_70',  'cet_glasbey_bw_minc_20_minl_30',
             'cet_glasbey_category10', 
             'cet_glasbey_cool',  'cet_glasbey_dark',  'cet_glasbey_hv',  'cet_glasbey_light',
             'cet_glasbey_warm',  'cet_gouldian',  'cet_gray', 
             'cet_gwv',  'cet_isolum',  'cet_isoluminant_cgo_70_c39',  'cet_isoluminant_cgo_80_c38', 
             'cet_isoluminant_cm_70_c39',  'cet_kb',  'cet_kbc',  'cet_kbgyw', 
             'cet_kg',  'cet_kgy',  'cet_kr',  'cet_linear_bgy_10_95_c74', 
             'cet_linear_bgyw_15_100_c67',  'cet_linear_bgyw_15_100_c68',  'cet_linear_bgyw_20_98_c66',
             'cet_linear_blue_5_95_c73',  'cet_linear_blue_95_50_c20',  
             'cet_linear_bmw_5_95_c86',  'cet_linear_bmw_5_95_c89',  'cet_linear_bmy_10_95_c71', 
             'cet_linear_bmy_10_95_c78',  'cet_linear_gow_60_85_c27',  
             'cet_linear_gow_65_90_c35',  'cet_linear_green_5_95_c69',  'cet_linear_grey_0_100_c0', 
             'cet_linear_grey_10_95_c0',  'cet_linear_kbc_5_95_c73',  
             'cet_linear_kbgoy_20_95_c57',  'cet_linear_kbgyw_10_98_c63',  'cet_linear_kbgyw_5_98_c62',
             'cet_linear_kgy_5_95_c69',  'cet_linear_kry_0_97_c73',  
             'cet_linear_kry_5_95_c72',  'cet_linear_kry_5_98_c75',  'cet_linear_kryw_0_100_c71', 
             'cet_linear_kryw_5_100_c64',  'cet_linear_kryw_5_100_c67', 
             'cet_linear_protanopic_deuteranopic_kbjyw_5_95_c25',  
             'cet_linear_protanopic_deuteranopic_kbw_5_95_c34',  'cet_linear_protanopic_deuteranopic_kbw_5_98_c40', 
             'cet_linear_protanopic_deuteranopic_kyw_5_95_c49', 
             'cet_linear_ternary_blue_0_44_c57',  'cet_linear_ternary_green_0_46_c42',  
             'cet_linear_tritanopic_kcw_5_95_c22', 
             'cet_linear_tritanopic_krjcw_5_95_c24',  'cet_linear_tritanopic_krjcw_5_98_c46', 
             'cet_linear_tritanopic_krw_5_95_c46',  'cet_linear_wcmr_100_45_c42',
             'cet_linear_worb_100_25_c53',  'cet_linear_wyor_100_45_c55', 
             'cividis',  'cool', 
             'coolwarm',  'copper',  'crest',  'cubehelix',  'flag',  'flare',  
             'gist_earth',  'gist_gray',  'gist_heat',  'gist_ncar',   
             'gist_stern',  'gist_yarg',  'gnuplot', 'gnuplot2',   'gray',  'hot',  'hsv', 
             'icefire',  'inferno',  'jet',  'magma',  'mako',  'nipy_spectral',  
             'ocean',  'pink',  'plasma',  'prism',  'rainbow',  'rocket',  'seismic', 
             'spring',  'summer',  'tab10',  'tab20',  'tab20b',  'tab20c',  'terrain',  
             'turbo',  'twilight',  'twilight_shifted',  'viridis',  'vlag',  'winter']


# Widgets e Funções

datei = datetime.strptime('2019-11-15', '%Y-%m-%d')
datef = datetime.strptime('2019-11-26', '%Y-%m-%d')

date = pn.widgets.DateSlider(name='Data', start=datei, end=datef, value=datei, format='%Y-%m-%d')
       
# Widgets Série Temporal (_st)
varlev_st = pn.widgets.Select(name='Variável', value=[i[0] for i in Vars][0], options=[i[0] for i in Vars])
reg_st = pn.widgets.Select(name='Região', value=Regs[0], options=Regs)
ref_st = pn.widgets.Select(name='Referência', value=Refs[0], options=Refs)
expt_st = pn.widgets.MultiChoice(name='Experimentos', value=[Exps[0]], options=Exps, solid=False)

# Widgets Scorecard (_sc)
Tstats = ['Ganho Percentual', 'Mudança Fracional']
colormap_sc = pn.widgets.Select(name='Cor do Preenchimento', value=colormaps[269], options=colormaps)
invert_colors_sc = pn.widgets.Checkbox(name='Inverter Cores', value=True)
statt_sc = pn.widgets.Select(name='Estatística', value=StatsT[2], options=StatsT)
tstat = pn.widgets.Select(name='Tipo', value=Tstats[1], options=Tstats)
reg_sc = pn.widgets.Select(name='Região', value=Regs[0], options=Regs)
ref_sc = pn.widgets.Select(name='Referência', value=Refs[0], options=Refs)
expt1 = pn.widgets.Select(name='Experimento 1', value=Exps[0], options=Exps)
expt2 = pn.widgets.Select(name='Experimento 2', value=Exps[1], options=Exps)

# Widgets Distribuição Espacial (_de) 
Fills = ['image', 'contour']
fill_de = pn.widgets.Select(name='Preenchimento', value=Fills[0], options=Fills)     
state = pn.widgets.Select(name='Estatística', value=StatsE[0], options=StatsE)    
varlev_de = pn.widgets.Select(name='Variável', value=[i[0] for i in Vars][0], options=[i[0] for i in Vars])    
reg_de = pn.widgets.Select(name='Região', value=Regs[0], options=Regs)    
ref_de = pn.widgets.Select(name='Referência', value=Refs[0], options=Refs)    
colormap_de = pn.widgets.Select(name='Cor do Preenchimento', value=colormaps[275], options=colormaps)      
invert_colors_de = pn.widgets.Checkbox(name='Inverter Cores', value=True) 
interval = pn.widgets.IntInput(name='Intervalos', value=10, step=1, start=5, end=20)        
expe_de = pn.widgets.MultiChoice(name='Experimentos', value=[Exps[0]], options=Exps, solid=False)    
      
# Widgets Distribuição Espacial Double (_ded) 
fill_ded = pn.widgets.Select(name='Preenchimento', value=Fills[0], options=Fills)     
varlev_ded = pn.widgets.Select(name='Variável', value=[i[0] for i in Vars][0], options=[i[0] for i in Vars])    
reg_ded = pn.widgets.Select(name='Região', value=Regs[0], options=Regs)    
ref_ded = pn.widgets.Select(name='Referência', value=Refs[0], options=Refs)    
colormap_ded = pn.widgets.Select(name='Cor do Preenchimento', value=colormaps[275], options=colormaps)      
invert_colors_ded = pn.widgets.Checkbox(name='Inverter Cores', value=True) 
expe_ded = pn.widgets.MultiChoice(name='Experimentos', value=[Exps[0]], options=Exps, solid=False)  
swipe_ded = pn.widgets.Checkbox(name='Juntar Figuras', value=False) 
show_diff_ded = pn.widgets.Checkbox(name='Mostrar Diferença', value=False) 
exp1_ded = pn.widgets.Select(name='Experimento 1', value=Exps[0], options=Exps)
exp2_ded = pn.widgets.Select(name='Experimento 2', value=Exps[1], options=Exps)

#######

def get_min_max_ds(ds):
    return ds.compute().min().item(), ds.compute().max().item()

def get_df(reg, exp, stat, ref, varlev):
    kname = 'scantec_' + reg + '_' + stat + '_' + exp.lower() + '-' + ref + '-table'
    df = ds_catalog[kname].read()
    df.set_index('Unnamed: 0', inplace=True)
    df.index.name = '' 
    return df

#######

@pn.depends(varlev_st, reg_st, ref_st, expt_st)
def plotCurves(varlev_st, reg_st, ref_st, expt_st):
        
    for i in Vars:
        if i[0] == varlev_st:
            nexp_ext = i[1]

    varlev_st = varlev_st.lower()

    height=500    
        
    for count, i in enumerate(expt_st):
        if count == 0:
            exp = expt_st[count] 
            
            df_vies = get_df(reg_st, exp, 'vies', ref_st, varlev_st)
            
            ax_vies = df_vies.hvplot.line(x='%Previsao',
                                          y=varlev_st,
                                          xlabel='Horas',
                                          ylabel='VIES',
                                          shared_axes=False,
                                          grid=True,
                                          line_width=3,
                                          label=str(exp),
                                          fontsize={'ylabel': '12px', 'ticks': 10},
                                          responsive=True,
                                          height=height,
                                          title='VIES' + ' - ' + str(nexp_ext))
            
            df_rmse = get_df(reg_st, exp, 'rmse', ref_st, varlev_st)
        
            ax_rmse = df_rmse.hvplot.line(x='%Previsao',
                                          y=varlev_st,
                                          xlabel='Horas',
                                          ylabel='RMSE',
                                          shared_axes=False,
                                          grid=True,
                                          line_width=3,
                                          label=str(exp),
                                          fontsize={'ylabel': '12px', 'ticks': 10},
                                          responsive=True,
                                          height=height,
                                          title='RMSE' + ' - ' + str(nexp_ext))            
                        
            df_acor = get_df(reg_st, exp, 'acor', ref_st, varlev_st)
            
            ax_acor = df_acor.hvplot.line(x='%Previsao', 
                                          y=varlev_st,
                                          xlabel='Horas',
                                          ylabel='ACOR',
                                          shared_axes=False,
                                          grid=True,
                                          line_width=3,
                                          label=str(exp),
                                          fontsize={'ylabel': '12px', 'ticks': 10},     
                                          responsive=True,
                                          height=height,
                                          title='ACOR' + ' - ' + str(nexp_ext))  
            
        else:
            
            exp = expt_st[count]
            
            df_vies = get_df(reg_st, exp, 'vies', ref_st, varlev_st)
            
            ax_vies *= df_vies.hvplot.line(x='%Previsao', 
                                           y=varlev_st, 
                                           xlabel='Horas', 
                                           ylabel='VIES',
                                           shared_axes=False,
                                           grid=True,
                                           line_width=3,
                                           label=str(exp),  
                                           fontsize={'ylabel': '12px', 'ticks': 10},
                                           responsive=True,
                                           height=height,
                                           title='VIES' + ' - ' + str(nexp_ext))
            
            df_rmse = get_df(reg_st, exp, 'rmse', ref_st, varlev_st)
            
            ax_rmse *= df_rmse.hvplot.line(x='%Previsao',
                                           y=varlev_st,
                                           xlabel='Horas',
                                           ylabel='RMSE', 
                                           shared_axes=False,
                                           grid=True,
                                           line_width=3,
                                           label=str(exp), 
                                           fontsize={'ylabel': '12px', 'ticks': 10},
                                           responsive=True,
                                           height=height,
                                           title='RMSE' + ' - ' + str(nexp_ext))       

            df_acor = get_df(reg_st, exp, 'acor', ref_st, varlev_st)
            
            ax_acor *= df_acor.hvplot.line(x='%Previsao',
                                           y=varlev_st,
                                           xlabel='Horas',
                                           ylabel='ACOR', 
                                           shared_axes=False,
                                           grid=True,
                                           line_width=3,
                                           label=str(exp),      
                                           fontsize={'ylabel': '12px', 'ticks': 10},
                                           responsive=True,
                                           height=height,
                                           title='ACOR' + ' - ' + str(nexp_ext))             
       
        ax_vies *= hvs.HLine(0).opts(line_width=1, shared_axes=False, responsive=True, height=height, line_color='black', line_dash='dashed')
        ax_rmse *= hvs.HLine(0).opts(line_width=1, shared_axes=False, responsive=True, height=height, line_color='black', line_dash='dashed')
        ax_acor *= hvs.HLine(0.6).opts(line_width=1, shared_axes=False, responsive=True, height=height, line_color='black', line_dash='dashed')    
            
    ax_vies.opts(axiswise=True, legend_position='bottom_left')
    ax_rmse.opts(axiswise=True, legend_position='top_left')
    ax_acor.opts(axiswise=True, legend_position='bottom_left')
            
    return hvs.Layout(ax_vies + ax_rmse + ax_acor).cols(3)
    
#######

@pn.depends(statt_sc, tstat, reg_sc, ref_sc, expt1, expt2, colormap_sc, invert_colors_sc)    
def plotScorecard(statt_sc, tstat, reg_sc, ref_sc, expt1, expt2, colormap_sc, invert_colors_sc):  
    
    dfs = globals()['ds_catalog']
    
    kname1 = 'scantec_' + reg_sc + '_' + statt_sc.lower() + '_' + expt1.lower() + '-' + ref_sc + '-table'
    kname2 = 'scantec_' + reg_sc + '_' + statt_sc.lower() + '_' + expt2.lower() + '-' + ref_sc + '-table'
    
    df1 = dfs[kname1].read()
    df2 = dfs[kname2].read()
        
    df1.set_index('Unnamed: 0', inplace=True)
    df1.index.name = ''   

    df2.set_index('Unnamed: 0', inplace=True)
    df2.index.name = ''      
        
    p_table1 = pd.pivot_table(df1, index='%Previsao', values=list_var)
    p_table2 = pd.pivot_table(df2, index='%Previsao', values=list_var)
 
    if invert_colors_sc == True:
        cmap = colormap_sc + '_r'
    else:
        cmap = colormap_sc
    
    if tstat == 'Ganho Percentual':
        # Porcentagem de ganho
        if statt_sc == 'ACOR':
            score_table = ((p_table2.T - p_table1.T) / (1.0 - p_table1.T)) * 100
        elif statt_sc == 'RMSE' or statt_sc == 'VIES':
            score_table = ((p_table2.T - p_table1.T) / (0.0 - p_table1.T)) * 100
    elif tstat == 'Mudança Fracional':
        # Mudança fracional
        score_table = (1.0 - (p_table2.T / p_table1.T))
 
    if score_table.isnull().values.any():
        # Tentativa de substituir os NaN - que aparecem quando vies e rmse são iguais a zero
        score_table = score_table.fillna(0.0000001)
    
        # Tentativa de substituir valores -inf por um número não muito grande
        score_table.replace([np.inf, -np.inf], 1000000, inplace=True)
        
        pn.state.notifications.info('Valores como NaN ou Inf podem ter sido substituídos por outros valores.', duration=0)
    
    # Figura
    plt.figure(figsize = (8,5))
        
    sns.set(style='whitegrid', font_scale=0.450)
    sns.set_context(rc={'xtick.major.size':  1.5,  'ytick.major.size': 1.5,
                        'xtick.major.pad':   0.05,  'ytick.major.pad': 0.05,
                        'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
                        'xtick.minor.size':  1.5,  'ytick.minor.size': 1.5,
                        'xtick.minor.pad':   0.05,  'ytick.minor.pad': 0.05,
                        'xtick.minor.width': 0.5, 'ytick.minor.width': 0.5})
 
    if tstat == 'Ganho Percentual':
        ax = sns.heatmap(score_table, annot=True, fmt='.6f', cmap=cmap, 
                         vmin=-100, vmax=100, center=0, linewidths=0.25, square=False,
                         cbar_kws={'shrink': 1.0, 
                                   'ticks': np.arange(-100,110,10),
                                   'pad': 0.01,
                                   'orientation': 'vertical'})
 
        cbar = ax.collections[0].colorbar
        cbar.set_ticks([-100, -50, 0, 50, 100])
        cbar.set_ticklabels(['pior', '-50%', '0', '50%', 'melhor'])
        cbar.ax.tick_params(labelsize=8)    

        plt.title('Ganho ' + str(statt_sc) + ' (%) - ' + expt1 + ' Vs. ' + expt2, fontsize=8)
 
    elif tstat == 'Mudança Fracional':
        ax = sns.heatmap(score_table, annot=True, fmt='.6f', cmap=cmap, 
                         vmin=-1, vmax=1, center=0, linewidths=0.25, square=False,
                         cbar_kws={'shrink': 1.0, 
                                   'ticks': np.arange(-1,2,1),
                                   'pad': 0.01,
                                   'orientation': 'vertical'})
 
        cbar = ax.collections[0].colorbar
        cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
        cbar.set_ticklabels(['pior', '-0.5', '0', '0.5', 'melhor'])
        cbar.ax.tick_params(labelsize=8)    
 
        plt.title('Mudança Fracional ' + str(statt_sc) + " - " + expt1 + ' Vs. ' + expt2, fontsize=8)
   
    plt.xlabel('Horas de Integração')
    plt.yticks(fontsize=8)
    plt.xticks(rotation=90, fontsize=8)    
    plt.tight_layout()        

    fig = ax.get_figure()
    
    plt.close()

    return fig

#######
     
@pn.depends(state, varlev_de, reg_de, ref_de, date, colormap_de, invert_colors_de, interval, expe_de, fill_de)
def plotFields(state, varlev_de, reg_de, ref_de, date, colormap_de, invert_colors_de, interval, expe_de, fill_de):
    
    date = str(date) + ' 12:00' # consertar...

    var = varlev_de.replace(':', '').lower()
    
    for i in Vars:
        if i[0] == varlev_de:
            nexp_ext = i[1]
    
    if invert_colors_de == True:
        cmap = colormap_de + '_r'
    else:
        cmap = colormap_de
    
    if reg_de == 'as':
        data_aspect=1
        frame_height=650
    elif (reg_de == 'hn') or (reg_de == 'hs'):
        data_aspect=1
        frame_height=225        
    elif reg_de == 'tr':
        data_aspect=1
        frame_height=150         
    elif reg_de == 'gl': 
        data_aspect=1
        frame_height=590
  
    for count, i in enumerate(expe_de):
        if count == 0:
            exp = expe_de[count]
            kname = 'scantec_' + reg_de + '_' + state.lower() + '_' + exp.lower() + '-' + ref_de + '-field'
            ds = ds_catalog[kname].to_dask()
            
            vmin, vmax = get_min_max_ds(ds[var])
                       
            if fill_de == 'image':
            
                ax = ds.sel(time=date).hvplot.image(x='lon',
                                                    y='lat',
                                                    z=var,
                                                    data_aspect=data_aspect,
                                                    frame_height=frame_height, 
                                                    cmap=cmap, 
                                                    projection=ccrs.PlateCarree(), 
                                                    coastline=True,
                                                    rasterize=True,
                                                    clim=(vmin,vmax),
                                                    title=str(state) + ' - ' + str(nexp_ext) + ' (' + str(date) + ')')    
                
            elif fill_de == 'contour':
                
                ax = ds.sel(time=date).hvplot.contour(x='lon',
                                                      y='lat',
                                                      z=var,
                                                      data_aspect=data_aspect,
                                                      frame_height=frame_height, 
                                                      cmap=cmap, 
                                                      projection=ccrs.PlateCarree(), 
                                                      coastline=True,
                                                      rasterize=True,
                                                      clim=(vmin,vmax),
                                                      levels=interval,
                                                      line_width=2,
                                                      title=str(state) + ' - ' + str(nexp_ext) + ' (' + str(date) + ')')  
             
        else:  
            
            ax *= ds.sel(time=date).hvplot.contour(x='lon',
                                                   y='lat',
                                                   z=var,
                                                   data_aspect=data_aspect,
                                                   frame_height=frame_height, 
                                                   cmap=cmap, 
                                                   projection=ccrs.PlateCarree(), 
                                                   coastline=True,
                                                   clim=(vmin,vmax),
                                                   colorbar=True,
                                                   levels=interval,
                                                   line_width=4,
                                                   line_dash='dashed',
                                                   title=str(state) + ' - ' + str(nexp_ext) + ' (' + str(date) + ')') 
   
    return ax

########
    
@pn.depends(state, varlev_ded, reg_ded, ref_ded, date, colormap_ded, invert_colors_ded, interval, fill_ded, swipe_ded, show_diff_ded, exp1_ded, exp2_ded)
def plotFieldsDouble(state, varlev_ded, reg_ded, ref_ded, date, colormap_ded, invert_colors_ded, interval, fill_ded, swipe_ded, show_diff_ded, exp1_ded, exp2_ded):
    
    datefmt = str(date) + ' 12:00' # consertar...
    
    var = varlev_ded.replace(':', '').lower()
    
    for i in Vars:
        if i[0] == varlev_ded:
            nexp_ext = i[1]
    
    if invert_colors_ded == True:
        cmap = colormap_ded + '_r'
    else:
        cmap = colormap_ded
    
    if reg_ded == 'as':
        data_aspect=1
        frame_height=660
    elif (reg_ded == 'hn') or (reg_ded == 'hs'):
        data_aspect=1
        frame_height=235        
    elif reg_ded == 'tr':
        data_aspect=1
        frame_height=155         
    elif reg_ded == 'gl': 
        data_aspect=1
        frame_height=300
        frame_height=350
  
    exp1 = exp1_ded
    kname1 = 'scantec_' + reg_ded + '_' + state.lower() + '_' + exp1.lower() + '-' + ref_ded + '-field'
    ds1 = ds_catalog[kname1].to_dask()
 
    exp2 = exp2_ded
    kname2 = 'scantec_' + reg_ded + '_' + state.lower() + '_' + exp2.lower() + '-' + ref_ded + '-field'
    ds2 = ds_catalog[kname2].to_dask()
    
    vmin, vmax = get_min_max_ds(ds1[var])
               
    if show_diff_ded:
        
        if fill_ded == 'image':
        
            ax = (ds1.sel(time=datefmt) - ds2.sel(time=datefmt)).hvplot.image(x='lon',
                                                                              y='lat',
                                                                              z=var,
                                                                              data_aspect=data_aspect,
                                                                              frame_height=frame_height, 
                                                                              cmap=cmap, 
                                                                              projection=ccrs.PlateCarree(), 
                                                                              coastline=True,
                                                                              rasterize=True,
                                                                              colorbar=True,
                                                                              clim=(vmin,vmax),
                                                                              title=str(state) + ' - ' + 'Dif. (' + str(exp1) + '-' + str(exp2) + ') - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    
            
        elif fill_ded == 'contour':
                
            ax = (ds1.sel(time=datefmt) - ds2.sel(time=datefmt)).hvplot.contour(x='lon',
                                                                                y='lat',
                                                                                z=var,
                                                                                data_aspect=data_aspect,
                                                                                frame_height=frame_height, 
                                                                                cmap=cmap, 
                                                                                projection=ccrs.PlateCarree(), 
                                                                                coastline=True,
                                                                                rasterize=True,
                                                                                clim=(vmin,vmax),
                                                                                levels=interval,
                                                                                line_width=1,
                                                                                title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')          
    else:
        
        if fill_ded == 'image':
            
            ax1 = ds1.sel(time=datefmt).hvplot.image(x='lon',
                                                  y='lat',
                                                  z=var,
                                                  data_aspect=data_aspect,
                                                  frame_height=frame_height, 
                                                  cmap=cmap, 
                                                  projection=ccrs.PlateCarree(), 
                                                  coastline=True,
                                                  rasterize=True,
                                                  colorbar=True,
                                                  clim=(vmin,vmax),
                                                  title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    
        
            ax2 = ds2.sel(time=datefmt).hvplot.image(x='lon',
                                                  y='lat',
                                                  z=var,
                                                  data_aspect=data_aspect,
                                                  frame_height=frame_height, 
                                                  cmap=cmap, 
                                                  projection=ccrs.PlateCarree(), 
                                                  coastline=True,
                                                  rasterize=True,
                                                  colorbar=True,   
                                                  clim=(vmin,vmax),
                                                  title=str(state) + ' - ' + str(exp2) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')       
            
        elif fill_ded == 'contour':
                
            ax1 = ds1.sel(time=datefmt).hvplot.contour(x='lon',
                                                    y='lat',
                                                    z=var,
                                                    data_aspect=data_aspect,
                                                    frame_height=frame_height, 
                                                    cmap=cmap, 
                                                    projection=ccrs.PlateCarree(), 
                                                    coastline=True,
                                                    rasterize=True,
                                                    clim=(vmin,vmax),
                                                    levels=interval,
                                                    line_width=1,
                                                    title=str(state) + ' - ' + str(exp1) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')    
             
            ax2 = ds2.sel(time=datefmt).hvplot.contour(x='lon',
                                                    y='lat',
                                                    z=var,
                                                    data_aspect=data_aspect,
                                                    frame_height=frame_height, 
                                                    cmap=cmap, 
                                                    projection=ccrs.PlateCarree(), 
                                                    coastline=True,
                                                    rasterize=True,
                                                    clim=(vmin,vmax),
                                                    levels=interval,
                                                    line_width=1,
                                                    title=str(state) + ' - ' + str(exp2) + ' - ' + str(nexp_ext) + ' (' + str(datefmt) + ')')  

    if show_diff_ded:    
        layout = pn.Column(ax, sizing_mode='stretch_width')
    else:
        if swipe_ded:
            layout = pn.Swipe(ax1, ax2, value=5)
        else:
            if reg_ded == 'as':# or reg_ded == 'gl':
                layout = hvs.Layout(ax1 + ax2).cols(2)
            else:
                layout = hvs.Layout(ax1 + ax2).cols(1)
     
    pn.state.notifications.info('As cores nos gráficos podem representar intervalos de valores.', duration=0)
    
    return layout
    
#######

@pn.depends(state, varlev_de, reg_de, ref_de, date, expt1)
def plotSeriesFromField(state, varlev_de, reg_de, ref_de, date, expt1):

    var = varlev_de.replace(':', '').lower()
    
    kname = 'scantec_' + reg_de + '_' + state.lower() + '_' + expt1.lower() + '-' + ref_de + '-field'
    dsv = ds_catalog['scantec_gl_rmse_exp18-ref_era5_no_clim-field'].to_dask()

    source = dsv.isel(time=0).hvplot.image(x='lon',
                                           y='lat',
                                           z=var,
                                           geo=True,
                                           projection=ccrs.PlateCarree(),
                                           title=str(state) + ' - ' + str(expt1) + ' (' + str(date) + ')')
    
    map_file = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    map_overlay = map_file.hvplot(geo=True, projection=ccrs.PlateCarree(), alpha=0.1)
    
    stream = hvs.streams.Tap(source=source, x=-88 + 360, y=40)
    
    def create_timeseries(x, y):
        ds_sel = dsv.sel(lon=x, lat=y, method='nearest')
        return hvs.Curve(ds_sel, ['time'], [var])
    
    target = hvs.DynamicMap(create_timeseries, streams=[stream]).opts(framewise=True, height=380, responsive=True)#, min_width=700)
    
    return pn.Row(source * map_overlay + target, sizing_mode='stretch_width')
    
#######

# Mensagens

text_gen_info = """
# SCANPLOT

SCANPLOT - Um sistema de visualização simples para o SCANTEC.

## Experimentos:

* **EXP18**: análises e previsões do experimento com o SMNA em coordenada híbrida na resolução TQ0299L064;
* **X666**: análises e previsões do modelo BAM em coordenada híbrida na resolução TQ0666L064.

## Validade:

Os experimentos foram considerados para o período de 2023021612 a 2023030312.

## Avaliação:

O SCANTEC foi utilizado para a avaliação objetiva dos experimentos com os seguintes ajustes:

* Interpolação de todos os campos atmosféricos para a resolução 0,4 graus (lat/lon);
* Utilização das seguintes referências:
    * `ref_era5_no_clim`: utilização das reanálises do Era5 como referência e considerando a média temporal desta referência como climatologia para o cálculo do Coeficiente de Correlação de Anomalias;
    * `ref_era5_no_clim`: utilização das próprias análises dos experimentos como referência e considerando a média temporal desta referência como climatologia para o cálculo do Coeficiente de Correlação de Anomalias;
    * `ref_era5_cfsr_clim` utilização das próprias análses dos experimentos como referência e utilização da reanálise do CFSR como climatologia para o cálculo do Coeficiente de Correlação de Anomalias;
    * `ref_era5_agcm_clim` utilização das próprias análses dos experimentos como referência e utilização da climatologia do antigo MCGA para o cálculo do Coeficiente de Correlação de Anomalias. 

---

Atualizado em: 29/06/2023 ([carlos.bastarz@inpe.br](mailto:carlos.bastarz@inpe.br))
"""

text_vies1 = """
# Viés 

Para uma variável _alpha_ (e.g., pressão, temperatura, umidade, componentes do vento etc.), discretizada em uma grade de _N_ pontos (com dimensões _i_ e _j_ - longitude e latitude, respectivamente, onde _N_ = _i_ x _j_), o Viés é calculado de acordo com a equação a seguir:
"""

text_vies2 = """
onde,

* 
* 
* 
"""

text_rmse1 = """
# Raiz do Erro Quadrático Médio

Para uma variável _alpha_ (e.g., pressão, temperatura, umidade, componentes do vento etc.), discretizada em uma grade de _N_ pontos (com dimensões _i_ e _j_ - longitude e latitude, respectivamente, onde _N_ = _i_ x _j_), a Raiz do Erro Quadrático Médio é calculada de acordo com a equação a seguir:
"""

text_rmse2 = """
onde,

* 
* 
* 
"""

text_acor1 = """
# Coeficiente de Correlação de Anomalias

O Coeficiente de Correlação de Anomalias é calculado de acordo com a equação a seguir:
"""

text_acor2 = """
onde,

* 
* 
* 
"""

text_scor1 ="""
# Scorecard

Para uma variável alpha (e.g., pressão, temperatura, umidade, componentes do vento etc.), podem ser calculadas duas métricas que permitem quantificar a variação relativa entre dois experimentos avaliados pelo SCANTEC. As métricas aplicadas são o Ganho Percentual e a Mudança Fracional* e ambas podem ser calculadas com base nas tabelas de estatisticas do SCANTEC. Estas métricas podem ser utilizadas quando se quiser ter uma visão imediata sobre as melhorias obtidas entre duas versões de um modelo ou entre dois experimentos de um mesmo modelo.

O Ganho Percentual é definido por:
"""

text_scor2 ="""
onde,

* E1: tabelas do experimento 1;
* E2: tabelas do experimento 2;
* EP: experimento 'perfeito' (valor considerado quando o experimento é perfeito, ie., 0 quando Viés ou RMSE e 1 quando ACOR).

A Mudança Fracional é definida por:
"""

text_scor3 ="""
onde,

* E1: tabelas do experimento 1;
* E2: tabelas do experimento 2;
* EP: experimento 'perfeito' (valor considerado quando o experimento é perfeito, ie., 0 quando Viés ou RMSE e 1 quando ACOR).

---
*[BAÑOS, I. H.](http://lattes.cnpq.br/6820161737155390); et al. **Impacto da Assimilação de Perfis de Refratividade do  Satélite Metop-B nas Previsões de Tempo do CPTEC/INPE Durante os Meses de Janeiro e Agosto de 2014.** Disponível em [link](https://www.scielo.br/scielo.php?script=sci_arttext&pid=S0102-77862018000100065).
"""  

eq_ganho = pn.pane.Markdown(r'$$GP(\alpha) = \frac{E2 - E1}{EP - E1} \times 100$$')
eq_mf = pn.pane.Markdown(r'$$MF(\alpha) = 1 - \frac{E2}{E1}$$')
eq_vies = pn.pane.Markdown(r'$$REQM(\alpha) = \frac{1}{N}\sum_{n=1}^{N}\bigg[ \frac{1}{I \cdot J}\sum_{i=1}^{I}\sum_{j=1}^{J}(\alpha_{i,j,n}^{P} - \alpha_{i,j,n}^{O})^{2} \bigg]^\frac{1}{2}$$')
eq_rmse = pn.pane.Markdown(r'$$REQM(\alpha) = \frac{1}{N}\sum_{n=1}^{N}\bigg[ \frac{1}{I \cdot J}\sum_{i=1}^{I}\sum_{j=1}^{J}(\alpha_{i,j,n}^{P} - \alpha_{i,j,n}^{O})^{2} \bigg]^\frac{1}{2}$$')
eq_cca = pn.pane.Markdown(r'$$CCA(\alpha) = \frac{\sum\limits_{i=1}^{I}\sum\limits_{j=1}^{J}\big[ (\alpha_{i,j}^{P} - \alpha_{i,j}^{C})\cdot(\alpha_{i,j}^{A} - \alpha_{i,j}^{C}) \big]}{\bigg \lbrace \bigg[ \sum\limits_{i=1}^{I}\sum\limits_{j=1}^{J}(\alpha_{i,j}^{P} - \alpha_{i,j}^{C})^2 \bigg] \bigg[ \sum\limits_{i=1}^{I}\sum\limits_{j=1}^{J}(\alpha_{i,j}^{A} - \alpha_{i,j}^{C})^2 \bigg] \bigg \rbrace ^\frac{1}{2}}$$')

text_st = """
# Série Temporal

A avaliação por meio de série temporal permite verificar o comportamento de parâmetros (variáveis) do modelo ao longo do tempo, seja por meio da verificação dos erros aleatórios, sistemáticos e habilidade de previsão.
"""

text_sc = """
# Scorecard

A avaliação por meio de scorecards permite obter uma visão geral do comportamento de parâmetros (variáveis) do modelo ao longo do tempo.
"""

text_ded = """
# Distribuição Espacial

A avaliação por meio da distribuição espacial permite verificar o comportamento de parêmetros (variáveis) do modelo ao longo do tempo, seja por meio da verificação dos erros aleatórios, sistemáticos e habilidade de previsão.
"""

text_help = """
# Ajuda

Clique sobre as abas `Série Temporal`, `Scorecard` ou `Distribuição Espacial` para acessar as opções de plotagem e visualização das estatísticas calculadas.
Cada tipo de visualização possui opções diferentes e independentes para a realização das plotagens. Utilize as opções para fazer os ajustes necessários.
"""

welcomeText = """
# Bem-vindo!

Este é o SCANPLOT - Um sistema simples de plotagem para o SCANTEC. O SCANTEC - Sistema Comunitário de Avaliação de modelos Numéricos de Tempo E Clima, é um sistema desenvolvido
para a avaliação de modelos numéricos de previsão e clima em uso no CPTEC - Centro de Previsão de Tempo e Estudos Climáticos. O SCANPLOT foi desenvolvido para uso exclusivo com 
o SCANTEC, devido as suas particularidades de desenvolvimento e aplicação.
"""

text_fu = """
# Selecionar catálogo

Clique no botão `Escolher arquivo...` e selecione o arquivo de catálogo `.yml` com os resultados da avaliação realizada pelo SCANTEC.
"""

text_float_panel = """
# SCANPLOT V2.0.0a1

SCANPLOT - Um sistema de visualização simples para o SCANTEC.

---

CPTEC-INPE, 2023.
"""

# Dashboard 

scantec_logo = 'https://raw.githubusercontent.com/GAM-DIMNT-CPTEC/SCANPLOT/8fe1c419bcb4881a78a3b1ac83673bcd229b075d/img/logo_scantec.png'
inpe_logo = 'https://raw.githubusercontent.com/GAM-DIMNT-CPTEC/SCANPLOT/8fe1c419bcb4881a78a3b1ac83673bcd229b075d/img/logo_inpe.png'

template = pn.template.BootstrapTemplate(title = 'SCANPLOT', logo = scantec_logo)

scantec_logo = pn.pane.PNG(scantec_logo, width=200)
inpe_logo = pn.pane.PNG(inpe_logo, width=200)

config = {'headerControls': 
          {#'minimize': 'remove', 
           'maximize': 'remove', 
           #'normalize': 'remove', 
           'smallify': 'remove'}
         }

float_panel = pn.layout.FloatPanel(
    pn.Tabs(('Sobre',
    pn.Row(text_float_panel, scantec_logo)),
           ('Reportar Bugs', 'Encontrou um bug? Abra uma issue no [GitHub do projeto](https://github.com/GAM-DIMNT-CPTEC/SCANPLOT/issues) ou envie um email para [carlos.bastarz@inpe.br](mailto:carlos.bastarz@inpe.br).'),
           ('Contribuir', 'Quer contribuir com o desenvolvimento do SCANPLOT? Envie um email para [carlos.bastarz@inpe.br](mailto:carlos.bastarz@inpe.br).'),
           ), 
    name='SCANPLOT', 
    contained=False, 
    position='center', 
    margin=20, 
    config=config)

col_pallete1 = pn.pane.PNG('/extra2/SCANTEC_EGEON/SCANTEC-2.1.0/dataout/periodo/jupyter/img/cp_uniform_sequential.png', width=1000)
col_pallete2 = pn.pane.PNG('/extra2/SCANTEC_EGEON/SCANTEC-2.1.0/dataout/periodo/jupyter/img/cp_diverging.png', width=1000)
col_pallete3 = pn.pane.PNG('/extra2/SCANTEC_EGEON/SCANTEC-2.1.0/dataout/periodo/jupyter/img/cp_rainbow.png', width=1000)
col_pallete4 = pn.pane.PNG('/extra2/SCANTEC_EGEON/SCANTEC-2.1.0/dataout/periodo/jupyter/img/cp_categorical.png', width=1000)
col_pallete5 = pn.pane.PNG('/extra2/SCANTEC_EGEON/SCANTEC-2.1.0/dataout/periodo/jupyter/img/cp_mono_sequential.png', width=1000)
col_pallete6 = pn.pane.PNG('/extra2/SCANTEC_EGEON/SCANTEC-2.1.0/dataout/periodo/jupyter/img/cp_other_sequential.png', width=1000)
col_pallete7 = pn.pane.PNG('/extra2/SCANTEC_EGEON/SCANTEC-2.1.0/dataout/periodo/jupyter/img/cp_miscellaneous.png', width=1000)

color_palletes_tabs = pn.Tabs(('Uniform Sequential', col_pallete1), 
                              ('Diverging', col_pallete2),
                              ('Rainbow', col_pallete3),
                              ('Categorical', col_pallete4),
                              ('Mono Sequential', col_pallete5),
                              ('Other Sequential', col_pallete6),
                              #('Miscellaneous', col_pallete7),
                             )

show_color_pallete = pn.widgets.Button(name='🎨 Paletas de Cores...', button_type='default')

modal_btn = pn.widgets.Button(name='📖 Informações Gerais', button_type='primary')
modal_btn_st = pn.widgets.Button(name='📊 Sobre', button_type='success')
modal_btn_sc = pn.widgets.Button(name='📊 Sobre', button_type='success')
modal_btn_ded = pn.widgets.Button(name='📊 Sobre', button_type='success')
modal_help = pn.widgets.Button(name='☝🏼 Ajuda', button_type='primary')

card_parameters_st = pn.Card(varlev_st, reg_st, ref_st, expt_st, modal_btn_st, title='Série Temporal', collapsed=False)
card_parameters_sc = pn.Card(statt_sc, tstat, reg_sc, ref_sc, expt1, expt2, pn.Column(colormap_sc, show_color_pallete), invert_colors_sc, modal_btn_sc, title='Scorecard', collapsed=False)
card_parameters_ded = pn.Card(state, varlev_ded, reg_ded, ref_ded, exp1_ded, exp2_ded, date, fill_ded, pn.Column(colormap_ded, show_color_pallete), invert_colors_ded, interval, swipe_ded, show_diff_ded, modal_btn_ded, title='Distribuição Espacial', collapsed=False)

template.modal.append(pn.Column())

tabs = pn.Tabs(dynamic=True, active=0)
tabs.append(('Série Temporal', plotCurves))
tabs.append(('Scorecard', plotScorecard))
tabs.append(('Distribuição Espacial', plotFieldsDouble))

# Atualiza o conteúdo da barra lateral de acordo com a aba ativa (utiliza o conteúdo da primeira aba no início)
#col = pn.Column(card_parameters_fu)
col = pn.Column(card_parameters_st)
text_info1 = pn.Column(text_gen_info)
text_info2 = pn.Column(text_st)

@pn.depends(tabs.param.active, watch=True)
def insert_widget(active_tab):
    if active_tab == 0: 
        col[0] = card_parameters_st
        text_info2[0] = text_st
    elif active_tab == 1: 
        col[0] = card_parameters_sc    
        text_info2[0] = text_sc
    elif active_tab == 2: 
        col[0] = card_parameters_ded
        text_info2[0] = text_ded
        
def show_modal_1(event):
    template.modal[0].clear()
    template.modal[0].append(text_info1)
    template.open_modal()

def show_modal_2(event):
    template.modal[0].clear()
    template.modal[0].append(text_info2)
    template.open_modal()    

modal_btn.on_click(show_modal_1)
modal_btn_st.on_click(show_modal_2)
modal_btn_sc.on_click(show_modal_2)
modal_btn_ded.on_click(show_modal_2)           
    
def show_modal_3(event):
    template.modal[0].clear()
    template.modal[0].append(pn.Column('# Paletas de Cores', 'Mais informações em <a href="https://holoviews.org/user_guide/Colormaps.html" target="_blank">Colormaps</a>.', color_palletes_tabs))
    template.open_modal()

def show_modal_4(event):
    template.modal[0].clear()
    template.modal[0].append(pn.Column(text_help))
    template.open_modal()    
    
show_color_pallete.on_click(show_modal_3)    
modal_help.on_click(show_modal_4)    
     
template.sidebar.append(col)
template.sidebar.append(modal_btn)
template.sidebar.append(modal_help)
template.main.append(pn.Column(
    tabs,    
    float_panel,
    pn.pane.Alert('⚠️ **Aviso:** As informações aqui apresentadas não representam informações oficiais e não podem ser utilizadas para a tomada de decisão.', alert_type='warning')
    )
)

template.servable();
