2.19.4
------
(unreleased)

2.19.3
------
- Windows: Fix missing toolbar icons
- Fix loading of ProxyPorts with informationFlow attached
- Fix to resolve CSS style variables before using the values

2.19.2
------
- Add SysML Requirements trace derived unions
- Fix Parameter Node and Execution Specification with Dark mode
- Scale parameter nodes to contain long names
- Lenient derived unions
- Fix segfault by reverting Gtk.ListVew for Parameters
- Fix connect interaction fragments
- chore: clean up deprecated properties from UIComponent
- Add Python 3.12 Support, Update Poetry to version 1.5.1
- Apply security best practices to GitHub Actions
- Create a Security Policy and Run Scorecard Checks
- Only use mature translations for released versions of Gaphor
- Update Spanish, Hungarian, and Finnish translations
- Fix scaling of Activity Parameter nodes

2.19.1
------
- Fix: order is preserved when undoing a change
- Actions: ObjectNode now also connects to decision/merge and join/fork nodes.
- Fix: ports should be nested under properties
- Experimental: support for plugins
- Add fullscreen mode with F11
- Remove Tkinter from packaging

2.19.0
------
- Dropped support for AppImage
- Add Information Flow support for Associations
- Interactions: fixed DnD for partially connected messages
- Restore CSS auto-complete
- Docs: A coffee machine tutorial has been added
- Make model loading more lenient to model corruption
- CLI: export diagrams and run scripts within Gaphor
- Enable PyPI Trusted Publisher
- Replace deprecated Gtk.TreeView with ListView: Activity Parameter Nodes
- Use consistent naming for element_factory in storage module
- Use new style Dropdowns for selecting items in property editor
- Updates to translations

2.18.1
------
- Make operations visible on Blocks
- A quick fix for crashes in the CSS editor, disable autocomplete
- Fix doc translation catalogs not found
- Fix encoding warnings for no encoding argument
- Update AppImage build with GTK 4.10
- Add non-goals to README
- Enable translation of docs, and add Crotian, German, and Dutch
- Updates to most translations and add Tamil

2.18.0
------
- Support for manually resolving Git merge conflicts
- Drop support for GTK3, bundle macOS with GTK4
- Enable middle-click mouse scrolling of diagrams
- Support for changing the spoken language in a model
- Add diagrams in diagrams
- Upgrade development build to GNOME 44
- Clean up application architecture for copy service
- Css editor dark mode
- macOS: update notarize, staple, and cert actions
- Just load modules for gaphor.modules entry points
- Finnish, Dutch, Spanish, Polish, Portuguese (BRA) translation update
- Toggle the "no tabs" background based on notebook activity
- Fix drag from model browser
- Fix orthogonal lines during copy/paste
- Update diagram directly when partitions change
- Make main window always available to avoid warnings

2.17.0
------
- Add support for diagram metadata
- macOS: Fix freeze creating new diagram
- Properly unsubscribe when property page is removed
- Package GSettings daemon schemas for AppImage
- Consider only default modifiers in toolbox shortcuts
- New status page icon
- Workaround removing skip-changelog labels
- Update gvsbuild to version 2023.2.0
- meta: Add .doap-file
- Update "Keep model in sync" design principle
- Update to using the GNOME Code of Conduct
- Add Polish translation
- Spanish, Dutch, Croatian, Turkish, and German Translation Updates

2.16.0
------
- Automatic switching to dark mode in diagrams
- Add Model browser multi select and popup menu
- Refactor and improve model browser
- Use normal + icon for new diagram dropdown
- Add support for CSS variables and named colors
- Apply development mode for dev releases
- Show diagram name in header
- Show something when no diagrams are opened
- Fix the packaged data dirs
- Stabilize macOS/GTK tests
- Add a comments option to our documentation
- Split tips in to multiple labels
- Win and macOS: Fix wrong language selected when region not default
- Fix translation warning never logged with missing mo files
- Spanish, Russian, Hungarian, Czech translation update

2.15.0
------
- Add basic git merge conflict support by asking which model to load
- Improvements to CSS autocomplete with function completion
- Insert colons, spaces, and () automatically for CSS autocomplete
- Use native file chooser in Windows
- Fix translations not loading in Windows, macOS, and AppImage
- Fix PyInstaller versionfile parse error with pre-release versions
- Update CI to publish to PyPI after all other jobs have passed
- Replace pytest-mock with monkeypatch for tests
- Fix PEP597 encoding warnings
- Fix regression that caused line handles to not snap to elements
- Add Turkish, and update French, Russian, and Swedish translations
- Remove translation Makefile

