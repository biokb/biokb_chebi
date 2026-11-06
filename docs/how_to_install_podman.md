# How to install Podman

=== "Windows"

    Follow the instruction on [Podman for Windows](https://github.com/podman-container-tools/podman/blob/main/docs/tutorials/podman-for-windows.md)

=== "macOS"
    1. Download [Podman macOS Installer](https://podman.io/)
    2. Create and start your first Podman machine:
        ```bash
        podman machine init
        podman machine start
        ```
    3. Verify the installation by running:
        ```bash
        podman info
        ```

=== "Debian/Ubuntu"

    1. Install Podman using your package manager. For example, on Ubuntu:
        ```bash
        sudo apt update
        sudo apt install podman -y
        ```
    2. Verify the installation by running:
        ```bash
        podman --version
        ```
        
=== "Fedora"

    1. Install Podman using your package manager. For example, on Fedora:
        ```bash
        sudo dnf install podman -y
        ```
    2. To run the machine ...
       ```bash
       sudo dnf -y install podman-machine
       ```
    slirp4netns is no longer the default for rootless networking on new podman installations, obsoleted in favor of passt. If you have containers using slirp4netns, make sure slirp4netns is installed:
       ```bash
       sudo dnf -y install slirp4netns
       ```