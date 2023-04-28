importScripts("https://cdn.jsdelivr.net/pyodide/v0.22.1/full/pyodide.js");

function sendPatch(patch, buffers, msg_id) {
  self.postMessage({
    type: 'patch',
    patch: patch,
    buffers: buffers
  })
}

async function startApplication() {
  console.log("Loading pyodide!");
  self.postMessage({type: 'status', msg: 'Loading pyodide'})
  self.pyodide = await loadPyodide();
  self.pyodide.globals.set("sendPatch", sendPatch);
  console.log("Loaded!");
  await self.pyodide.loadPackage("micropip");
  const env_spec = ['https://cdn.holoviz.org/panel/0.14.3/dist/wheels/bokeh-2.4.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/0.14.3/dist/wheels/panel-0.14.3-py3-none-any.whl', 'pyodide-http==0.1.0', 'holoviews>=1.15.4', 'hvplot', 'matplotlib', 'numpy', 'pandas']
  for (const pkg of env_spec) {
    let pkg_name;
    if (pkg.endsWith('.whl')) {
      pkg_name = pkg.split('/').slice(-1)[0].split('-')[0]
    } else {
      pkg_name = pkg
    }
    self.postMessage({type: 'status', msg: `Installing ${pkg_name}`})
    try {
      await self.pyodide.runPythonAsync(`
        import micropip
        await micropip.install('${pkg}');
      `);
    } catch(e) {
      console.log(e)
      self.postMessage({
	type: 'status',
	msg: `Error while installing ${pkg_name}`
      });
    }
  }
  console.log("Packages loaded!");
  self.postMessage({type: 'status', msg: 'Executing code'})
  const code = `
  
import asyncio

from panel.io.pyodide import init_doc, write_doc

init_doc()

#!/usr/bin/env python
# coding: utf-8

import os
import re
import numpy as np
import pandas as pd
import hvplot.pandas
import panel as pn
import pickle as pk

from datetime import datetime, timedelta
from matplotlib import pyplot as plt

pn.extension(sizing_mode="stretch_width")

#path = './pkl'

#dfs = pk.load(open(os.path.join(path,'jo_table_series.pkl'), 'rb'))
dfs = pk.load(open('jo_table_series.pkl', 'rb'))

df_dtc = dfs.df_dtc
df_bamh_T0 = dfs.df_bamh_T0
df_bamh_T4 = dfs.df_bamh_T4
df_bamh_GT4AT2 = dfs.df_bamh_GT4AT2

df_dtc.name = 'df_dtc'
df_bamh_T0.name = 'df_bamh_T0'
df_bamh_T4.name = 'df_bamh_T4'
df_bamh_GT4AT2.name = 'df_bamh_GT4AT2'

experiment_list = [df_dtc, df_bamh_T0, df_bamh_T4, df_bamh_GT4AT2]
variable_list = ['surface pressure', 'temperature', 'wind', 'moisture', 'gps', 'radiance'] 
synoptic_time_list = ['00Z', '06Z', '12Z', '18Z', '00Z e 12Z', '06Z e 18Z']
iter_fcost_list = ['OMF', 'OMF (1st INNER LOOP)', 'OMF (2nd INNER LOOP)', 'OMA (AFTER 1st OUTER LOOP)', 'OMA (1st INNER LOOP)', 'OMA (2nd INNER LOOP)', 'OMA (AFTER 2nd OUTER LOOP)']

experiment = pn.widgets.MultiChoice(name='Experimentos', value=[experiment_list[0].name], options=[i.name for i in experiment_list], solid=False)
variable = pn.widgets.Select(name='Variável', value=variable_list[0], options=variable_list)
synoptic_time = pn.widgets.RadioBoxGroup(name='Horário', options=synoptic_time_list, inline=False)
iter_fcost = pn.widgets.Select(name='Iteração', value=iter_fcost_list[0], options=iter_fcost_list)

height=250

@pn.depends(variable, experiment, synoptic_time, iter_fcost)
def plotNobs(variable, experiment, synoptic_time, iter_fcost):
    for count, i in enumerate(experiment):
        if count == 0:
            sdf = globals()[i]
            df = dfs.xs(sdf.name, axis=1)
            
            if synoptic_time == '00Z': time_fmt0 = '00:00:00'; time_fmt1 = '00:00:00'
            if synoptic_time == '06Z': time_fmt0 = '06:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z': time_fmt0 = '12:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '18Z': time_fmt0 = '18:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == '00Z e 12Z': time_fmt0 = '00:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '06Z e 18Z': time_fmt0 = '06:00:00'; time_fmt1 = '18:00:00'
    
            if synoptic_time == '00Z e 06Z': time_fmt0 = '00:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z e 18Z': time_fmt0 = '12:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == 'Tudo': time_fmt0 = '00:00:00'; time_fmt1 = '18:00:00'   
    
            if time_fmt0 == time_fmt1:
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').at_time(str(time_fmt0)).reset_index()
            else:                
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')
                
                if synoptic_time == '00Z e 12Z':
                    df_s = df_s.drop(df_s.at_time('06:00:00').index).reset_index()
                elif synoptic_time == '06Z e 18Z':    
                    df_s = df_s.drop(df_s.at_time('12:00:00').index).reset_index()
                
            xticks = len(df_s['Date'].values)    
                
            ax = df_s.hvplot.line(x='Date', y='Nobs', xlabel='Data', ylabel=str('Nobs'), xticks=xticks, rot=90, grid=True, label=str(i), line_width=3, height=height)
            
        else:
            
            sdf = globals()[i]
            df = dfs.xs(sdf.name, axis=1)
            
            if synoptic_time == '00Z': time_fmt0 = '00:00:00'; time_fmt1 = '00:00:00'
            if synoptic_time == '06Z': time_fmt0 = '06:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z': time_fmt0 = '12:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '18Z': time_fmt0 = '18:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == '00Z e 12Z': time_fmt0 = '00:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '06Z e 18Z': time_fmt0 = '06:00:00'; time_fmt1 = '18:00:00'
    
            if time_fmt0 == time_fmt1:
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').at_time(str(time_fmt0)).reset_index()
            else:                    
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')

                if synoptic_time == '00Z e 12Z':
                    df_s = df_s.drop(df_s.at_time('06:00:00').index).reset_index()
                elif synoptic_time == '06Z e 18Z':    
                    df_s = df_s.drop(df_s.at_time('12:00:00').index).reset_index()
                
            xticks = len(df_s['Date'].values)
            
            ax *= df_s.hvplot.line(x='Date', y='Nobs', xlabel='Data', ylabel=str('Nobs'), xticks=xticks, rot=90, grid=True, label=str(i), line_width=3, height=height)
            
    return ax

@pn.depends(variable, experiment, synoptic_time, iter_fcost)
def plotJo(variable, experiment, synoptic_time, iter_fcost):
    for count, i in enumerate(experiment):
        if count == 0:
            sdf = globals()[i]
            df = dfs.xs(sdf.name, axis=1)
            
            if synoptic_time == '00Z': time_fmt0 = '00:00:00'; time_fmt1 = '00:00:00'
            if synoptic_time == '06Z': time_fmt0 = '06:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z': time_fmt0 = '12:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '18Z': time_fmt0 = '18:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == '00Z e 12Z': time_fmt0 = '00:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '06Z e 18Z': time_fmt0 = '06:00:00'; time_fmt1 = '18:00:00'
    
            if synoptic_time == '00Z e 06Z': time_fmt0 = '00:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z e 18Z': time_fmt0 = '12:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == 'Tudo': time_fmt0 = '00:00:00'; time_fmt1 = '18:00:00'   
    
            if time_fmt0 == time_fmt1:
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').at_time(str(time_fmt0)).reset_index()
            else:                
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')
                
                if synoptic_time == '00Z e 12Z':
                    df_s = df_s.drop(df_s.at_time('06:00:00').index).reset_index()
                elif synoptic_time == '06Z e 18Z':    
                    df_s = df_s.drop(df_s.at_time('12:00:00').index).reset_index()
                
            xticks = len(df_s['Date'].values)    
                
            ax = df_s.hvplot.line(x='Date', y='Jo', xlabel='Data', ylabel=str('Jo'), xticks=xticks, rot=90, grid=True, label=str(i), line_width=3, height=height)
            
        else:
            
            sdf = globals()[i]
            df = dfs.xs(sdf.name, axis=1)
            
            if synoptic_time == '00Z': time_fmt0 = '00:00:00'; time_fmt1 = '00:00:00'
            if synoptic_time == '06Z': time_fmt0 = '06:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z': time_fmt0 = '12:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '18Z': time_fmt0 = '18:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == '00Z e 12Z': time_fmt0 = '00:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '06Z e 18Z': time_fmt0 = '06:00:00'; time_fmt1 = '18:00:00'
    
            if time_fmt0 == time_fmt1:
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').at_time(str(time_fmt0)).reset_index()
            else:                    
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')

                if synoptic_time == '00Z e 12Z':
                    df_s = df_s.drop(df_s.at_time('06:00:00').index).reset_index()
                elif synoptic_time == '06Z e 18Z':    
                    df_s = df_s.drop(df_s.at_time('12:00:00').index).reset_index()
                
            xticks = len(df_s['Date'].values)
            
            ax *= df_s.hvplot.line(x='Date', y='Jo', xlabel='Data', ylabel=str('Jo'), xticks=xticks, rot=90, grid=True, label=str(i), line_width=3, height=height)
            
    return ax

@pn.depends(variable, experiment, synoptic_time, iter_fcost)
def plotJon(variable, experiment, synoptic_time, iter_fcost):
    for count, i in enumerate(experiment):
        if count == 0:
            sdf = globals()[i]
            df = dfs.xs(sdf.name, axis=1)
            
            if synoptic_time == '00Z': time_fmt0 = '00:00:00'; time_fmt1 = '00:00:00'
            if synoptic_time == '06Z': time_fmt0 = '06:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z': time_fmt0 = '12:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '18Z': time_fmt0 = '18:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == '00Z e 12Z': time_fmt0 = '00:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '06Z e 18Z': time_fmt0 = '06:00:00'; time_fmt1 = '18:00:00'
    
            if synoptic_time == '00Z e 06Z': time_fmt0 = '00:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z e 18Z': time_fmt0 = '12:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == 'Tudo': time_fmt0 = '00:00:00'; time_fmt1 = '18:00:00'   
    
            if time_fmt0 == time_fmt1:
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').at_time(str(time_fmt0)).reset_index()
            else:                
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')
                
                if synoptic_time == '00Z e 12Z':
                    df_s = df_s.drop(df_s.at_time('06:00:00').index).reset_index()
                elif synoptic_time == '06Z e 18Z':    
                    df_s = df_s.drop(df_s.at_time('12:00:00').index).reset_index()
                
            xticks = len(df_s['Date'].values)    
                
            ax = df_s.hvplot.line(x='Date', y='Jo/n', xlabel='Data', ylabel=str('Jo/n'), xticks=xticks, rot=90, grid=True, label=str(i), line_width=3, height=height)
            
        else:
            
            sdf = globals()[i]
            df = dfs.xs(sdf.name, axis=1)
            
            if synoptic_time == '00Z': time_fmt0 = '00:00:00'; time_fmt1 = '00:00:00'
            if synoptic_time == '06Z': time_fmt0 = '06:00:00'; time_fmt1 = '06:00:00'
            if synoptic_time == '12Z': time_fmt0 = '12:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '18Z': time_fmt0 = '18:00:00'; time_fmt1 = '18:00:00'    
    
            if synoptic_time == '00Z e 12Z': time_fmt0 = '00:00:00'; time_fmt1 = '12:00:00'
            if synoptic_time == '06Z e 18Z': time_fmt0 = '06:00:00'; time_fmt1 = '18:00:00'
    
            if time_fmt0 == time_fmt1:
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').at_time(str(time_fmt0)).reset_index()
            else:                    
                df_s = df.loc[df['Observation Type'] == variable].loc[df['Iter'] == iter_fcost].set_index('Date').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')

                if synoptic_time == '00Z e 12Z':
                    df_s = df_s.drop(df_s.at_time('06:00:00').index).reset_index()
                elif synoptic_time == '06Z e 18Z':    
                    df_s = df_s.drop(df_s.at_time('12:00:00').index).reset_index()
                
            xticks = len(df_s['Date'].values)
            
            ax *= df_s.hvplot.line(x='Date', y='Jo/n', xlabel='Data', ylabel=str('Jo/n'), xticks=xticks, rot=90, grid=True, label=str(i), line_width=3, height=height)
            
    return ax

settings = pn.Row(pn.WidgetBox(variable, iter_fcost, synoptic_time, pn.Column(experiment, height=250)))
pn.Column(
    '### SMNA Dashboard', 
    settings,
    plotNobs,
    plotJo,
    plotJon,
    width_policy='max'
)

pn.template.FastListTemplate(
    site="SMNA", title="Dashboard", sidebar=[settings],
    main=[plotNobs, plotJo, plotJon]
).servable();


await write_doc()
  `

  try {
    const [docs_json, render_items, root_ids] = await self.pyodide.runPythonAsync(code)
    self.postMessage({
      type: 'render',
      docs_json: docs_json,
      render_items: render_items,
      root_ids: root_ids
    })
  } catch(e) {
    const traceback = `${e}`
    const tblines = traceback.split('\n')
    self.postMessage({
      type: 'status',
      msg: tblines[tblines.length-2]
    });
    throw e
  }
}

self.onmessage = async (event) => {
  const msg = event.data
  if (msg.type === 'rendered') {
    self.pyodide.runPythonAsync(`
    from panel.io.state import state
    from panel.io.pyodide import _link_docs_worker

    _link_docs_worker(state.curdoc, sendPatch, setter='js')
    `)
  } else if (msg.type === 'patch') {
    self.pyodide.runPythonAsync(`
    import json

    state.curdoc.apply_json_patch(json.loads('${msg.patch}'), setter='js')
    `)
    self.postMessage({type: 'idle'})
  } else if (msg.type === 'location') {
    self.pyodide.runPythonAsync(`
    import json
    from panel.io.state import state
    from panel.util import edit_readonly
    if state.location:
        loc_data = json.loads("""${msg.location}""")
        with edit_readonly(state.location):
            state.location.param.update({
                k: v for k, v in loc_data.items() if k in state.location.param
            })
    `)
  }
}

startApplication()