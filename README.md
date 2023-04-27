# SMNA Dashboard

Um exemplo de dashboard utilizando o Panel para a visualização do processo de minimização da função custo do GSI/3DVar do Sistema de Modelagem Numérica e Assimilação de dados.

## Conversão

Para transformar o arquivo Jupyter Notebook em um App, basta salvar o arquivo de notebook como um script do Python (utilizando a interface do Jupyter). Depois, executar o seguinte comando:

```
panel convert SMNA_Dashboard.py --to pyodide-worker --out .
```