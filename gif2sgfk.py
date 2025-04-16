import argparse
import os
from PIL import Image
# A Note from the verbose author TheNomCognom - 16/04/2025

# This script was made for personal use, use it for free and modify as you wish. I'm sure it can be 
# imporved and tuned for your own needs or just because can be refactored, no credit or mentions needed. 
# It's barely tested, so each case worked but not corner cases used. 
# It was made as i needed to improve animations for SGDK project. 

# What do you need? just a gif with your animation. Generate it online, with aseprite, freeaseprite or whatever.
# Be sure that the gif has the palette you need - changing palette manually on a bunch of images is a pain in the as* 
# Be sure that the gif is 8x8 divisible to avoid modifying outputs to be usable for SGDK

# What does? Takes a gif as input and generates one of 2 options. 

# Option 1: 
# if you choose --imageres/-ir A set of png images for each frame of the input gif, a resources.res with the images included and a .c file with 
# an array with te images indexed. Myabe you don't need it, but i do ;) See options on the command line for details.
# see commandline help for details as there is compression arg for the .res generation

# Option 2:
# if you choose --spriteres/-sr A png containing each frame of the animation will be generated, you can choose -hz for horizontal output
# or -vz for vertical and a resources.res with the spirte included as well. 
# If the gif is 16x8px the -hz out will be 16*<#gif frames>x8px
# If the gif is 16x8px the -hz out will be 16x8*<#gif frames>px
# see commandline help for details as there are compression and speed args for the .res generation

# Case of use (mine) See example folder, as it there are typical final folder states for each option.
# 1. create your animation with some keyframes - nointerpolated.gif
# 2. use https://github.com/n00mkrad/flowframes to interpolate frames between them using nointerpolated.gif -> generated interpolated.gif
# 3. run the script as you need: 
#    Set of png - one per gif frame - with the result saved on ./ and base name for each file anim, compression FAST
#    $  python3 gif2sgdk.py -ir -g examples/imageres/interpolated.gif -op ./examples/imageres/ -bn newinterpolated_ -c NONE
#
#    A png with all gif frames, with the result saved on ./ 
#    base name for each file "anim", compression FAST, animation speed 2, horizontal 
#    
#    $ gif2sgdk.py -ir -g nointerpolated.gif -op ./ -bn anim -c FAST -sp 2 -hz
#
# NOTE: --compression/-c --speed/-sp are just for the .res generated file.

# The best way to know how it works is to run it ;) 


def extract_frames_with_transparency(gif_path):
    im = Image.open(gif_path)
    palette = im.getpalette()
    transparency_index = im.info.get('transparency')
    if transparency_index is not None and palette:
        transparent_color = tuple(palette[transparency_index * 3:transparency_index * 3 + 3])
    else:
        transparent_color = None

    frames = []
    try:
        while True:
            frame = im.convert('RGBA')
            if transparent_color:
                datas = frame.getdata()
                new_data = []
                for item in datas:
                    if item[:3] == transparent_color:
                        new_data.append((0, 0, 0, 0))
                    else:
                        new_data.append(item)
                frame.putdata(new_data)
            frames.append(frame.copy())
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return frames

def save_imageres(frames, output_dir, base_name, compression):
    os.makedirs(output_dir, exist_ok=True)
    res_lines = []
    c_array_lines = []

    # Get base palette from first frame
    base_palette_image = frames[0].convert('P', dither=Image.NONE, palette=Image.ADAPTIVE, colors=16)
    base_palette = base_palette_image.getpalette()
    while base_palette and base_palette[-3:] == [0, 0, 0]:
        base_palette = base_palette[:-3]

    for i, frame in enumerate(frames):
        filename = f"{base_name}_{i:04d}.png"
        path = os.path.join(output_dir, filename)

        # Convert to 8-bit using base palette
        pal_frame = frame.convert('RGB').quantize(palette=base_palette_image)
        pal_frame.putpalette(base_palette)
        pal_frame.save(path, transparency=0)

        res_lines.append(f"IMAGE {base_name}_{i:04d} \"{filename}\" {compression} ALL")
        c_array_lines.append(f"    &{base_name}_{i:04d}")

    with open(os.path.join(output_dir, "resources.res"), "w") as f:
        f.write("\n".join(res_lines))

    with open(os.path.join(output_dir, f"{base_name}_array.c"), "w") as f:
        f.write(f"Image * {base_name}[{len(frames)}] = {{\n")
        f.write(",\n".join(c_array_lines))
        f.write("\n};\n")

