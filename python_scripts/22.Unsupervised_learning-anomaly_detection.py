# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: notebooks//ipynb,markdown_files//md,python_scripts//py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 1.2.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown] {"deletable": true, "editable": true}
# # Anomaly detection
#
# Anomaly detection is a machine learning task that consists in spotting so-called outliers.
#
# “An outlier is an observation in a data set which appears to be inconsistent with the remainder of that set of data.”
# Johnson 1992
#
# “An outlier is an observation which deviates so much from the other observations as to arouse suspicions that it was generated by a different mechanism.”
#   Outlier/Anomaly
# Hawkins 1980
#
# ### Types of anomaly detection setups
#
# - Supervised AD
#     - Labels available for both normal data and anomalies
#     - Similar to rare class mining / imbalanced classification
# - Semi-supervised AD (Novelty Detection)
#     - Only normal data available to train
#     - The algorithm learns on normal data only
# - Unsupervised AD (Outlier Detection)
#     - no labels, training set = normal + abnormal data
#     - Assumption: anomalies are very rare

# %% {"deletable": true, "editable": true}
# %matplotlib inline

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# %% [markdown] {"deletable": true, "editable": true}
# Let's first get familiar with different unsupervised anomaly detection approaches and algorithms. In order to visualise the output of the different algorithms we consider a toy data set consisting in a two-dimensional Gaussian mixture.

# %% [markdown] {"deletable": true, "editable": true}
# ### Generating the data set

# %% {"deletable": true, "editable": true}
from sklearn.datasets import make_blobs

X, y = make_blobs(n_features=2, centers=3, n_samples=500,
                  random_state=42)

# %% {"deletable": true, "editable": true}
X.shape

# %% {"deletable": true, "editable": true}
plt.figure()
plt.scatter(X[:, 0], X[:, 1])
plt.show()

# %% [markdown] {"deletable": true, "editable": true}
# ## Anomaly detection with density estimation

# %% {"deletable": true, "editable": true}
from sklearn.neighbors.kde import KernelDensity

# Estimate density with a Gaussian kernel density estimator
kde = KernelDensity(kernel='gaussian')
kde = kde.fit(X)
kde

# %% {"deletable": true, "editable": true}
kde_X = kde.score_samples(X)
print(kde_X.shape)  # contains the log-likelihood of the data. The smaller it is the rarer is the sample

# %% {"deletable": true, "editable": true}
from scipy.stats.mstats import mquantiles
alpha_set = 0.95
tau_kde = mquantiles(kde_X, 1. - alpha_set)

# %% {"deletable": true, "editable": true}
n_samples, n_features = X.shape
X_range = np.zeros((n_features, 2))
X_range[:, 0] = np.min(X, axis=0) - 1.
X_range[:, 1] = np.max(X, axis=0) + 1.

h = 0.1  # step size of the mesh
x_min, x_max = X_range[0]
y_min, y_max = X_range[1]
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                     np.arange(y_min, y_max, h))

grid = np.c_[xx.ravel(), yy.ravel()]

# %% {"deletable": true, "editable": true}
Z_kde = kde.score_samples(grid)
Z_kde = Z_kde.reshape(xx.shape)

plt.figure()
c_0 = plt.contour(xx, yy, Z_kde, levels=tau_kde, colors='red', linewidths=3)
plt.clabel(c_0, inline=1, fontsize=15, fmt={tau_kde[0]: str(alpha_set)})
plt.scatter(X[:, 0], X[:, 1])
plt.show()

# %% [markdown] {"deletable": true, "editable": true}
# ## now with One-Class SVM

# %% [markdown]
# The problem of density based estimation is that they tend to become inefficient when the dimensionality of the data increase. It's the so-called curse of dimensionality that affects particularly density estimation algorithms. The one-class SVM algorithm can be used in such cases.

# %% {"deletable": true, "editable": true}
from sklearn.svm import OneClassSVM

# %% {"deletable": true, "editable": true}
nu = 0.05  # theory says it should be an upper bound of the fraction of outliers
ocsvm = OneClassSVM(kernel='rbf', gamma=0.05, nu=nu)
ocsvm.fit(X)

# %% {"deletable": true, "editable": true}
X_outliers = X[ocsvm.predict(X) == -1]

# %% {"deletable": true, "editable": true}
Z_ocsvm = ocsvm.decision_function(grid)
Z_ocsvm = Z_ocsvm.reshape(xx.shape)

plt.figure()
c_0 = plt.contour(xx, yy, Z_ocsvm, levels=[0], colors='red', linewidths=3)
plt.clabel(c_0, inline=1, fontsize=15, fmt={0: str(alpha_set)})
plt.scatter(X[:, 0], X[:, 1])
plt.scatter(X_outliers[:, 0], X_outliers[:, 1], color='red')
plt.show()

# %% [markdown] {"deletable": true, "editable": true}
# ### Support vectors - Outliers
#
# The so-called support vectors of the one-class SVM form the outliers

# %% {"deletable": true, "editable": true}
X_SV = X[ocsvm.support_]
n_SV = len(X_SV)
n_outliers = len(X_outliers)

print('{0:.2f} <= {1:.2f} <= {2:.2f}?'.format(1./n_samples*n_outliers, nu, 1./n_samples*n_SV))

# %% [markdown] {"deletable": true, "editable": true}
# Only the support vectors are involved in the decision function of the One-Class SVM.
#
# 1. Plot the level sets of the One-Class SVM decision function as we did for the true density.
# 2. Emphasize the Support vectors.

