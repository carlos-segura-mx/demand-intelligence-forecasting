# Inteligencia de demanda y pronósticos

**Cuando una cartera tiene cientos de productos con comportamientos distintos, ¿qué pronósticos conviene utilizar y cuáles revisar primero?**

[Español](README.es.md) | [English](../README.md) | [Metodología](methodology.es.md) | [Datos y reproducción](DATA.es.md)

Un equipo de planeación comercial necesita pronósticos que pueda explicar y una forma práctica de decidir dónde concentrar su atención. Un modelo más complejo no necesariamente produce mejores resultados. Evalué esa decisión con 52 semanas indexadas de cantidades compradas para 811 productos del conjunto *Sales Transactions Weekly* de UCI.

## Qué encontré

| Evaluación final, W44 a W51 | WAPE | Sesgo del pronóstico |
| --- | ---: | ---: |
| Modelo base: repetir la última semana observada | 33.73 % | -2.50 % |
| Suavizamiento exponencial simple (SES) | **27.45 %** | -3.73 % |
| Selección de modelos por segmento ABC/XYZ | 27.63 % | -6.03 % |

SES redujo **18.6 %** el error absoluto total en unidades respecto al modelo base. Elegir diferentes modelos por segmento ABC/XYZ no mejoró el resultado agregado. En este ejercicio conviene comenzar con un método sencillo por producto, en vez de añadir complejidad sin una mejora comprobada.

El indicador agregado no cuenta toda la historia. En la evaluación final, el segmento A/X concentró 43,424 de las 56,528 unidades observadas y obtuvo un WAPE de 22.22 % con SES. El segmento C/Z concentró solamente 1,287 unidades y registró un WAPE de 93.59 %. Estas diferencias justifican revisar los errores por grupo de productos y no únicamente en toda la cartera. La clasificación ABC se basa en unidades históricas, no en ingresos ni rentabilidad.

## Del pronóstico a la revisión

Construí una aplicación interactiva en Streamlit, disponible en español e inglés, para comparar modelos, explorar productos, analizar segmentos ABC/XYZ y consultar una lista priorizada de revisión. Esa lista utiliza **solo observaciones hasta W43** y produce pronósticos para W44 y para el periodo W44 a W47. Son periodos históricos de demostración, no pronósticos para la semana actual.

La lista ofrece dos formas complementarias de trabajo: alertas basadas en una puntuación de revisión y un ordenamiento independiente por volumen histórico. Incluye una tabla resumida, el diagnóstico de cada producto y exportación CSV. La prioridad es una regla de revisión definida por el analista, no una clasificación económica, una probabilidad de desabasto ni una orden de compra.

## Dashboard interactivo

[Explorar el dashboard en línea](https://demand-intelligence-forecasting-biexn2j5lhinfwgmdybb2x.streamlit.app/). La aplicación permite comparar modelos, analizar errores por segmento ABC/XYZ y descargar una lista priorizada de revisión en español e inglés.

## Explorar y reproducir

El repositorio contiene `app.py`, modelos, pruebas, datos autorizados y resultados reproducibles. Para ejecutar el proyecto localmente:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python reproduce.py
streamlit run app.py
```

Consulta la [metodología](methodology.es.md) para conocer el diseño temporal y los métodos, y las [notas sobre los datos](DATA.es.md) para verificar origen, licencia y reproducción.

## Datos e interpretación

WAPE es la suma de errores absolutos dividida entre las unidades observadas; un valor menor indica menor error agregado. El sesgo resume la diferencia con signo entre pronósticos y cantidades observadas. Ninguna de estas métricas representa un impacto financiero.

La fuente contiene cantidades compradas observadas, no una medición confirmada de demanda sin restricciones. No incluye fechas reales, precios, costos, inventarios, desabastos, promociones ni tiempos de entrega. La evaluación final solo utiliza dos orígenes de pronóstico y no demuestra superioridad permanente por producto.

**Fuente:** Tan, J. (2014), *Sales Transactions Weekly*, UCI Machine Learning Repository, [DOI: 10.24432/C5XS4Q](https://doi.org/10.24432/C5XS4Q), licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Derechos

No se ha seleccionado una licencia open-source separada para el código original de este repositorio.

**Carlos Segura**
