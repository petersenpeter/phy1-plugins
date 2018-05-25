import os
import numpy as np

import platform

from phy import IPlugin
from pathlib import Path

class ControllerSettingsKwik(IPlugin):
    def attach_to_controller(self, controller):
        controller.n_spikes_features = 15000
        controller.n_spikes_waveforms = 300
        @controller.supervisor.connect
        def on_create_cluster_views():
            @controller.supervisor.add_column
            def FiringRate(cluster_id):
                return '%.2f Hz' % (len(controller._get_spike_times(cluster_id, 'None').data) / controller.model.duration)