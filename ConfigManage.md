### Add/Remove/Copy

> Note that you need to save the blender preferences to keep the newly added config in the plug-in<br>Or use the export config command to export the config to a json file to prevent loss

##### Add

<img src="media/img/cn/1.png" alt="1" style="zoom: 80%;" />

Just click ➕ next to the list to complete the addition of custom configs.

After adding the config, you can specify the name, prompt, applicable format, and operator type for the config

<img src="media/img/cn/0.png" alt="0" style="zoom:67%;" />

Different configs can be for the same extension, when multiple configs conflict（Use [Match Rule](/ImportConfig.md) to avoid
conflict），A selection menu will pop up for the user to select the corresponding config to import.<br>The config name and
prompt will be used as the **button name** and **button tips** on this

<img src="media/img/cn/img.png" alt="img" style="zoom:67%;" />

##### Remove

Click ➖ to remove the currently selected config.
<br>This operation cannot be undone, so be cautious.

If you accidentally delete and cut and turn on the automatic saving preferences option, you can immediately close the
current blender (do not save)

##### Copy

opy the currently selected config and paste it into the new config

### Config import and export

<img src="media/img/cn/2.png" alt="2" style="zoom:67%;" />

Use the export config command to export all currently checked configs to a json file.
<br>If you check the export all option on the side, the existing configs in the config list will be exported
<img src="media/img/cn/5.png" alt="5" style="zoom:50%;" />

Use the import configuration command to import the file config exported by the above operation and add it to the list
<br>*If a config with the same name already exists, it will be ignored*

### Search & match

SPIO provides a rich filtering system to ensure that you can quickly find the config you want to edit

<img src="media/img/cn/3.png" alt="3" style="zoom: 67%;" />

+ Show import/Show export: display import configuration display export configuration

+ Name: The name of the search config (default)

+ Extension: Search for config matching the extension (file format)

  <img src="media/img/cn/6.png" alt="6" style="zoom: 67%;" />

+ Rule: search configured rule type

  <img src="media/img/cn/7.png" alt="7" style="zoom:67%;" />

+ Color Tag: Search for the config that matches the current color (the default is colorless)

  <img src="media/img/cn/4.png" alt="4" style="zoom:67%;" />

