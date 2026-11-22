# Fuente de datos y reproducción

[Español](DATA.es.md) | [English](DATA.en.md)

El conjunto original **Sales Transactions Weekly** fue publicado por James Tan en UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/396/sales+transactions+dataset+weekly. DOI: https://doi.org/10.24432/C5XS4Q. UCI indica la licencia **Creative Commons Atribución 4.0 Internacional**, https://creativecommons.org/licenses/by/4.0/.

Se utiliza la fuente original con atribución, sin incorporar datos de clientes. El modelo emplea Product_Code y W0 a W51. Excluye las variables normalizadas disponibles en el archivo original.

Ejecutar desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
python scripts/fetch_uci_data.py
python -m pytest -q
python reproduce.py
streamlit run app.py
```

El script descarga el archivo oficial de UCI, recupera el CSV original y verifica su SHA-256 frente a la versión utilizada en el análisis: `6f939a928c04820bc291a6184f4f1d0be694b8de58d949e808852804f25969c3`. Si cambia la huella, la ejecución se detiene para revisar la fuente y no modifica los resultados silenciosamente.

El flujo de publicación incorpora al repositorio el CSV verificado y las tablas calculadas, de manera que Streamlit no necesite ejecutar todos los modelos al abrir la página. Para regenerar el análisis se utiliza `python reproduce.py`, cotejando las métricas con los valores documentados. Las semanas son índices relativos y no deben convertirse en fechas reales.

Los datos conservan su licencia CC BY 4.0. Que el código sea público no significa que su autor haya elegido una licencia abierta adicional para el código.
