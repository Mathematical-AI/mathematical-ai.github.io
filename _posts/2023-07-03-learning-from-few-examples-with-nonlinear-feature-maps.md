---
layout: authored_post
title:  Learning from few examples with nonlinear feature maps
date:   2023-07-05 06:32:38 +0000
categories: news
authors: 
  - Oliver Sutton
---

In a recent paper[^mathematical-fsl], we have been exploring the role of nonlinear feature maps in learning from few examples.
Specifically, suppose that we have some previously trained classifier $F : \mathbb{R}^n \to \mathcal{L}$ (where $\mathcal{L}$ is some set of data labels), which works well on an existing dataset. 
However, we now wish to update this classifier to also be able to classify data from some new data class, for which we have very few available examples.
Rather than retraining the whole system with this extra data (and risking losing any existing behaviour and overfitting to the few available new data points), we just want to be able to cheaply 'update' our existing classifier.

A simple way of achieving this is to use a binary linear classifier in some appropriate feature space: if we decide that a sample belongs to the old classes then we use the old classifier, otherwise we just assign the new label.
This approach has also been studied elsewhere[^entropy] [^3], and indeed in[^3] it was shown that for *high dimensional* data, this approach can be extremely effective.

[...then the story continues...]

#### References

[^mathematical-fsl]: {%- include citation_markdown.html citekey="Sutton2022-towards-a-mathematical" %}

[^entropy]: {%- include citation_markdown.html citekey="Gorban2021-high-dimensional-separability" %}

[^3]: {%- include citation_markdown.html citekey="Tyukin2021-demystification-of-few" %}