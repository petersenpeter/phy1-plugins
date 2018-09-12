# Plugins to Phy 
These plugins add additional features to Phy

## Features
* Reclustering. Reclustering with KlustaKwik 2.0 - dependent on a local version of KlustaKwik, which is provided in the zip file for Windows 10) and python package: pandas. To install write “pip install pandas” in the terminal in your phy environment.
* Outlier removal using the Mahalanobis distance. Standard threshold is 16 standard deviations (adjustable).
* K-means clustering. Standard separation into two clusters (adjustable).
* Export shank info for each unit. This is necessary if you want to know which shank a given unit was detected on.

All new features are accessible from the top menu labeled clustering.

## ControllerSettings - Extra columns in ClusterView
* Firing rate
* Horizontal position
* Shank number (dependent on the rezToPhy.m version in the KiloSortWrapper)

ControllerSettings also allows you to adjust the number of spike displayed i FeatureView (increased to 15,000) and WaveformView (standard: 300). I recommend to delete the local .phy folder in your data folder, when adjusting these parameters.

## Installation 
To install, place the content in your plugins directory (~/.phy/), replacing the existing files and plugins folder.
