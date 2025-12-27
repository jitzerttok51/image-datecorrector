{
  description = "A Nix-flake-based Zig development environment";

  inputs = {
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0"; # stable Nixpkgs
    pyproject-nix = {
      url = "github:nix-community/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    { self, ... }@inputs:

    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forEachSupportedSystem =
        f:
        inputs.nixpkgs.lib.genAttrs supportedSystems (
          system:
          f rec {
            inherit system;
            pkgs = import inputs.nixpkgs {
              inherit system;
            };
            python = pkgs.python3;
          }
        );
      project = inputs.pyproject-nix.lib.project.loadPyproject {
        projectRoot = ./.;
      };
    in
    {
      packages = forEachSupportedSystem (
        { pkgs, system, python }: let 
          attrs = project.renderers.buildPythonPackage { 
            inherit python;
          };
        in {
          default = pkgs.python3Packages.buildPythonPackage (attrs // { 
            nativeBuildInputs = [ pkgs.python3Packages.pytestCheckHook ];
          });
        }
      ); 

      devShells = forEachSupportedSystem (
        { pkgs, system, python }: let 
          arg = project.renderers.withPackages { inherit python; };
          pythonEnv = python.withPackages arg;
        in {
          default = pkgs.mkShellNoCC {
            packages = [ pythonEnv ];
          };
        }
      );
    };
}