2.14.2
------
- Fix macOS release failed

2.14.1
------
- Add autocompletion for CSS properties
- Fix coredumps on Flatpak
- Hide New Package menu unless package selected
- Update Getting Started pages
- Spanish translation update

2.14.0
------
- Simplify the greeter and provide more info to new users
- New element handle and toolbox styles
- Use system fonts by default for diagrams
- Add tooltips to the application header icons
- Make sequence diagram messages horizontal by default
- Make keyboard shortcuts more standard especially on macOS
- macOS: cursor shortcuts for text entry widgets
- Load template as part of CI self-test
- Update docs to make it more clear how to edit CSS
- Switch doc style to Furo
- Add custom style sheet language
- Support non-standard Sphinx directory structures
- Continue to make model loading and saving more reliable
- Move Control Flow line style to CSS
- Do not auto-layout sequence diagrams
- Use new actions/cache/(save|restore)
- Remove querymixin from modeling lists
- Improve Windows build reliability by limiting cores to 2
- Croatian, Hungarian, Czech, Swedish, and Finnish translation updates

2.13.0
------
- Auto-layout for diagrams
- Relations to actors can connect below actor name
- Export to EPS
- Zoom with Ctrl+scroll wheel works again
- Recent files is disabled if none are present
- Windows and AppImage are upgraded to GTK4
- Update packaging to use Python 3.11
- Many GTK4 improvements: About window, diagram tabs, message dialogs
- Ensure toolbox is always visible
- Add additional tests around architectural rules
- Many translation updates and bug fixes

2.12.1
------
- Fix/move connected handle
- Fix error when disconnecting line with multiple segments
- Fail CI build if Windows certificate signing fails
- namespace.py: Actually set properties for rectangle
- Update Shortcuts window

2.12.0
------
- GTK4 is now the default for Flatpak; Windows, macOS, and AppImage still use GTK3
- Save folder is remembered across save actions
- State machine functionality has been expanded, including support for regions
- Resize of partition keeps actions in the same swimlane
- Activities (behaviors) can be assigned to classifiers
- Stereotypes can be inherited from other stereotypes
- Many GTK4 fixes: rename, search, instant editors
- Many translation updates

2.11.0
------
- Add Copy/Paste for GTK4
- Make dialogs work with GTK4
- Fix instant editors for GTK4
- Update list view for GTK4
- Make SysML Enumerations also ValueTypes
- Add union types
- Let Gaphor check for its own health
- Add error reports window
- Add element to diagram by double click
- Ensure all models are saved with UTF-8 encoding
- Fix states can't transition to themselves
- Fix unlinking elements from the model
- Fix issue with fully pasting a diagram
- Fix scroll speed for touch screens
- Fix codeql warnings and error
- Improve text placement for Associations
- Enable additional pre-commit hooks
- Add example in docs of color for comments using CSS
- Hungarian translation updates

2.10.0
------
- Pin support for activity diagram
- Add Activity item to diagram
- Allow to drag and drop all elements from tree view to diagram
- Codegen use all defined modeling languages
- Fix diagram dependency cycle
- Add Skip Duplicate Action and Release-Drafter Permissions
- Update permissions for CodeQL GitHub Action
- Include all diagram items in test model
- Fix GTK4 property page layouts
- Use official RAAML logo in greeter
- Relation metadata to allow better reuse
- Rename relationship connector base classes
- Add design principles to docs
- French, Finnish, Croatian translation update

2.9.2
-----
- Fix Windows build

2.9.1
-----
- Fix bad release of version 2.9.0
- Cleanup try except blocks and add more f-strings

2.9.0
-----
- Separate Control and Object Flow
- Automatically select dark mode for macOS and Windows
- Automatically Enable Rename Prompt for Newly Created Diagrams
- New group function for element grouping
- Simulate user behavior with Hypothesis and fix uncovered bugs
- Proxyport: update ports when proxyport is moved
- Fix AppImage Crashes on Save Command
- Improve reconnect for relationships
- Update connection behavior for Association
- Enable preferences shortcut
- Rename Component Toolbox to Deployment
- Update Finnish, Spanish, Croation, and German translatio

2.8.2
-----
- Fix splitting of lines
- Update README to reflect new functionality
- Add additional strings to translations
- Update Hungarian, Spanish, and Finnish translations

