# Changelog

All notable changes to Granade will be documented in this file.

## [0.2.0] - 2025-11-TBD
- Added WebAssembly target
- Updated renderer to OpenGL 3.3 / WebGL2
- Reduced memory footprint significantly
- Added a build configuration interface
- Added control tooltips
- Removed all dependence on the C runtime library from the plugin
- Added support for statically linking the plugin library
- Added a rudimentary profiler
- Fixed a bug where the logger's lock was not taken when flushing the log

## [0.1.0] - 2025-06-01

### Added
- Initial release of Granade granular synthesizer
- Real-time granular synthesis engine
- Cross-platform support (Windows, macOS, Linux)
- Standalone application with microphone input
- JUCE-based VST3 plugin support for DAW integration
- OpenGL-based graphics native application
- Basic grain parameter controls && grain visualization
- ...
<!-- list of things carried out so far - consider as a more detailed feature list. --I personaly like this example : https://github.com/adamstark/AudioFile?tab=readme-ov-file#versions -->

### Known Issues
- File loading interface not implemented
- Some UI controls are non-functional
- VST3 automatic installation may not work on all systems
- Linux hot-reloading occasionally crashes
- ..

