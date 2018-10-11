import logging
import os
import numpy as np

import platform

from phy import IPlugin
from pathlib import Path
from subprocess import Popen

logger = logging.getLogger(__name__)

try:
    from klusta.launch import cluster2
except ImportError:  # pragma: no cover
    logger.warn("Package klusta not installed: the KwikGUI will not work.")
try:
    import pandas as pd
except ImportError:  # pragma: no cover
    logger.warn("Package pandas not installed.")
try:
    from phy.utils.config import phy_config_dir
except ImportError:  # pragma: no cover
    logger.warn("phy_config_dir not available.")

class Export2neurosuite(IPlugin):
    def attach_to_controller(self, controller):
        @controller.supervisor.connect
        def on_create_cluster_views():
            @controller.supervisor.actions.add(shortcut='alt+o')
            def export_shank_info_and_clu_files():
                logger.warn("Exporting shanks, peak_channels and cluster_ids for all units to a .npy files")
                my_file = Path("channel_shanks.npy")
                if my_file.is_file():
                    def _load_channel_shanks(self):
                        return self._read_array('channel_shanks')
                    path, filename = os.path.split(controller.model.dat_path)
                    filename = filename[:-4]
                    logger.warn(filename)
                    channel_shanks = _load_channel_shanks(controller.model)
                    cluster_ids = controller.supervisor.clustering.cluster_ids
                    spike_cluster_index = controller.supervisor.clustering.spike_clusters
                    shanks = []
                    peak_channel = []
                    for x in range(0, len(cluster_ids)):
                        channel_id = controller.get_best_channel(cluster_ids[x])
                        shanks.append(channel_shanks[channel_id].astype(int))
                        peak_channel.append(channel_id)
                    # logger.warn(str(shanks))
                    # Saving both the shank id and the unit id as two separate files
                    np.save('shanks.npy', shanks)
                    np.save('cluster_ids.npy', cluster_ids)
                    np.save('peak_channel.npy', peak_channel)

                    logger.warn("Export of shank info complete. Now exporting Neurosuite files")
                    kcoords2 = np.unique(shanks)

                    for kcoords3 in kcoords2:
                        logger.warn('Exporting .clu.' + str(kcoords3))
                        temp = (shanks == kcoords3).nonzero()
                        ia = np.in1d(spike_cluster_index,cluster_ids[temp])
                        clu = spike_cluster_index[ia]
                        clufile = filename + '.clu.' + str(kcoords3)
                        unique_clusters = len(np.unique(clu))
                        np.savetxt(clufile, np.concatenate(([unique_clusters],clu.astype(int)), axis=0), delimiter="\n", fmt='%i')
                    logger.warn("Export of .clu files complete.")

                else:
                    logger.warn("channel_shanks.npy does not exist and is required for the export.")
                    logger.warn("The .npy file is created when running Kilosort with the KilosortWrapper")