2.8.1
-----
- Fix Gaphor fails to load when launched in German
- Simplify the greeter dialogs
- Update Hungarian, Finnish, and Chinese (Simplified) translations

2.8.0
-----
- Add diagram type support
- Improve the welcoming experience with a greeter window and starting templates
- Add a Magnet-tool
- Support SysML Item flow
- Stereotypes for ItemFlow properties
- Full Copy/Paste of model elements
- Allow for deleting elements in the tree view
- Allocation of structural types to swimlane partitions
- User notification when model elements are automatically removed
- Store toolbox settings per modeling language
- Grow item when an item is dropped on it
- Add "values" compartment to Block item and set a minimal height for compartments
- Support empty square bracket notation in an Operation
- New code generator
- Fix AppImage GLIBC Error on Older Distro Versions
- Fix Sequence diagram loading when message is close to lifeline body
- Support for loading .gaphor files directly from the macOS Finder
- Fix positions of nested items during undo
- Fix ownership of Connector, ProxyPort, and ItemFlow
- Improve GTK4 compatibility
- Improve clarity of syntax for attributes and operations using a popover
- Clean up Toolbox and remove some legacy code
- Invert association creation
- Ensure model consistency on save and fork node loading fixes
- Core as a separate ModelingLanguage
- Use symbolic close icon for notebook tabs
- Update to latest gvsbuild, switch to wingtk repo
- Spanish, Hungarian, Finnish, Dutch, Portuguese, Croation, Espanian, and Galician translations updates
- Add Chinese (Simplified) translation

2.7.1
-----
- Fix lines don't disconnect when moved
- No GTK required anymore for generating docs
- Update Python to 3.10.0
- Spanish translation updates

2.7.0
-----
- Add Reflexive Message item for Interactions
- Allow messages to move freely on Lifeline and ExecutionSpec
- Pop-up element name editor on creation of a new element
- Add option to show underlying DecisionNode type
- Add InformationFlow for Connectors
- Swap relationship direction for Generalization, Dependency, Import, Include, and Extend
- Use Jedi for autocomplete in the Python Console
- Sphinx directive for embedding Gaphor models into docs
- Fix lifeline ordering when not all items are linked in a diagram
- Allow generalizations to be reused
- Allow auto-generated elements (Activity, State Machine, Interaction, Region) to be removed
- Fix Windows build by updating to Python 3.9.9
- Emit events for Diagram.ownedPresentation and Presentation.diagram after element creation
- Show underlying DecisionNode type
- Add documentation dependencies to pyproject.toml
- Move enumeration layout to UML.classes
- Rename packaging to _packaging
- Remove names for initial/final nodes
- Update to latest gvsbuild
- Update to PyInstaller 4.6
- Add gtksourceview to Windows docs
- Fix Python 3.10 warnings
- Fix indentation in Style Sheet docs
- Expand the number of strings translated
- Hungarian, Spanish, Japanese, Finnish, and Croatian translation updates

2.6.5
-----
- Update style sheet editor to be a code editor
- Update strings to improve ability to translate
- Ensure all relationships are brought to top
- Fix errors in Italian translation which prevented model saving
- Add association end properties to editor pane
- Restore rename right click option to diagrams in tree view
- Add Japanese translation
- Update Hungarian, Croatian, and Spanish translations

2.6.4
-----
- Fix Flatpak build failure by reverting to previous dependencies

2.6.3
-----
- Fix about dialog logo
- Add translation of more elements
- Remove importlib_metadata dependency
- Simpler services for about dialog
- Up typing compliance to 3.9, and remove typing_extensions
- Finnish translation updates

2.6.2
-----
- Fix localization of UI files
- Fix icons in dark mode
- Update Spanish, Finnish, Hugarian, and Portuguese (Br) translations

2.6.1
-----
- Display guard conditions in square brackets
- Use flat buttons in the header bar
- Fix translation support
- Fix drag and drop of elements does not work on diagrams
- Fix parameter is incorrect error with ";;" in path
- Fix fork/join node incorrectly rotates
- Fix close button on about dialog doesn't work in Windows
- Fix wrong label is displayed when object node ordering is enabled
- Improve inline editor undo/redo behavior
- Fixed closing of about dialog
- Add VSCode debug instructions for Windows
- Rename usage of Partitions to Swimlanes
- Update Dutch and Hungarian Translations
- Croatian translation updates
- Simplify attribute and enumeration lookup