def save_spriteres(frames, output_dir, base_name, compression, speed, vertical):
    os.makedirs(output_dir, exist_ok=True)
    width, height = frames[0].size
    if vertical:
        sprite_sheet = Image.new("RGBA", (width, height * len(frames)))
        for i, frame in enumerate(frames):
            sprite_sheet.paste(frame, (0, i * height))
    else:
        sprite_sheet = Image.new("RGBA", (width * len(frames), height))
        for i, frame in enumerate(frames):
            sprite_sheet.paste(frame, (i * width, 0))

    # Convert sprite sheet to P mode using palette from first frame
    palette_image = frames[0].convert('P', dither=Image.NONE, palette=Image.ADAPTIVE, colors=16)
    palette = palette_image.getpalette()
    while palette and palette[-3:] == [0, 0, 0]:
        palette = palette[:-3]

    palette_image.putpalette(palette)
    sprite_sheet = sprite_sheet.convert('RGB').quantize(palette=palette_image)
    sprite_sheet.info['transparency'] = 0

    sprite_filename = f"{base_name}.png"
    sprite_path = os.path.join(output_dir, sprite_filename)
    sprite_sheet.save(sprite_path, transparency=0)

    tiles_width = width // 8
    tiles_height = height // 8

    with open(os.path.join(output_dir, "resources.res"), "w") as f:
        f.write(f"SPRITE {base_name} \"{sprite_filename}\" {tiles_width} {tiles_height} {compression} {speed}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Convert GIF to SGDK image or sprite resources",
        epilog="Example:\n  python gif2sgdk.py --imageres --gif anim.gif --outpath ./ --basename animation_ --compression FAST\n  python gif2sgdk.py --spriteres --gif anim.gif --outpath ./ --basename spritesheet --compression FAST --speed 0",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--imageres', '-ir', action='store_true')
    mode.add_argument('--spriteres', '-sr', action='store_true')
    parser.add_argument('--gif', '-g')
    parser.add_argument('--outpath', '-op')
    parser.add_argument('--basename', '-bn')
    parser.add_argument('--compression', '-c', choices=['NONE', 'FAST', 'BEST'])
    parser.add_argument('--speed', '-sp', type=int, default=0)
    parser.add_argument('--horizontal', '-hz', dest='horizontal', action='store_true')
    parser.add_argument('--vertical', '-vz', dest='vertical', action='store_true')
    args = parser.parse_args()

    if not (args.gif and args.outpath and args.basename):
        if args.imageres:
            parser.error("the following arguments are required: --gif/-g, --outpath/-op, --basename/-bn")
        elif args.spriteres:
            parser.error("the following arguments are required: --gif/-g, --outpath/-op, --basename/-bn, --compression/-c")

    if args.horizontal and args.vertical:
        parser.error("--horizontal and --vertical are mutually exclusive")

    frames = extract_frames_with_transparency(args.gif)
    if args.imageres:
        save_imageres(frames, args.outpath, args.basename, args.compression)
        print(f"[✓] Generated {len(frames)} individual PNGs, resources.res IMAGE mode and array c file.")
    elif args.spriteres:
        vertical = args.vertical or not args.horizontal  # Default to vertical if not specified
        save_spriteres(frames, args.outpath, args.basename, args.compression, args.speed, vertical)
        print(f"[✓] Generated sprite sheet with {len(frames)} frames and resources.res en modo SPRITE.")

if __name__ == '__main__':
    main()

