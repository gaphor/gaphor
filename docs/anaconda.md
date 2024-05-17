# Gaphor in Anaconda

Sometimes, it may be helpful to call gaphor functionality from a python console on computers without the ability for a full development install (e.g., without administrative privileges). In these cases, gaphor can be installed as a package in an anaconda environment using the following process:


## Create new anaconda environment

If you use anaconda for other projects, it's a good idea to create a new environment for gaphor, since many of its dependencies can conflict with common packages like spyder. To do this, run the following command from anaconda prompt:

```
conda create -n "gaphor"
conda activate gaphor
```
where ``gaphor'' can be any name desired for the environment.

## Update packages in the new environment

Get the most recent packages using:

```
conda update --all
```

## Install dependencies

The following gaphor dependencies are installable from anaconda:
```
conda install -c conda-forge gobject-introspection gtk4 pygobject pycairo hicolor-icon-theme adwaita-icon-theme
```
Unfortunatley, the `gtksourceview5` and `libadwaita` dependencies are not available as anaconda packages. So you may not be able to fully build/run the program in this environment.

## Set up your development environment

Now, to develop with gaphor, you will want to set it up with your development. If you want to work with `ipython`, install it below:
```
conda install ipython ipykernel
```
### VSCode Tips
VSCode should work out-of-the box if it is already installed. Just set 'gaphor' as the kernel in your VSCode Profile or notebook.

### Spyder Tips
You can install spyder in this environment using `conda install spyder`.

If this does not work, (i.e., if `conda install spyder` reveals conflicts), you can instead use the following workaround:
```
conda install spyder-kernels=2.4
```
Then, in spyder, set 'gaphor' as your python interpreter

## Install gaphor

From a python console running within your new anaconda environment, you may then install gaphor using pip:

```
pip install gaphor
```