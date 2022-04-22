<p align="center">
  <a href="https://etiq.ai">
    <img src="https://etiq.ai/etiq-ai-logo-transparent.png" alt="Etiq AI logo">
  </a>
</p>

<h3 align="center">Etiq AI Demo Repository</h3>

<p align="center">
  Etiq AI provides a platform to allow you to optimise and mitigate issues &amp; identify fairness and biases issues in your predictive models.
  <br>
  <a href="https://docs.etiq.ai"><strong>Explore the documentation</strong></a>
  <br>
  <br>
  <a href="https://github.com/ETIQ-AI/demo/issues">Raise an issue</a>
  ·
  <a href="https://etiqcore.slack.com/signup#/domain-signup">Slack</a>
  ·
  <a href="https://etiq.ai/blog">Blog</a>
  ·
  <a href="https://etiq.ai/contact-us">Contact</a>
</p>

## Etiq AI 

In order to start working with the Etiq AI platform you will need to sign-up to our dashboard: https://dashboard.etiq.ai/ and then install the python package. 

    pip install etiq

This repository provides a number of notebooks and examples that show how easy it is to use and work with the Etiq.

### Docs

For a quickstart and install just go to our docs: https://docs.etiq.ai/quickstart

### Getting started

To set-up your testing suite as you build your model, you can just use etiq directly from your jupyter notebook or any other python based IDE. To start just import etiq once you've installed it, log to the dashboard and create a project.
You can run the library without connecting to the dashboard, but then your results will not be stored. 
Only the results of the tests gets stored, the details of the models or datasets underneath are not stored.

    import etiq
    


Load the config you'll use for your tests from whereever you store it. A config is in a simple json format & it's where you can set your tests details - metrics you want to use, what kind of scans you want to run, what thresholds you want to put for passing a test:

    etiq.load_config("./config_demo.json")

A config is in a simple json format & it's where you can set your tests details - metrics you want to use, what kind of scans you want to run, what thresholds you want to put for passing a test:


        {"dataset": {
                "label": "income",
                "bias_params": {
                    "protected": "gender",
                    "privileged": 1,
                    "unprivileged": 0,
                    "positive_outcome_label": 1,
                    "negative_outcome_label": 0
                },
                "train_valid_test_splits": [0.0, 1.0, 0.0],
                "cat_col": "cat_vars",
                "cont_col": "cont_vars"
            },
            "scan_accuracy_metrics": {
                "thresholds": {
                    "accuracy": [0.8, 1.0],
                    "true_pos_rate": [0.6, 1.0],
                    "true_neg_rate":  [0.6, 1.0]           
                }
            },
            "scan_bias_metrics": {
                "thresholds": {
                    "equal_opportunity": [0.0, 0.2],
                    "demographic_parity": [0.0, 0.2]     
                }
            }, 
            "scan_leakage": {
                "leakage_threshold": 0.85
               }
        }

Next, log your dataset, model, shanpshot - as applicable

    from etiq import Model
     
    dataset_loader = etiq.dataset(my_test_dataset)
      
    model = Model(model_architecture=my_trained_model, model_fitted=my_model_fit)
     
    snapshot = project.snapshots.create(name="My New Snapshot", dataset=dataset_loader.initial_dataset, model=model, bias_params=dataset_loader.bias_params)


Run the scans you want to run:

    snapshot.scan_accuracy_metrics()
     
    snapshot.scan_bias_metrics()
     
    snapshot.scan_leakage()

You can retrieve the results either via the interface or via the dashboard.

![dashboard_screenshot](https://user-images.githubusercontent.com/94112047/164801597-b100f7fa-a82c-441d-91a3-05bdf480852c.png)


For testing in production, we will release an Etiq + Airflow demo example shortly. But in the meantime, just reach out: info@etiq.ai

We also recommend integrating tests with your Github commits. For help just email us info@etiq.ai


## Example Notebooks & Configs

We have pre-set example notebooks and config files.

### Legacy library

As the change from v1.2.4 to v1.3 we have Legacy notebooks in case you are still on 1.2.4 and you can find the dashboard for this version at https://legacy-dashboard.etiq.ai

## Bugs and feature requests

If you discover a bug or have a great idea that you would like to see in the Etiq AI tool then please share it either by:

- Raising an [issue](https://github.com/ETIQ-AI/demo/issues) in this repo.
- Join &amp; discuss it with us on the [Etiq Slack channel](https://etiqcore.slack.com/signup#/domain-signup).
- [Contact us via our website](https://etiq.ai/contact-us) and we will come back to discuss it with you.

## Documentation

Etiq AI provide a full set of documentation covering all aspects of the Etiq AI Library [here](https://docs.etiq.ai/).

## The Good Data Science Club

Are you interested in Ethics, Fairness &amp; Bias in Artificial intelligence and Machine Learning?

If so we are part of The Good Data Science Club community. We'd love to discuss all things AI/ML here and you can click to join [here](https://gooddatascience.slack.com/signup#/domain-signup).

## Copyright and license

All Code and documentation copyright 2019–2022 [Etiq AI](https://etiq.ai)
