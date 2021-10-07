# Super Import (SPIO)

> only support windows now (I don't have mac or linux computer)

SPIO is a blender addon that allow you to copy and paste to import model. 

Currently we can not drag and drop to import model in blender, but with this addon, you can easily copy your model/Image in your File Explorer, then paste in blender with just one click/shortcut!

Import model / image never so easily in blender before.

## Feature

> SPIO have a config system for advance import. Normally, you wont need to add even one config to import model like .obj/.fbx./.dae/.usd.
>
> But if you want to use your own addon(Like Better Fbx), or your own operator, SPIO's config system make sense.

### 1.Custom extension / operator

You are allow to assign a operator to import a certain types of file.

Just need to fill in the `extension` with your file suffix (like obj), and copy and paste the python command to the `Operator Idenfitier`.

<img src="res/img/image-20211007110357103.png" alt="image-20211007110357103" style="zoom: 80%;" />

Though the operator identifier will auto correct the itself, you are still need to pay attention to the format.

Right: `import_mesh.stl`

Error: `bpy.ops.import_mesh.stl(prop = value)`

### 2.Operator Property

You are allow to set most of the property of  your custom operator with a prop list. 

![image-20211007110540728](res/img/image-20211007110540728.png)

### 3.Config Filter

If you have hundreds of config, you can search and filter it with both extension / config name.

![image-20211007110306654](res/img/image-20211007110306654.png)

### 4.Import / Export Config

Config can be import or export with json file.

It will look like this. 

```json
{
    "config name": {
        "extension": "stl",
        "bl_idname": "import_mesh.stl",
        "prop_list": {
            "global_scale": 1,
            "axis_up": "Z"
        }
    }
}
```



## Settings

+ Force Unicode:

  force the encoding to be 'utf-8' . If you enable the same option in your windows languages settings, check it，else not.

  <img src="res/img/1.png" alt="1" style="zoom:50%;" />

+ Report time

  a small to for compare custom operator running time