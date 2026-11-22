# Inteligencia de demanda y pronósticos

**¿Cuánta complejidad necesita realmente el pronóstico de una cartera de productos?**

[Español](README.es.md) | [English](../README.md) | [Método y datos](methodology.es.md)

Pronosticar cientos de productos no consiste solo en elegir un algoritmo. También hay que decidir cuáles requieren una revisión más cercana y cuándo vale la pena utilizar un modelo más complejo.

Construí este caso con 52 semanas indexadas de cantidades observadas para 811 productos del conjunto *Sales Transactions Weekly* de UCI. Comparé modelos sencillos, evalué sus resultados en semanas posteriores y diseñé una cola de revisión para orientar el trabajo de planeación comercial.

## Lo que encontré

| Evaluación final, semanas W44 a W51 | WAPE | Sesgo |
| --- | ---: | ---: |
| Pronóstico ingenuo | 33.73 % | -2.50 % |
| Suavizamiento exponencial simple global (SES) | **27.45 %** | -3.73 % |
| Política segmentada ABC/XYZ | 27.63 % | -6.03 % |

El modelo SES global redujo **18.6 %** el error absoluto agregado frente al pronóstico ingenuo. La política segmentada ABC/XYZ, aunque más elaborada, no lo superó en esta evaluación.

Por eso no recomendaría añadir complejidad sin un beneficio comprobado. Mantendría SES como referencia de partida y utilizaría la segmentación para decidir qué productos merecen atención. Una cola prospectiva de revisión identifica cambios recientes y patrones irregulares sin mirar los resultados del periodo de evaluación final.

## Explorar el análisis

El proyecto incluye un dashboard Streamlit para consultar modelos, pronósticos por producto, segmentación ABC/XYZ, errores retrospectivos y un centro de revisión prospectiva. La interfaz está disponible en **español e inglés**.

**Estado de publicación:** el repositorio contiene una versión candidata. Añadiremos la URL de Streamlit cuando el despliegue esté realizado y comprobado.

## Origen de los datos y límites

Los datos contienen 811 productos anónimos y 52 índices semanales relativos. Son **cantidades compradas observadas**, no una medición confirmada de demanda sin restricciones. No incluyen fechas de calendario, precios, costos, inventario, faltantes, promociones ni tiempos de entrega. La clasificación ABC se calcula por volumen de unidades, no por ingresos.

Los pronósticos y las reglas de revisión no equivalen a órdenes de compra ni estimaciones de pérdidas económicas. La evaluación final tiene solamente dos orígenes de pronóstico, por lo que no permite asegurar estabilidad en todos los productos.

**Fuente:** Tan, J. (2014), *Sales Transactions Weekly*, UCI Machine Learning Repository, DOI: https://doi.org/10.24432/C5XS4Q, licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). El conjunto original se atribuye a su autor y no contiene datos de clientes propios.

## Reproducir el caso

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python reproduce.py
streamlit run app.py
```

El procedimiento de incorporación de datos está explicado en [datos y reproducción](DATA.es.md), y la metodología completa en [metodología](methodology.es.md).

**Carlos Segura | CS Intelligence**
