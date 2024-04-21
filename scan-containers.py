import subprocess

file_template = """
{pkgs ? import <nixos-${{channel}}> {}
, pkgsLinux ? import <nixpkgs> { system = "x86_64-linux"; }
}:

pkgs.dockerTools.buildImage {
    name = "${{package}}";
    tag = "nix-${{channel}}-latest";
    copyToRoot = pkgs.buildEnv {
      name = "image-root";
      pathsToLink = [ "/bin" ];
      paths = [
        pkgs.${{package}}
      ];
    };
    config = {
    Cmd = [ "${pkgs.python39}/bin/${{bin_name}}" ];
    };
 }
"""
params = [
    {
        "package": "python39",
        "bin_name": "python",
        "channel": "stable",
    },
    {
        "package": "python39",
        "bin_name": "python",
        "channel": "unstable",
    },
]

for param in params:
    image = f"{param.get('package')}:nix-{param.get('channel')}-latest"
    with open(
        f"nix-image/{param.get('package')}-{param.get('channel')}.nix", "w"
    ) as fp:
        fp.write(
            file_template.replace("${{channel}}", param.get("channel"))
            .replace("${{package}}", param.get("package"))
            .replace("${{bin_name}}", param.get("bin_name"))
        )
    subprocess.run(
        f"docker load < $(nix-build nix-image/{param.get('package')}-{param.get('channel')}.nix)",
        shell=True,
    )

subprocess.run(
    f"grype {image} -o template -t csv.tmpl --file image_data/{image}.csv", shell=True
)

images = ["cgr.dev/chainguard/python:latest", "python:3.9-slim", "python:3.9-alpine"]
for image in images:
    subprocess.run(
        f"grype {image} -o template -t csv.tmpl --file image_data/{image}.csv",
        shell=True,
    )
