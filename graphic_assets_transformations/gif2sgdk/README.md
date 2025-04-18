## A Note from the verbose author TheNomCognom - 16/04/2025

This script was made for personal use, use it for free and modify as you wish. I'm sure it can be 
imporved and tuned for your own needs or just because can be refactored, no credit or mentions needed. 
It's barely tested, so each case worked but not corner cases used. 
It was made as i needed to improve animations for SGDK project. 

## What do you need? 
What do you need? just a gif with your animation. Generate it online, with aseprite, freeaseprite or whatever.

Be sure that the gif has the palette you need - changing palette manually on a bunch of images is a pain in the as* 

Be sure that the gif is 8x8 divisible to avoid modifying outputs to be usable for SGDK

## What does? 
Takes a gif as input and generates one of 2 options. 

### Option 1: 
if you choose --imageres/-ir A set of png images for each frame of the input gif, a resources.res with the images included and a .c file with an array with te images indexed. Myabe you don't need it, but i do...

see commandline help for details as there is compression arg for the .res generation

### Option 2:
if you choose --spriteres/-sr A png containing each frame of the animation will be generated, you can choose -hz for horizontal output or -vz for vertical and a resources.res with the spirte included as well. 

If the gif is 16x8px the -hz out will be 16*<#gif frames>x8px

If the gif is 16x8px the -hz out will be 16x8*<#gif frames>px

see commandline help for details as there are compression and speed args for the .res generation


###
###
### Case of use (mine) See example folder, as there are typical final folder states for each option. Running those commands will generate new files
    1. create your animation with some keyframes - nointerpolated.gif
    2. use https://github.com/n00mkrad/flowframes to interpolate frames between them using nointerpolated.gif -> generated interpolated.gif
    3. run the script as you need: 


    Ex: Set of png - one per gif frame - with the result saved on ./ and base name for each file anim, compression FAST

```shell
    $ python3 gif2sgdk.py -ir -g examples/imageres/interpolated.gif -op ./examples/imageres/ -bn newinterpolated_ -c NONE
```

    Ex: A png with all gif frames, with the result saved on ./ 
    base name for each file "anim", compression FAST, animation speed 2, horizontal 

```shell    
    $ python3 gif2sgdk.py -sr -g  examples/spriteres/interpolated.gif -op ./examples/spriteres/ -bn newspritesheet_ -c NONE -sp 2 -hz
```
### NOTE: 
--compression/-c --speed/-sp are just for the .res generated file.


The best way to know how it works is read and run ;)