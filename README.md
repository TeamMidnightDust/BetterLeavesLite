# Motschen's Better Leaves: Lite
A more optimized version of my Better Leaves pack aiming to be the best-performing of all, while still looking spectacular.

### In which ways is this more optimized than the regular version?
Glad you asked.
First of all, the leaf models use way less elements in comparison, as the round textures are generated in advance instead of being faked as round during rendering.

### Does it also outperform packs made by other authors?
Yes, probably.
Most other packs use two seperate textures: one for the regular part of the leaves and one for the bushy part.
This is generally not a problem, since Minecraft bakes textures into an atlas (a big texture containing all the smaller block textures), to avoid constant texture rebinds.
However, using two textures in a model can still cause some overhead, as the game has to locate the coordinates of both on the atlas.
Additionally, the atlas size might have to be increased to fit two textures per leaf block – also resulting in performance loss.

This pack mitigates this by just replacing the regular leaf texture with one round version, which contains the default texture in the middle.

### Are there any downsides?
As with everything good, there are a couple caviats, but don't worry, as I've designed the pack with them in mind.

The first is the fact that – compared to the regular pack – there is no compatibility with texturepacks that feature custom leaf textures.
You can however easily build your own version of the pack with custom textures by using the script included in this repo (see more below).
This should also work with higher-res textures, though your mileage may wary.

The second downside is that mod-support always has to be explicitly added, while the regular version has basic support for all mods using the vanilla leaf model as a base.
Though I aim to solve this over time by just adding that explicit support, also resulting in better quality than the basic support would bring.

## Building versions for your texturepack (or mod)
To build your own version, simply download this repository and replace the textures in the input/assets folder with those of your texturepack.
Then, make sure you've installed Python (available for every OS).
After that, simply open a terminal in the main directory and run `python3 gen-pack.py <YOUR VERSION NAME>`
Tada! You should now have a zip file ready for use. Have fun :)