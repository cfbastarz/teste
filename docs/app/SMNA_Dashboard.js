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

# In[1]:


import os
import re
import numpy as np
import pandas as pd

from datetime import datetime, timedelta
from matplotlib import pyplot as plt

import hvplot.pandas  # noqa
import panel as pn

pn.extension(sizing_mode="stretch_width")
#pn.extension()
#pd.options.plotting.backend = 'holoviews'


# In[2]:


def df_Nobs(fname, loop, nexp, mname):

    colnames = ['Observation Type', 'Nobs', 'Jo', 'Jo/n']
    
    dfNobs = pd.DataFrame(columns=colnames)
    
    if loop == 'outer':
        begin = 'Begin Jo table outer loop'
        end = 'End Jo table outer loop'
    elif loop == 'inner':
        begin = 'Begin Jo table inner loop'
        end = 'End Jo table inner loop'
    else:
        begin = 'Begin Jo'
        end = 'End Jo'
    
    with open(fname, 'r') as file:
        match = False
        i = 0
        for line in file:
            line = line.strip()
            if re.match(begin, line):
                match = True
                continue
            elif re.match(end, line):
                match = False
                continue
            elif match:     

                sline = line.split()
                if len(sline) == 5:
                    ltmp = [sline[0] + ' ' + sline[1]] + sline[2:]
                elif len(sline) == 3:
                    ltmp = [''] + sline
                else:
                    ltmp = sline

                if ltmp[0] == 'Observation Type':
                    pass
                elif ltmp[1] == 'Nobs':
                    pass
                else:
                    ltmp[0] = str(ltmp[0])
                    ltmp[1] = int(ltmp[1])
                    ltmp[2] = float(ltmp[2])
                    ltmp[3] = float(ltmp[3])
                    
                    dfNobs.loc[i] = ltmp
                    
                i += 1
            
        dfNobs = dfNobs.set_index('Observation Type')
        #dfNobs.name = nexp   
        dfNobs.name = str(mname)
            
    return dfNobs


# In[3]:


bpath = '/home/carlos/Documents/INPE2023/GDAD/SMNA_Dashboard'

def get_df_Nobs(datai, dataf, nexp, mname):

    datai = datetime.strptime(str(datai), '%Y%m%d%H')
    dataf = datetime.strptime(str(dataf), '%Y%m%d%H')
    
    dataifmt=datai.strftime('%Y%m%d%H')
    
    delta = 6
    data = datai

    data = datai + timedelta(hours=delta)

    log_list = {}

    while (data <= dataf):

        datafmt = data.strftime('%Y%m%d%H')
    
        fname = os.path.join(bpath, nexp, str(datafmt), str('gsiStdout_' + str(datafmt) + '.log')) 
    
        #log_list[datafmt] = df_Nobs(fname, loop, nexp)
        log_list[data] = df_Nobs(fname, loop, nexp, mname)
    
        data = data + timedelta(hours=delta)
    
    dftmp = pd.concat(log_list)
    dftmp.index.names = ['Date', dftmp.index.names[1]]
    dftmp = dftmp.reset_index()
    #dftmp.name = nexp.split('.')[1]
    dftmp.name = str(mname)
    
    return dftmp


# In[4]:


datai = '2023021600'
dataf = '2023031600'

loop = 'all'

df_dtc = get_df_Nobs(datai, dataf, 'dataout.fullobs_ncep-2023.jgerd', 'df_dtc')
df_bamh_T0 = get_df_Nobs(datai, dataf, 'dataout.fullobs_bamh_T0-2023', 'df_bamh_T0')
df_bamh_T4 = get_df_Nobs(datai, dataf, 'dataout.fullobs_bamh_T4-2023', 'df_bamh_T4')


# In[5]:


df_dtc


# In[6]:


df_bamh_T0


# In[7]:


df_bamh_T4


# In[62]:


experiment_list = [df_dtc, df_bamh_T0, df_bamh_T4]
variable_list = ['surface pressure', 'temperature', 'wind', 'moisture', 'gps', 'radiance'] 
attribute_list = ['Nobs', 'Jo', 'Jo/n'] 
facet_attribute_list = [None, 'Nobs', 'Jo', 'Jo/n'] 

experiment = pn.widgets.Select(name='Experimento', value=experiment_list[0].name, options=[i.name for i in experiment_list])
#experiment = pn.widgets.CheckBoxGroup(name='Experimentos', value=list(experiment_list[0].name), options=[i.name for i in experiment_list], inline=False)
variable = pn.widgets.Select(name='Variável', value=variable_list[0], options=variable_list)
attribute = pn.widgets.Select(name='Atributo', value=attribute_list[0], options=attribute_list)
facet_attribute = pn.widgets.Select(name='Combinação de Atributos', value=None, options=attribute_list)

@pn.depends(variable, attribute, experiment)
def plot(variable, attribute, experiment):
    df = globals()[experiment]
    return df.loc[df['Observation Type'] == variable][attribute].hvplot(label=str(experiment))
#    #return pn.widgets.StaticText(value=experiment)
#    df1 = globals()[experiment]
#    df1p = df1.loc[df1['Observation Type'] == variable][attribute].hvplot(label=str(experiment))
#    return df1p

settings = pn.Row(pn.WidgetBox(experiment, variable, attribute))
pn.Column(
    '### SMNA Dashboard', 
    settings,
    plot,
    width_policy='max'
)

pn.template.FastListTemplate(
    #site="SMNA", title="Dashboard", sidebar=[settings], 
    site="Teste", title="Dashboard", sidebar=[settings], 
    #main=["Visualização do processo de minimização da função custo do sistema **SMNA**.", plot]
    main=["Minimização da função custo.", plot]
).servable()


# In[ ]:






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