# %% {"deletable": true, "editable": true}
plt.figure()
plt.contourf(xx, yy, Z_ocsvm, 10, cmap=plt.cm.Blues_r)
plt.scatter(X[:, 0], X[:, 1], s=1.)
plt.scatter(X_SV[:, 0], X_SV[:, 1], color='orange')
plt.show()

# %% [markdown]
# <div class="alert alert-success">
#     <b>EXERCISE</b>:
#      <ul>
#       <li>
#       **Change** the `gamma` parameter and see it's influence on the smoothness of the decision function.
#       </li>
#     </ul>
# </div>

# %%
# # %load solutions/22_A-anomaly_ocsvm_gamma.py

# %% [markdown] {"deletable": true, "editable": true}
# ## Isolation Forest
#
# Isolation Forest is an anomaly detection algorithm based on trees. The algorithm builds a number of random trees and the rationale is that if a sample is isolated it should alone in a leaf after very few random splits. Isolation Forest builds a score of abnormality based the depth of the tree at which samples end up.

# %% {"deletable": true, "editable": true}
from sklearn.ensemble import IsolationForest

# %% {"deletable": true, "editable": true}
iforest = IsolationForest(n_estimators=300, contamination=0.10)
iforest = iforest.fit(X)

# %% {"deletable": true, "editable": true}
Z_iforest = iforest.decision_function(grid)
Z_iforest = Z_iforest.reshape(xx.shape)

plt.figure()
c_0 = plt.contour(xx, yy, Z_iforest,
                  levels=[iforest.threshold_],
                  colors='red', linewidths=3)
plt.clabel(c_0, inline=1, fontsize=15,
           fmt={iforest.threshold_: str(alpha_set)})
plt.scatter(X[:, 0], X[:, 1], s=1.)
plt.show()

# %% [markdown]
# <div class="alert alert-success">
#     <b>EXERCISE</b>:
#      <ul>
#       <li>
#       Illustrate graphically the influence of the number of trees on the smoothness of the decision function?
#       </li>
#     </ul>
# </div>

# %%
# # %load solutions/22_B-anomaly_iforest_n_trees.py

# %% [markdown] {"deletable": true, "editable": true}
# # Illustration on Digits data set
#
#
# We will now apply the IsolationForest algorithm to spot digits written in an unconventional way.

# %% {"deletable": true, "editable": true}
from sklearn.datasets import load_digits
digits = load_digits()

# %% [markdown] {"deletable": true, "editable": true}
# The digits data set consists in images (8 x 8) of digits.

# %% {"deletable": true, "editable": true}
images = digits.images
labels = digits.target
images.shape

# %% {"deletable": true, "editable": true}
i = 102

plt.figure(figsize=(2, 2))
plt.title('{0}'.format(labels[i]))
plt.axis('off')
plt.imshow(images[i], cmap=plt.cm.gray_r, interpolation='nearest')
plt.show()

# %% [markdown] {"deletable": true, "editable": true}
# To use the images as a training set we need to flatten the images.

# %% {"deletable": true, "editable": true}
n_samples = len(digits.images)
data = digits.images.reshape((n_samples, -1))

# %% {"deletable": true, "editable": true}
data.shape

# %% {"deletable": true, "editable": true}
X = data
y = digits.target

# %% {"deletable": true, "editable": true}
X.shape

# %% [markdown] {"deletable": true, "editable": true}
# Let's focus on digit 5.

# %% {"deletable": true, "editable": true}
X_5 = X[y == 5]

# %% {"deletable": true, "editable": true}
X_5.shape

# %% {"deletable": true, "editable": true}
fig, axes = plt.subplots(1, 5, figsize=(10, 4))
for ax, x in zip(axes, X_5[:5]):
    img = x.reshape(8, 8)
    ax.imshow(img, cmap=plt.cm.gray_r, interpolation='nearest')
    ax.axis('off')

# %% [markdown] {"deletable": true, "editable": true}
# 1. Let's use IsolationForest to find the top 5% most abnormal images.
# 2. Let's plot them !

# %% {"deletable": true, "editable": true}
from sklearn.ensemble import IsolationForest
iforest = IsolationForest(contamination=0.05)
iforest = iforest.fit(X_5)

# %% [markdown] {"deletable": true, "editable": true}
# Compute the level of "abnormality" with `iforest.decision_function`. The lower, the more abnormal.

# %% {"deletable": true, "editable": true}
iforest_X = iforest.decision_function(X_5)
plt.hist(iforest_X);

# %% [markdown]
# Let's plot the strongest inliers

# %% {"deletable": true, "editable": true}
X_strong_inliers = X_5[np.argsort(iforest_X)[-10:]]

fig, axes = plt.subplots(2, 5, figsize=(10, 5))

for i, ax in zip(range(len(X_strong_inliers)), axes.ravel()):
    ax.imshow(X_strong_inliers[i].reshape((8, 8)),
               cmap=plt.cm.gray_r, interpolation='nearest')
    ax.axis('off')

# %% [markdown]
# Let's plot the strongest outliers

# %% {"deletable": true, "editable": true}
fig, axes = plt.subplots(2, 5, figsize=(10, 5))

X_outliers = X_5[iforest.predict(X_5) == -1]

for i, ax in zip(range(len(X_outliers)), axes.ravel()):
    ax.imshow(X_outliers[i].reshape((8, 8)),
               cmap=plt.cm.gray_r, interpolation='nearest')
    ax.axis('off')

# %% [markdown]
# <div class="alert alert-success">
#     <b>EXERCISE</b>:
#      <ul>
#       <li>
#       Rerun the same analysis with all the other digits
#       </li>
#     </ul>
# </div>

# %%
# # %load solutions/22_C-anomaly_digits.py
