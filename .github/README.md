# City Building Library

This library generates realistic city road layouts in a non-planned style, by adding junctions and roads iteratively from the main roads to the leaves. Users can vary at each generation the road curvature, probabilities of junction creation and random (or not) number generation, to alter the look-and-feel of the layout.

![](https://gcrossland.github.io/CityBuilder/radius800-000.sm.gif) ![](https://gcrossland.github.io/CityBuilder/radius200to800.sm.gif)

Interface documentation can be directly found in the library file, [libraries/citybuilder.py](../libraries/citybuilder.py), in Javadoc-esque documentation comments.

## Licence

The content of the CityBuilder repository is free software; you can redistribute it and/or modify it under the terms of the [GNU General Public License](http://www.gnu.org/licenses/gpl-2.0.txt) as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

The content is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

## Quick Start

*   The library depends on [Tst](https://github.com/gcrossland/Tst). Prepare to use this first.
*   Ensure that the contents of [libraries](../libraries) is available on PYTHONPATH e.g. `export PYTHONPATH=/path/to/CityBuilder/libraries:${PYTHONPATH}`.
*   Run the tests by running [Tst](https://github.com/gcrossland/Tst)'s runtsts.py utility from the working directory (or archive) root.
*   The library also comes with some testing demos, demonstrating how radial roads vary with different random number generators and how city growth patterns vary with radius. The demos emit [XPM version 2](https://en.wikipedia.org/wiki/X_PixMap#XPM2) images to the current directory; these can be combined into animated GIFs with the GIMP-based xpm-to-gif.sh utility.
    ```shell
    ./angle-demo.py
    for rng in ConstantRng LinearRng Random
    do
      ./xpm-to-gif.sh 24 angle-${rng}-*.xpm && rm angle-${rng}-*.xpm
    done
    ```
    ```shell
    ./growth-demo.py
    ./xpm-to-gif.sh 0.5 radius*-999.xpm && rm radius*-999.xpm && mv radius*-999.xpm.gif radius200to800.xpm.gif
    for rad in 200 300 400 500 600 700 800
    do
      ./xpm-to-gif.sh 0.5 radius${rad}-*.xpm && rm radius${rad}-*.xpm
    done
    ```
