import os
import numpy as np

import platform

from phy import IPlugin
from pathlib import Path

class ControllerSettings(IPlugin):
    def attach_to_controller(self, controller):
        controller.n_spikes_features = 15000
        controller.n_spikes_waveforms = 300
        @controller.supervisor.connect
        def on_create_cluster_views():
            @controller.supervisor.add_column
            def FiringRate(cluster_id):
                return '%.2f Hz' % (len(controller._get_spike_times(cluster_id, 'None').data) / controller.model.duration)
            @controller.supervisor.add_column
            def HorzPos(cluster_id):
                channel_id = controller.get_best_channel(cluster_id)
                return controller.model.channel_positions[channel_id][0]
            my_file = Path("channel_shanks.npy")
            if my_file.is_file():
                @controller.supervisor.add_column
                def Shank(cluster_id):
                    def _load_channel_shanks(self):
                        return self._read_array('channel_shanks')
                    channel_shanks = _load_channel_shanks(controller.model)
                    channel_id = controller.get_best_channel(cluster_id)
                    return channel_shanks[channel_id]
