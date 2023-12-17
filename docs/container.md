# Gaphor in a Container

Instead of setting up a development environment locally, the easiest way
to contribute to the project is using GitHub Codespaces.

## GitHub Codespaces

Follow these steps to open Gaphor in a Codespace:
1. Navigate to https://github.com/gaphor/gaphor
1. Click the Code drop-down menu and select the **Open with Codespaces** option.
1. Select **+ New codespace** at the bottom on the pane.

For more info, check out the [GitHub documentation](https://docs.github.com/en/free-pro-team@latest/github/developing-online-with-codespaces/creating-a-codespace#creating-a-codespace).

## Remote access to Gaphor graphic window with Codespaces

When using Codespaces, chances are that you also want to interact with the
graphical window of Gaphor.

This is facilitated in Gaphor by use of container feature called [desktop-lite](https://github.com/devcontainers/features/tree/main/src/desktop-lite). This feature is activated by default in the Gaphor's [devcontainer.json](https://github.com/gaphor/gaphor/blob/main/.devcontainer/devcontainer.json) file.

Notice the webPort/vncPort and password values. These are used in subsequent steps.
```
    		"desktop-lite": {
			"password": "vscode",
			"webPort": "6080",
			"vncPort": "5901"
		},
```



There are two options:
### Using a local VNC viewer
1. Download and install VNC viewer of your choice (e.g. realvnc)
1. Specify remote hostname as *localhost* and port as *5901* and connect VNC. The port number should be same as specified in attribute *vncPort*
1. Upon [debugging/running](https://github.com/gaphor/gaphor/blob/main/.devcontainer/devcontainer.json) Gaphor the familiar Graphic window should be displayed in VNC view

### Using noVNC viewer on the Browser
1. This is based on [noVNC](https://novnc.com/info.html) application
1. Open the browser on your local machine and give address as *http://127.0.0.1:6080/*. The port number should be same as specified in attribute *webPort*
1. A noVNC window will open, click on Connect and provide password as *vscode*. The password should be same as specified in attribute *password*
1. Upon [debugging/running](https://github.com/gaphor/gaphor/blob/main/.devcontainer/devcontainer.json) Gaphor the familiar Graphic window should be displayed in noVNC view on Browser
