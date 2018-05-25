# Plugins to Phy 
The plugins add additional columns and features to Phy

## Features
* Reclustering. Reclustering with KlustaKwik 2.0 - dependent on a local version of KlustaKwik, which is provided in the zip file for Windows 10) and python package: pandas. To install write “pip install pandas” in the terminal in your phy environment.
* Outlier removal using the Mahalanobis distance. Standard threshold is 10 standard deviations.
* K-means clustering. Standard separation into two clusters.
* Export shank info for each unit.

All new features are accessible from the top menu labeled clustering.

## ControllerSettings - Extra columns in ClusterView
*Firing rate
*Horizontal position
*Shank number (dependent on the rezToPhy.m version in the KiloSortWrapper)

Adjusting number of spike displayed i FeatureView and WaveformView (delete the local .phy folder located in your data folder, when adjusting these parameters)

## Installation 
To install, copy the files to your plugins directory (~/.phy/), replacing the existing files and plugins folder.
