# SMNA-Dashboards

Testes com dashboards no GitHub utilizando o Panel.

```
panel convert load_csv_dataset_plot-multiple-panel-from_zarr.py --index --skip-embed --pwa --to pyodide-worker --requirements requirements.txt --out .
```

## Opções

* `--index`: cria um arquivo `index.html` que serve como uma página de índice para vários dashboards;
* `--skip-embed`: não mostra a pré-visualização do dashboard enquanto ele é carregado;
* `--pwa`: cria uma versão Progressive Web App.
