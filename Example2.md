### Usage scenarios

> There is a designer who needs to shade and render two chair from the client (given models are shown in the figure) <br>The customer sent some reference pictures of cloth, hoping that he could make some materials for him to compare. <br>The designer gave the client screenshots of chairs made of different materials.  <br>The client finally finalized two kinds of materials and put forward the following requirements:
>
> a. Each chair shows two materials,solo in one image (four image in total),<br>b. Combine 2 chairs in one image (different materials)

<img src="media/img/example2/1.png" alt="1" width="1080px" />

<!-- panels:start -->

<!-- div:title-panel -->

### Concluded requirement and Set Variants

Because of the large number of case variables, we will use variant and set variant nodes to manage the scene without copying the chair

<!-- div:right-panel -->

> [!NOTE]
>
> 
>
> | name/variants input | input 0 | input 1 |
> | ------------------- | ------- | ------- |
> | chair 1 display     | true    | false   |
> | chair 2 display     | true    | false   |
> | chair 1 position    | middle  | side    |
> | chair 2 position    | middle  | side    |
> | chair 1 material    | mat 1   | mat2    |
> | chair 2 material    | mat 1   | mat2    |
>
> After a brief summary of the varieties<br> it is found that the position of the chair is related to the display of the chair
>
> | name/variants input                 | input 0                     | input 1             | input 2             |
> | ----------------------------------- | --------------------------- | ------------------- | ------------------- |
> | chair display<br>(display,position) | all chair<br />left / right | chair 1<br />middle | chair 2<br />middle |

<!-- div:left-panel -->

<img src="media/img/example2/3.png" alt="3" width="1080px" />

Use object display node, object PSR node and object material node respectively

#### Variant: chair display

<img src="media/img/example2/4.png" alt="4" width="1080px" />

#### Variants: chair 1&2 material 

<img src="media/img/example2/5.png" alt="5" width="720px" />

<!-- panels:end -->



### Set the preview task

1. connect the set variant node

2. change the activation value in the set variant node to change the used variant input

Now you can continue to preview and adjust the position and material of the chair

<img src="media/img/example2/6.png" alt="6" width="1080px" />

### Ready for one click rendering

 use the RSN help menu to quickly set the rendering list and output path

<img src="media/img/example2/7.png" alt="7" width="720px" />

So far, the entire node tree has been set

<img src="media/img/example2/8.png" alt="8" width="1080px"/>

### Render Result

<img src="media/img/example2/9.png" alt="9" width="720px" />