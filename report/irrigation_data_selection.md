# Irrigation training data selection

## Selected source

[Mendeley Data, version 3: Smart irrigation control system data with soil moisture, flow meter and electrovalve relay](https://data.mendeley.com/datasets/cjb4vy4mzj/3), DOI `10.17632/cjb4vy4mzj.3`, CC BY 4.0. Authors: Jose Maria Manzano, Luis Orihuela, Alejandro Tapia Cordoba, Erid Pacheco, and Jorge Bareiro (2023).

This is the strongest fit among the inspected candidates for a first model grounded in documented field measurements. It is not a claim that one dataset is universally best. The source describes a strawberry field in Paraguay, with measurements collected in July–September 2022.

The published file previews were inspected without training:

- `D_moisture.txt`: comma-separated `moisture,time_stamp`; 4,293 readings.
- `D_valve.txt`: comma-separated `relay,time_stamp`; 17,427 readings, with 14,038 closed (`0`) and 3,389 open (`1`).
- Moisture uses the source sensor's percentage scale. Do not interpret it as calibrated volumetric water content or feed it into notebook 07's soil-water equations.

The training notebook predicts an observed irrigation start in the next hour, at times when the valve is currently closed. Its label is derived from future valve observations, not generated from a moisture threshold. It learns the recorded controller's behavior; that is not proof of an optimal watering decision.

## Alternatives reviewed

| Candidate | Assessment |
| --- | --- |
| [Kaggle Smart Agriculture Dataset](https://www.kaggle.com/datasets/chaitanyagopidesi/smart-agriculture-dataset) | Broader crop/stage inputs, but the downloaded CSV contains labels 0/1/2 while the data card describes a binary target. Collection and annotation provenance are insufficient for treating this as the primary field benchmark. |
| [Mendeley Agricultural Irrigation Control Dataset](https://data.mendeley.com/datasets/3w3pf3vnd4/1) | Relevant environmental sensors; the available metadata does not establish a supervised irrigation-label definition. Its ZIP contents could not be inspected through the available download path. |
| [Mendeley Dataset on irrigation for Tomato](https://data.mendeley.com/datasets/33cngpcrmx/3) | Relevant tomato sensors and weather variables; its published summary alone does not establish the precise supervised target needed for this notebook. |

## Evaluation and limits

Use chronological training/validation/test periods, purge labels that extend past a split boundary, and add a one-hour gap. Features must only use readings available at prediction time. Compare a majority baseline, a one-feature threshold model, logistic regression, and random forest. Choose the classifier and threshold using validation data, then evaluate the frozen choice on the final test period.

Report macro-F1, positive-class precision/recall/F1, average precision, and a confusion matrix. Neighboring examples are correlated, so row counts are not independent field trials. This is a one-field, one-crop benchmark: weather forecasts, crop-stage variation, optimal water quantities, and actual water savings are not learned or established here.

The notebook is prepared for the user to execute. No notebook cells or training commands were run during preparation. Source metadata, file previews, and a separate read-only CSV inspection informed this selection.
