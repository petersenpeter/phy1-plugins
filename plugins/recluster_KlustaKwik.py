import logging
import os
import numpy as np

import platform

from phy import IPlugin
from pathlib import Path
from subprocess import Popen

from phy.utils.tempdir import TemporaryDirectory
from scipy.cluster.vq import kmeans2, whiten

logger = logging.getLogger(__name__)

try:
    from klusta.launch import cluster2
except ImportError:  # pragma: no cover
    logger.warn("Package klusta not installed: the KwikGUI will not work.")
try:
    import pandas as pd
except ImportError:  # pragma: no cover
    logger.warn("Package pandas not installed.")

class ReclusterKlustaKwik(IPlugin):
    def attach_to_controller(self, controller):
        @controller.supervisor.connect
        def on_create_cluster_views():
            @controller.supervisor.actions.add(shortcut='alt+r')
            def Recluster():
                def write_fet(fet, filepath):
                    with open(filepath, 'w') as fd:
                        #header line: number of features
                        fd.write('%i\n' % fet.shape[1])
                        #next lines: one feature vector per line
                        for x in range(0,fet.shape[0]):
                            fet[x,:].tofile(fd, sep="\t", format="%i")
                            fd.write ("\n")
                        #np.savetxt(fd, fet[0], fmt="%i", delimiter=' ')

                def read_clusters(filename_clu):
                    clusters = load_text(filename_clu, np.int32)
                    return process_clusters(clusters)
                def process_clusters(clusters):
                    return clusters[1:]
                def load_text(filepath, dtype, skiprows=0, delimiter=' '):
                    if not filepath:
                        raise IOError("The filepath is empty.")
                    with open(filepath, 'r') as f:
                        for _ in range(skiprows):
                            f.readline()
                        x = pd.read_csv(f, header=None,
                            sep=delimiter).values.astype(dtype).squeeze()
                    return x
                
                """Relaunch KlustaKwik on the selected clusters."""
                # Selected clusters.
                cluster_ids = controller.supervisor.selected
                spike_ids = controller.selector.select_spikes(cluster_ids)
                logger.info("Running KlustaKwik on %d spikes.", len(spike_ids))
                # s = controller.supervisor.clustering.spikes_in_clusters(cluster_ids)
                data3 = controller.model._load_features().data[spike_ids]
                fet2 = np.reshape(data3,(data3.shape[0],data3.shape[1]*data3.shape[2]))
                #logger.warn(str(fet2[0,:]))
                dtype = np.int32
                factor = 2.**31
                factor = factor/np.abs(fet2).max()
                fet2 = (fet2 * factor).astype(dtype) 
                # fet2 = convert_dtype(fet2, np.int32)
                # logger.warn(str(fet2[0,:]))

                # Run KK2 in a temporary directory to avoid side effects.
                # n = 10
                # spike_times = controller.model.spike_times[spike_ids]*controller.model.sample_rate

                #spike_times = convert_dtype(spike_times, np.int32)
                # times = np.expand_dims(spike_times, axis =1)
                
                # fet = 1000*np.concatenate((fet2,times),axis = 1)
                fet = fet2

                name = 'tempClustering'
                shank = 3
                mainfetfile = os.path.join(name + '.fet.' + str(shank))
                write_fet(fet, mainfetfile)
                if platform.system() == 'Windows':
                    program = 'C:/Users/peter/klustakwik.exe'
                else:
                    program = '/Users/peterpetersen/klustakwik/KlustaKwik'
                
                cmd = [program, name, str(shank)]
                cmd +=["-UseDistributional",'0',"-MinClusters",'2',"-MaxClusters",'12']

                # Run KlustaKwik.
                p = Popen(cmd)
                p.wait()
                # Read back the clusters
                spike_clusters = read_clusters(name + '.clu.' + str(shank))
                controller.supervisor.split(spike_ids, spike_clusters)
                logger.warn("Reclustering complete!")

            @controller.supervisor.actions.add(shortcut='alt+k')
            def K_means_clustering():
                """Cut Clusters by means of K-means clustering"""
                # Selected clusters.
                logger.warn("Running K means clustering...")
                cluster_ids = controller.supervisor.selected

                spike_ids = controller.selector.select_spikes(cluster_ids)
                s = controller.supervisor.clustering.spikes_in_clusters(cluster_ids)
                data = controller.model._load_features()
                data3 = data.data[spike_ids]
                data2 = np.reshape(data3,(data3.shape[0],data3.shape[1]*data3.shape[2]))
                logger.warn("Whitening the PCAs")
                whitened = whiten(data2)
                logger.warn("Running Kmeans")
                clusters_out,label = kmeans2(whitened,2)
                controller.supervisor.split(s,label)
                logger.warn("K means clustering complete")

            @controller.supervisor.actions.add(shortcut='alt+x')
            def MahalanobisDist(): #()
                """Remove outliers defined by the mahalanobis distance."""
                # Selected clusters.
                logger.warn("Removing outliers by Mahalanobis distance...")
                def MahalanobisDistCalc2(x, y):
                    covariance_xy = np.cov(x,y, rowvar=0)
                    inv_covariance_xy = np.linalg.inv(covariance_xy)
                    xy_mean = np.mean(x),np.mean(y)
                    x_diff = np.array([x_i - xy_mean[0] for x_i in x])
                    y_diff = np.array([y_i - xy_mean[1] for y_i in y])
                    diff_xy = np.transpose([x_diff, y_diff])
                    md = []
                    for i in range(len(diff_xy)):
                        md.append(np.sqrt(np.dot(np.dot(np.transpose(diff_xy[i]),inv_covariance_xy),diff_xy[i])))
                    return md

                def MahalanobisDistCalc(X, Y):
                    rx = X.shape[0]
                    cx = X.shape[1]
                    ry = Y.shape[0]
                    cy = Y.shape[1]

                    m = np.mean(X, axis=0)
                    M = np.tile(m,(ry,1))
                    C = X - np.tile(m,(rx,1))
                    Q, R = np.linalg.qr(C)
                    ri,ri2,ri3,ri4 = np.linalg.lstsq(np.transpose(R),np.transpose(Y-M))
                    d = np.transpose(np.sum(ri*ri, axis=0)).dot(rx-1)
                    return d

                cluster_ids = controller.supervisor.selected
                spike_ids = controller.selector.select_spikes(cluster_ids)
                s = controller.supervisor.clustering.spikes_in_clusters(cluster_ids)
                data = controller.model._load_features()
                data3 = data.data[spike_ids]
                data2 = np.reshape(data3,(data3.shape[0],data3.shape[1]*data3.shape[2]))
                logger.warn("Calculating the Mahalanobis distance")
                if data2.shape[0] < data2.shape[1]:
                    logger.warn("Error: Not enought spikes in the cluster!")
                    return

                MD = MahalanobisDistCalc(data2,data2)
                threshold = 10**2
                outliers  = np.where(MD > threshold)[0]
                outliers2 = np.ones(len(s),dtype=int)
                outliers2[outliers] = 2
                # outliers  = MD > threshold
                logger.info("Outliers detected: %d.", len(outliers))
                controller.supervisor.split(s,outliers2)
                logger.warn("Mahalanobis outlier removal complete")
