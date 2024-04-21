let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
(pkgs.python312.withPackages (python-pkgs: [
      python-pkgs.black
    ]))
    pkgs.grype
    pkgs.docker
    pkgs.ruff-lsp
    pkgs.ruff
    ];
}