2.6.0
-----
- Improve zoom and pan for mouse
- Add Finnish, Galician, Hungarian, and Korean, update Spanish translations
- Fix disappearing elements from tree view on Windows
- Convert CI from mingw to gvsbuild
- Upgrade Windows Build Script from Bash to Python
- Refactor GitHub Actions to use composite actions
- Add translations for UI files
- Add information flows to UML model
- Add extra rules to avoid cyclic references
- Fix typo in UML.gaphor
- Refactor class property pages in to multiple modules
- Fix Windows and other developer documentation updates
- Enable pyupgrade
- Update the README for Flatpak string translation
- Fix documentation build errors, update dependencies

2.5.1
-----
- Fix app release signing in Windows and macOS

2.5.0
-----
- Add initial support for STPA in RAAML
- Add support for notes in property pages and attributes
- Allow for diagrams to be nested under all elements
- Fix delete and undo of a diagram
- Rename C4ContainerDatabaseItem to C4DatabaseItem
- Cleanup model loading
- Change diagram item management to the element factory
- Organize and simplify element events
- Cleanup toolbox and diagram action code

2.4.2
-----
- Fix AttributeError when creating composite associations
- Add tooltips for A and S in attribute editor
- Improve drag and drop for TreeView
- Started to add support for GTK4
- Upload Linux assets during release automatically
- Sign only builds on the master branch

2.4.1
-----
- Fix reordering attributes and operations with drag and drop

2.4.0
-----
- Add support for DataType, ValueType, Primitive, and Enumeration
- Model state is stored per model, restores where you left off
- Add support for Containment Relationship
- Focus already opened model when opening a model file
- Remove the New From Template option
- Upgrade toolbox to be compatible with GTK 4
- Add regression tests
- Fix build fails when GitHub Actions secrets are not available
- Fix association direction arrow is not updated

2.3.2
-----
- Fix issue where ornaments were not show on associations
  after loading a model

2.3.1
-----
- Fix scrollbars cause the diagram to disappear
- Update Italian translation
- Left align the toolbox header labels

2.3.0
-----
- Add support for C4 model
- Add support for Fault Tree Analysis with RAAML
- Update the UML data model to align closer to version 2.5.1
- Enable arrow keys to expand and collapse namespace tree
- Allow Gaphor profiles to be copy and pasted between models
- Improve diagram drawing and scrolling speed
- Add Croatian translation
- Remove gray borders around editable text
- Complete converting all tests to pytest
- Fix guides are misaligned when top-left handle is moved
- Update development environment instructions
- Fix undo and redo does not set attributes
- Fix selection lasso is in the wrong place after scrolling

2.2.2
-----
- Fix undo of deleted elements
- Fix requirements are missing ID and text
- Add CSS styling to dropzone and grayed out elements
- Start to remove use of inline styles

2.2.1
-----
- Fix drawing of composite association

2.2.0
-----
- Guide users to create valid relationships
- macOS builds are signed and notarized
- New app icon
- Improvements to copy and paste, and undo robustness
- Fix RuntimeError caused by style sheet creation
- Use EventControllers from GTK 3.24

2.1.1
-----
- Fix copy and paste in Linux with Wayland

2.1.0
-----
- Improve swimlane behavior
- Add auto select in tree view
- Add in-app notifications
- Improve file load and save dialogs
- Show more elements and relationships in namespace tree
- Update Italian translation
- Make lifelines and messages owned by interactions

2.0.1
-----
- Fix Gaphor fails to launch in macOS
- Use certificate to sign Windows binaries
- Fix copy/paste issue that causes association ends to be removed
- Improve editing for inline editors (popovers)
- Fix undo on diagram items corrupts the model
- Fix UML composite and shared association tools

2.0.0
-----
- Add initial support for SysML
- Add support for styling using CSS
- Translate to Italian
- Improve dmg for macOS
- Improve Copy/Paste for nested items
- Add new modeling language service
- Show the element editor by default
- Create completely new data model code generator
- Add part and shared associations to tool palette
- Remove unused imports, enable flake8 checks
- Update App icons
- Update animation gif in README
- Fix Windows Build Errors caused by Missing ZST Archives
- Fix installation on Windows
- Add extra diagram item tests
- Fix macOS Python version problem
- Place UML model and diagram items closer together
- Refactor Code Generator to New Module and add CLI
- Fix MSYS2 package names and disable system update
- Remove CI workaround for console plugin
- Move core modeling concepts to a separate package
- Convert Some Profile Tests to Pytest
- Speed up text rendering
- Fix tree view text to allow names with angle brackets
- Clear the clipboard when diagram items are copied
- Fix name change for activity partitions
