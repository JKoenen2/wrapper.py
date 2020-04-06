# Design Goals #
- Quick setup
- Robust, stable, set-it-and-forget-it design
    - Wrapper should always be able to start without user input (e.g. with a physical server boot)
    - Updates to Wrapper should never intrude or require user input to fix problems
    - Resilient to corruption, should repair itself
- No excess of functionality; only bare bone features will be implemented
- As few dependencies needed to operate
- Plugin API, to supplement any specific features or use cases not built into the wrapper
- Python 2.x and 3.x compatible

# Major To-Do #

- [x] Wrapper shuts down on first start, to allow user to edit generated config file
    - Eventually, interactive first-time setup

- [PARTIAL] Implement backup system
    - [x] Support various containers (zip, tar, 7z, etc.) and compression methods (gzip, etc.)
    - [x] Don't backup if server has been in stopped state
    - [x] Option to stop backup if no players have logged in
    - [ ] Automatic world rollback through dashboard
- [x] Implement shell script calls
- [x] Implement dashboard using Flask
    - [ ] Multi-user support with permissions
- [ ] Implement locales, potentially
- [ ] Implement plugin API
    - [ ] Server object
        - [ ] Minecraft object
        - [ ] World object
        - [ ] Player object
        - [ ] (if proxy mode is implemented) Entity object
- [ ] Implement server.properties hijacking (temporarily replace server.properties with custom values before starting server, and putting original one back after server booted)
- [ ] (Very Low Priority) Implement Proxy mode

# Minor/Specific To-Do List #
- [x] Auto-accept EULA
- [x] Automatically turn on gamerule to hide command runs from ops, to prevent chat spam
- [ ] Server
    - [x] MCServer object's life should only be during the server's life; once the server stops, the MCServer object should be destroyed. A new one should be created when the server is started again
    - [x] Decouple console parsing from MCServer
    - [ ] Throttle server start attempts if failing to start (i.e. invalid CLI arguments, wrong server jar name, etc.)
    - [ ] Respect arguments
    - [ ] Respect auto-restart
    - [x] Custom java executable
- [ ] log_manager
    - [PARTIAL] Rotate logs
    - [x] Compress old logs using gzip
    - [x] Respect debug-mode settings
- [ ] Backups
    - [x] Purge old backups
    - [ ] Respect ingame-notification settings
    - [x] Console commands for controlling backups
    - [x] Cancel ongoing backup
- [ ] Dashboard
    - [ ] Localize MaterializeCSS dependencies (don't use CDN)
- [ ] Plugins
    - [x] Events need to unhook upon plugin reload
    - [ ] Commands need to un-register upon plugin reload
    - [ ] Rename player.message to something else, so that player.message can be used to send the player a message
- [ ] Make {"text":""} objects universally encoded

# Plugin Ideas #
- [ ] Essentials Clone
- [ ] IRC bridge plugin
