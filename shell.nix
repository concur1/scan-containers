let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
(pkgs.python312.withPackages (python-pkgs: [
      python-pkgs.black
      python-pkgs.polars
    ]))
    pkgs.grype
    pkgs.docker
    pkgs.ruff-lsp
    pkgs.ruff
    ];
}
