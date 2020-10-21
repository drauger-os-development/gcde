# Plugins
Plugin support is in-progress. Expect bugs and inconsistent behavior.

## Basics

There are 3 types of plugins:

 * Foreground Plugins
 * Background Plugins
 * Multi-threaded Plugins

Foreground Plugins are basic Tiles that provide basic functionality and run in the main thread.
These plugins are easiest to make if you overwrite the Tile.run() function.

Background Plugins do not need to use the Tile library.
They allow more advanced functionality, but have no GUI component.
These plugins CAN be multithreaded, but if no GUI component is present,
it is still considered a Background Plugin.

Multi-threaded Plugins have both a background and foreground component.
They will have a GUI Tile that provides much more advanced functionality, such as
system, memory, or network usage; app indicators; messaging clients built into Tiles;
and more!


## Recognition
In order for your plugin to be recognized, it must be registered in`__init__.py`. Otherwise, it will not be imported and used. It may be registered under whatever name you desire, except `example`. This name is reserved for the example plugin and is ignored in most circumstances.

## Expected Objects

### `plugin_type`
`plugin_type` defines what type of Plugin this is for GCDE. Every plugin MUST have this variable be publicly available.

 * 0 = Foreground Plugin
 * 1 = Background Plugin
 * \>= 2 = Multi-Threaded Plugin
 
This also lets GCDE know how many threads to make. GCDE will pass the thread
number to `run()` so that you can determine which thread does what.


### `run()`
**Foreground Plugins do not need a `run()` function, as GCDE does not anticipate there being one.**

This `run()` function is used as an entry point for forking off Background and Multi-Threaded Plugins.

#### args
`run()` receives a single integer as its argument. This integer indicates the thread number `run()` is running as. It is _NOT A PID_.



### `plugin_setup()`
**ALL** plugins **MUST** have this function. If no setup is needed for your plugin, you can do the following definition:

```python

def plugin_setup(settings):
	pass
```

#### args
`plugin_setup()` receives a dictionary as it's argument, `settings`.
The `settings` variable contains either location settings (if a Foreground Plugin), global settings (Background Plugin),
or both (Multi-Threaded Plugin). If both, location settings will be under `settings["loc"]`
global settings will be under `settings["global"]`

Settings are passed to `plugin_setup()` by value, not by reference. So, attempting
to edit global settings from within a plugin will not affect a running GCDE
instance.
