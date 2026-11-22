# Methodology and decision rules

[English](methodology.md) | [Español](methodology.es.md)

## Business decision

The case tests whether a simple product-quantity forecast is adequate and how a planner might organize reviews across hundreds of products. It does not estimate unconstrained demand or inventory needs.

## Dataset

The source contains 811 products and 52 indexed weeks, W0 to W51, of observed purchase quantities. The supplied normalized fields are excluded. No actual calendar dates, revenue, cost, stockouts, inventory or lead times are available.

## Forecast evaluation

Four candidates are evaluated: the last-observation baseline (naive method), a four-week moving average, simple exponential smoothing (SES, fixed alpha 0.3) and Croston-SBA (fixed alpha 0.2). SES is applied separately to each product using the same smoothing parameter; it is not fitted to one aggregated product series. Selection uses forecast origins W32, W36 and W40, targeting W32 to W43. The final holdout uses W44 and W48, targeting W44 to W51. All forecasts are constructed using only prior weeks.

WAPE is the sum of absolute errors divided by observed quantities. Bias is the signed sum of forecast minus observed quantities divided by observed quantities. An aggregate WAPE is undefined when the denominator is zero, and must not be assigned an artificial value.

SES was selected on validation and achieved 27.45% WAPE versus 33.73% for the baseline in the final holdout. This is an 18.6% pooled absolute-error reduction.

## Portfolio segmentation

ABC uses historical observed unit volume, not revenue or margin, at cumulative 80% and 95% thresholds. XYZ uses the coefficient of variation of weekly quantity observations. ADI and positive-quantity squared CV add descriptive purchasing-pattern labels.

The segment-to-model mapping is chosen using earlier validation only. A different historical window is used to assign the final holdout labels without reading holdout outcomes. The segmented policy returned 27.63% WAPE, slightly worse than SES. In the final evaluation under SES, A/X had 43,424 observed units with 22.22% WAPE, while C/Z had 1,287 observed units with 93.59% WAPE. ABC here represents historical quantities, not revenue or profitability. Segment-level percentages need volume context.

## Prospective Decision Center

The review queue uses W0 to W43 only. Its next-week forecast means W44 and its four-week total means W44 to W47 from that historical cutoff, not a forecast for the current calendar week. Its score adds A/B/C points (3/2/1), 2 points for XYZ=Z, 1 for 50% or more zero weeks and 2 for a recent four-week change of at least 50% and 4 units. High means score 6 or more, Medium 4 to 5 and Routine under 4.

The queue must align each historical series with the product identifier after segmentation is sorted. This alignment is explicitly tested. After the correction, the queue contains 7 High, 293 Medium and 511 Routine products.

The score is an analyst-defined rule, not a calibrated probability, monetary exposure or replenishment quantity. Retrospective holdout exceptions are separate and are not used to rank this queue.

## Limitations

Two final origins cannot prove long-term stability. Observed purchases can be constrained by product availability. There are no multi-year cycles, promotions, inventory histories, unit costs or actual calendar dates. The findings are an analytical demonstration, not observed commercial savings.

**Source:** Tan, J. (2014). Sales Transactions Weekly, UCI Machine Learning Repository, DOI 10.24432/C5XS4Q. CC BY 4.0.
