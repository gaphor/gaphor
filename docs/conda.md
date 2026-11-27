# Developing with Conda Workspaces

[Conda workspaces](https://github.com/conda-incubator/conda-workspaces) provide a cross-platform development environment for Gaphor without system package managers. Conda-forge supplies the dependencies, including GTK4, libadwaita, and gtksourceview. The `conda.lock` file pins versions for Linux, macOS, and Windows.

## Why use Conda workspaces?

- Use the same setup on Linux, macOS (Apple Silicon), and Windows
- Get GTK4, libadwaita, and other C libraries from conda-forge without installing system packages
- Keep the environment in the project directory, separate from global packages
- The `self` feature installs Gaphor in editable mode

## Prerequisites

- **Conda** (Miniconda or Miniforge); see the [install guide](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
- **conda-workspaces plugin** (required for `conda task` commands)

### Install the conda-workspaces plugin

```bash
# If you use Miniforge:
conda self install conda-workspaces

# If you use Miniconda:
conda install -n base conda-forge::conda-workspaces --override-frozen
```

## Setup instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/gaphor/gaphor.git
   cd gaphor
   ```

2. **Run the development task**
   ```bash
   conda task run dev
   ```

   The task:
   - Creates a conda environment in `.conda/envs/default` or reuses an existing one
   - Installs dependencies from `conda.lock`, including GTK4, libadwaita, gtksourceview, and Python packages
   - Runs `conda pypi install -e .` to install Gaphor in editable mode
   - Launches Gaphor

   Later runs reuse the environment and start faster.

## Configuration

The workspace is defined in `pyproject.toml` under `[tool.conda]`:

| Section | Purpose |
|---------|---------|
| `[tool.conda.workspace]` | Channels (`conda-forge`) and target platforms (`linux-64`, `osx-arm64`, `win-64`) |
| `[tool.conda.dependencies]` | Conda dependencies including GTK4, libadwaita, Python packages |
| `[tool.conda.environments]` | Default environment includes the `self` feature |
| `[tool.conda.feature.self]` | Editable install of the local Gaphor package |
| `[tool.conda.tasks]` | `dev` task runs `gaphor` after `_install-self` |

## Available tasks

| Task | Command | Description |
|------|---------|-------------|
| `dev` | `conda task run dev` | Install Gaphor in editable mode and launch the application |

You can list all tasks with:
```bash
conda task list
```

## Updating the environment

When `conda.lock` or `pyproject.toml` changes:
```bash
conda workspace install
```
Conda workspaces will detect the changes and update the environment automatically.

## Troubleshooting

`conda task` not found
- Ensure you installed the `conda-workspaces` plugin (see Prerequisites)

## Further reading

- [Conda workspaces documentation](https://github.com/conda-incubator/conda-workspaces)
- [Gaphor contributing guide](contribute.md)
