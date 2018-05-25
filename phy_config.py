
# You can also put your plugins in ~/.phy/plugins/.

from phy import IPlugin

try:
    import phycontrib
except:
    pass

# Plugin example:
#
# class MyPlugin(IPlugin):
#     def attach_to_cli(self, cli):
#         # you can create phy subcommands here with click
#         pass

c = get_config()
c.Plugins.dirs = [r'~/.phy/plugins/']#C:/Users/peter/Dropbox/PhyPlugins/plugins/
c.TemplateGUI.plugins = ['ControllerSettings','Recluster']
c.KwikGUI.plugins = ['ControllerSettingsKwik']
