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

## Etiq AI Library

In order to start working with the Etiq AI platform you first need to integrate our Python library which is used to interrogate your predictive models. This repository provides a number of notebooks and examples that show how easy it is to use and work with the Etiq AI library.

### Installing the Etiq AI library

Installing the Etiq AI library via the Pypi package manager is as simple as

```shell
pip install etiq-core
```

## Example Notebooks

- [DatascienceFestivalDemoLeakage_Sept_2021_2](#DatascienceFestivalDemoLeakage_Sept_2021_2)
- [DemoAdultLibrary03](#DemoAdultLibrary03)

### DatascienceFestivalDemoLeakage_Sept_2021_2.

The etiqai library enables users to identify and mitigate bias in predictive models. The library is similar to pytorch or sklearn libraries, with a battery of metrics and debiasing algorithms available to find the best debiasing method for the problem at hand. We are now adding functionality to identify additional issues in predictive models, e.g. leakage, which we found are very time-consuming and have many other bias and non-bias related implications down-the-line.

The DataPipeline object holds what we'd like to focus on during the debiasing process: the dataset used for training the model, the model we'd like to test and the fairness metrics used to evaluate results. DebiasPipeline objects take the initial DataPipeline object and apply to it different Identify methods, which aim to generate flags for rows at risk of being biased against, or Repair methods. Repair methods generate new "debiased" datasets. Models trained on debiased datasets perform better on fairness metrics. We have a (growing) collection of repair methods that allow our users to pick the debiased dataset version that best fits their criteria for a good solution.

### DemoAdultLibrary03

The Etiq AI library enables users to identify and mitigate bias in predictive models. The library is similar to pytorch or sklearn libraries, with a battery of metrics and debiasing algorithms available to find the best debiasing method for the problem at hand.

The DataPipeline object holds what we'd like to focus on during the debiasing process: the dataset used for training the model, the model we'd like to test and the fairness metrics used to evaluate results. DebiasPipeline objects take the initial DataPipeline object and apply to it different Identify methods, which aim to generate flags for rows at risk of being biased against, or Repair methods. Repair methods generate new "debiased" datasets. Models trained on debiased datasets perform better on fairness metrics. We have a (growing) collection of repair methods that allow our users to pick the debiased dataset version that best fits their criteria for a good solution.

As a social enterprise, our mission is to address some of the most fundamental AI ethics issues to create a fairer world. We really appreciate your feedback on using this library, whether it's good or bad! With your support we firmly believe we can build a better world together. To access our full solution including hands on support, to submit any comments, feature requests or issues please login to our slack channel https://etiqcore.slack.com or email us at info@etiq.ai

## Bugs and feature requests

If you discover a bug or have a great idea that you would like to see in the Etiq AI library then please share it either by:

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
