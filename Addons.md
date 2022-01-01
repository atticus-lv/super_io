SPIO 1.35 provides houdini/Cinema 4d script for win platform, which can interact with blender
### houdini

##### Installation

1. Click `Get Houdini Script` in the settings/addons, select import or export script
2. Enter houdini, create a new tool and paste the script, you can specify the tiff icon from the SPIO for houdini folder of the addons
3. Complete the settings of the two tool scripts and assign shortcut keys

##### Instructions
+ Import
  1. Copy model files
  2. In Network Editor, use shortcut keys to paste under the SOP level
    + If no file node is selected, a new file node is generated
    + If a file node is selected, set file node's parm `file` with the path of the first file in the selected file<br>
       and the remaining path will add a new file node and specify

+ Export
  1. In the Network Editor, select single or multiple nodes under the SOP level
  2. Use shortcut keys to export (each node will be exported as a separate file, then copy to clipboard)


### Cinema 4d

##### Installation

1. Click `Get Cinema 4d Script` in the settings addons
2. Enter Cinema 4d, `shift c` search script folder
3. After popping up the user script folder, paste files
4. Restart Cinema 4d, `shift F12` search for spio, assign shortcut keys

##### Instructions
+ Import & Export
Use Short-Cut to import export