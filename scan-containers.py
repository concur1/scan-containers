import subprocess

# Create and scan nix containers
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
        "package": "python312",
        "bin_name": "python",
        "channel": "stable",
    },
    {
        "package": "python312",
        "bin_name": "python",
        "channel": "unstable",
    },
]

from pathlib import Path

Path("image_data").mkdir(parents=True, exist_ok=True)
Path("nix-image").mkdir(parents=True, exist_ok=True)

images = []
for param in params:
    image = f"{param.get('package')}:nix-{param.get('channel')}-latest"
    images.append(image)
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

## Scan other containers
images = images + [
    "cgr.dev/chainguard/python:latest",
    "python:3.12-slim",
    "python:3.12-alpine",
]
for image in images:
   subprocess.run(
       f"grype {image} -o template -t csv.tmpl --file image_data/{image}.csv",
       shell=True,
   )


# Summarise data
import polars as pl


def sev_count(df, sev):
    return df.filter((pl.col("Severity") == sev) & (pl.col("Vuln Fix State")!="fixed")).select(pl.count()).item()


def get_data_as_df(image_name):
    df = pl.read_csv(f"image_data/{image_name}.csv", infer_schema_length=0)
    return {
        "Image": image_name,
        "Unknown": sev_count(df, "Unknown"),
        "Negligible": sev_count(df, "Negligible"),
        "Low": sev_count(df, "Low"),
        "Medium": sev_count(df, "Medium"),
        "High": sev_count(df, "High"),
        "Critical": sev_count(df, "Critical"),
    }


from pprint import pprint

print(pl.DataFrame(list(map(get_data_as_df, images))))
