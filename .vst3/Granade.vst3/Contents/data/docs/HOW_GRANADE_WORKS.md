# How Granade Works

Here are some notes on how Granade's code is organized. 

### Top-Level Directories

* `src` contains all the source code, including all the source code for the JUCE framework
* `data` contains audio files for the plugin to load
* building the project creates a new directory called `build`, which will contain the compiled executables, libraries, and plugins. See [Building](../../README.md#building-from-source)

### Terminology

This is a list of terms that will be used to mean specific things in this file, which may be commonly understood to mean something different. Other older and less centralized documentation in this codebase may use these terms differently. Attempts have been made to note equivalent terminology that is prominently used elsewhere.

* **translation unit**: refers to either a source file in this codebase that is meant to be passed to a compiler, or the resulting compiled binary. Used interchangeably with **module**. When referring to a binary, equivalent to **target**.
* **plugin**: the translation unit that contains the core application logic (responding to input, updating state, outputting render data and audio samples). Does not require linking with any libraries (including the C standard library). Not a complete audio plugin by itself. Must be loaded by a backend.
* **backend**: any translation unit that is not the plugin. Backends load the plugin. Used interchangeably with **host**. Often synonymous with platform.
* **platform**: a more loosely-defined term that usually means operating system, possibly combined with a machine code architecture, but also occasionally refers to a host environment such as a DAW or web browser. Could be extended to include embedded systems or game consoles as well in the future.
* **interface**: a collection of functions that are intended to be called from a translation unit without necessarily being defined in that translation unit. The translation unit that implements the functions in the interface is said to **export** or **expose** that interface. May also be called an **API**.

### Translation Units

* `plugin.so/dll/dylib`: a dynamic library containing all of the plugin's audio-visual output logic. Compiled from `plugin.cpp`. 
* `Granade.exe`: a simple native host application for the dynamic library plugin, capable of hot-reloading. Compiled from `main.cpp`. 
* `Granade.vst3`: a vst plugin that loads the dynamic library plugin. Compiled from `PluginProcessor.cpp` and `PluginEditor.cpp`.
* `wasm_glue.wasm`: a WebAssembly module that allows the plugin code to be run in the browser. Exposes a different interface from the plugin's which is easier to call into from javascript. Compiled from `wasm_glue.cpp`.

### Other Important Files

* `common.h` includes all code and data structures shared between the plugin and its various backends, as well as the interfaces each module exports.
* `common.api.h` defines the functions that the host exports for the plugin to use. Enables the plugin to perform file io, memory allocation, atomic operations, and math functions.
* `plugin.api.h` defines the functions that the plugin exports for the host to use. Enables the host to render the interface and process audio.
* `platform.h` is a small OS abstraction layer used by the native host and vst backends.

## How it Works

* at startup, the host application (the native host, a DAW, the JUCE plugin host, etc.) opens a window with an OpenGL context, connects to audio input and output devices, and loads the dynamic libarary plugin.
* the dynamic library plugin exposes three functions: `initializePluginState()` initializes the plugin's internal state, `renderNewFrame()` responds to keyboard/mouse input and outputs vertex data for the new video frame, and `audioProcess()` processes audio input and outputs samples to fill the audio output buffer.
* at runtime, the host calls the plugin functions. It passes them memory to store state, OS-dependent functions for things like file io and interlocked/atomic operations, and input information. It then copies the audio samples to the output device, and calls OpenGL to render the vertex data.
* all the logic for displaying an interactive UI, updating the state, and outputting audio is contained in the dynamic library. It has no dependencies besides the interface the host exposes, so porting Granade to another platform merely requires implementing a backend for this interface and doing something with the data the plugin functions output.
* in debug builds, the native host hot-reloads the the dynamic library plugin when it is recompiled. Thus you can edit the plugin, recompile it, and see the changes instantly without having to close and reopen the application window or otherwise manually retrigger a reload.
