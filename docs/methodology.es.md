# Metodología y reglas de decisión

[Español](methodology.es.md) | [English](methodology.md)

## Decisión comercial

El caso evalúa si un pronóstico sencillo de cantidades puede ser suficiente y cómo organizar la revisión de cientos de productos. No estima demanda sin restricciones ni necesidades reales de inventario.

## Datos

La fuente incluye 811 productos y 52 semanas indexadas, W0 a W51, con cantidades compradas observadas. Se excluyen las variables normalizadas proporcionadas en el conjunto original. No hay fechas de calendario, ventas en dinero, costos, desabastos, inventarios ni tiempos de entrega.

## Evaluación de pronósticos

Se comparan cuatro candidatos: ingenuo, promedio móvil de cuatro semanas, suavizamiento exponencial simple (alfa fijo de 0.3) y Croston-SBA (alfa fijo de 0.2). La selección utiliza los orígenes W32, W36 y W40, con objetivos entre W32 y W43. La evaluación final utiliza W44 y W48 para pronosticar W44 a W51. Cada cálculo usa solamente las semanas previas al origen.

WAPE es la suma de errores absolutos dividida entre las cantidades observadas. El sesgo es la suma de pronóstico menos observado, dividida entre cantidades observadas. Si el denominador es cero, no se asigna artificialmente un WAPE.

SES global fue elegido en la validación y obtuvo 27.45 % de WAPE frente a 33.73 % del pronóstico ingenuo en la evaluación final. Eso equivale a una reducción de 18.6 % del error absoluto agregado.

## Segmentación de cartera

ABC usa volumen histórico de unidades observadas, no ingresos o margen, con umbrales acumulados de 80 % y 95 %. XYZ se basa en el coeficiente de variación de cantidades semanales. ADI y CV cuadrado de cantidades positivas permiten describir patrones de compra.

Las reglas que asignan modelos a segmentos se eligen con la validación anterior. Para el periodo final se calculan perfiles históricos sin consultar los resultados futuros. La política segmentada registró 27.63 % de WAPE, ligeramente peor que SES global.

## Centro de decisiones prospectivo

La cola de revisión solo utiliza W0 a W43. Su puntuación suma puntos por clase ABC (3/2/1), 2 por XYZ=Z, 1 si al menos la mitad de las semanas tiene cero unidades y 2 si las últimas cuatro semanas muestran un cambio de al menos 50 % y 4 unidades. Alta corresponde a 6 puntos o más; media, de 4 a 5; rutinaria, menos de 4.

Tras ordenar la segmentación es indispensable relacionar cada serie con su identificador de producto. La alineación se prueba explícitamente. Después de corregirla, hay 7 productos de prioridad alta, 293 media y 511 rutinaria.

La puntuación es una regla de revisión definida por el analista. No representa probabilidades calibradas, pérdidas monetarias ni cantidades a reabastecer. Los errores retrospectivos del periodo de evaluación se mantienen separados.

## Limitaciones

Dos orígenes finales no prueban estabilidad a largo plazo. Las cantidades compradas pueden estar limitadas por la disponibilidad. No tenemos varios ciclos anuales, promociones, historiales de inventario, costos unitarios ni fechas reales. Este caso demuestra un método de análisis, no ahorros comerciales observados.

**Fuente:** Tan, J. (2014). Sales Transactions Weekly, UCI Machine Learning Repository, DOI 10.24432/C5XS4Q. CC BY 4.0.
