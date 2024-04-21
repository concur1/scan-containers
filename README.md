# scan-containers

Script to create and scan nix containers.

The script will:
- Create one or more nix files that will be used to build one or more container images.
- Create and load those container images.
- Run grype on those container images.
- Run grype on a extra list of container images.

## How to run:

1. Update the scan-containers.py file with the nix package and channel you want to examine.
2. With nix installed run: `nix-shell`
3. In the nix shell run `python scan-containers.py`
4. Check the `image_data` for csv's detailing the vulnerabilities for each image.
