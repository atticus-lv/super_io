> SPIO is an auxiliary blender plug-in, used to improve the efficiency of users importing blend file model pictures from outside
>
> Currently supports windows platform

### Quick Start

The use of SPIO is very simple.<br>

**Import**

After installing the plug-in from the preferences and enabling it, you only need to copy the file from the windows explorer `Ctrl+C`, and in the 3d view `Ctrl+Shift+V` can import the file. 

SPIO allows **single/batch** to import all the formats included in the default import menu, and can also support additional import of the detailed categories of blend files. 

For non-model files (or unrecognized formats) SPIO treats them as images

In the **3D view**, you can choose to import it as a reference or image plane

In the **shading editor** and **geometry node editor**, import it as an image texture node

**Export**

After selecting the model in the 3D view, press `Ctrl Shift C` to pop up the export menu. After selecting an exporter, the export file will be pasted to the clipboard (supports Windows, macOS platform to be tested), available in Resources Paste files directly with `Ctrl V` in the manager

> SPIO allows a single object to export selected objects, supports all formats included in the default export menu, and can be exported as a single blend file format<br>For the image on the image editor, you can choose to export it as a PNG file, Or paste the pixels to the clipboard (the two functions only support win, I hope more mac users will assist in the development)

### Customize

SPIO allows highly customized import config to meet complex import requirements

For specific usage methods, please refer to [Config Manage](/ConfigManage.md)



