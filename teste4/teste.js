importScripts("https://cdn.jsdelivr.net/pyodide/v0.21.3/full/pyodide.js");

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
  const env_spec = ['https://cdn.holoviz.org/panel/0.14.2/dist/wheels/bokeh-2.4.3-py3-none-any.whl', 'https://cdn.holoviz.org/panel/0.14.2/dist/wheels/panel-0.14.2-py3-none-any.whl', 'pyodide-http==0.1.0', 'intake']
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

import intake
import panel as pn

Regs = ['gl', 'hn', 'tr', 'hs', 'as']
Exps = ['DTC', 'BAMH', 'BAMH0', 'X666']
Stats = ['VIES', 'RMSE', 'MEAN']

catalog = intake.open_catalog('https://raw.githubusercontent.com/cfbastarz/teste/main/teste3/catalog-zarr.yml')

ds1 = catalog.scantec_gl_rmse_dtc.to_dask()

Vars = list(ds1.variables)
Vars.remove('time')
Vars.remove('lat')
Vars.remove('lon')

variable_list = Vars
variable = pn.widgets.Select(name='Variável', value=variable_list[0], options=variable_list)

region = pn.widgets.Select(name='Região', value=Regs[0], options=Regs)
experiment = pn.widgets.Select(name='Experimento', value=Exps[0], options=Exps)
statistic = pn.widgets.Select(name='Estatística', value=Stats[0], options=Stats)

test_list = ['ref_GFS', 'ref_Era5', 'ref_PAnl']
test = pn.widgets.Select(name='Referência', value=test_list[0], options=test_list)

#@pn.depends(variable, region, experiment, statistic, test)
#def plotFields(variable, region, experiment, statistic, test):
#    if test == 'ref_GFS': ttest = 'T1'
#    if test == 'ref_Era5': ttest = 'T2'
#    if test == 'ref_PAnl': ttest = 'T3'
#    #lfile = str(statistic) + str(experiment) + '_' + data + 'F.zarr'
#    #lfname = os.path.join(ttest, region, lfile)
#    #dfs = globals()['df_lst'][lfname]
#    lfname = 'scantec_' + region.lower() + '_' + statistic.lower() + '_' + experiment.lower()
#    dfs = catalog[lfname].to_dask()
#    cmin=dfs[variable].min()
#    cmax=dfs[variable].max()
#    #if (variable[0:4] == 'vtmp') or (variable[0:4] == 'temp'): cmap='fire_r'
#    #if (variable[0:4] == 'pslc') or (variable[0:4] == 'zgeo'): cmap='viridis'
#    #if variable[0:4] == 'umes': cmap='blues'
#    #if (variable[0:4] == 'uvel') or (variable[0:4] == 'vvel'): cmap='coolwarm'
#    cmap='tab20c_r'
#    if region == 'as': 
#        frame_width=500
#    else: 
#        frame_width=960
#    #ax = dfs[variable].hvplot(groupby='time', clim=(cmin, cmax), widget_type='scrubber', widget_location='bottom', 
#    #                          frame_width=frame_width, projection=ccrs.PlateCarree(), coastline=True,
#    #                          cmap=cmap)
#    ax = dfs[variable].hvplot(groupby='time', clim=(cmin, cmax), widget_type='scrubber', widget_location='bottom', 
#                              frame_width=frame_width, cmap=cmap)
#    #ax.add_feature(cfeature.STATES.with_scale('50m'), zorder=2, linewidth=1.5, edgecolor='b')
#    #ax.add_feature(cfeature.BORDERS, linewidth=0.5)
#    return pn.Column(ax, sizing_mode='stretch_width')

card_parameters = pn.Card(variable, region, experiment, statistic, test, title='Parâmetros', collapsed=False)

settings = pn.Column(card_parameters)

pn.Column(
    settings,
    width_policy='max'
)

pn.template.FastListTemplate(
    site="SMNA Dashboard", title="SCANTEC", sidebar=[settings],
    main=["Visualização do Skill do **SMNA**."], 
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