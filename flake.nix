{
  inputs = { nixpkgs.url = "github:nixos/nixpkgs/67f49b2a3854e8b5e3f9df4422225daa0985f451"; };
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
  flake-utils.lib.eachDefaultSystem (system:
  let 
    pkgs = nixpkgs.legacyPackages.${system}; 
    # dir = ''/home/jayghoshter/dev/tools/chromoo/'';

    mach-nix = import (builtins.fetchGit {
      url = "https://github.com/DavHau/mach-nix";
      ref = "refs/tags/3.5.0";
    }) {};

    ## CADET package
    ## Can also be placed in ~/.nixpkgs/config.nix
    cadet = pkgs.stdenv.mkDerivation rec {

      name = "cadet";

      version = "4.3.0";

      src = pkgs.fetchgit {
        url = "https://github.com/modsim/CADET";
        rev = "cbc0beea24fa8a25edcadfffa6cee03484fcd209";
        sha256 = "R6rOaW84qGZDFRT689YZB5XIU9dekvabTB/4O3SGoPU=";
      };

      nativeBuildInputs = with pkgs; [ cmake ];

      buildInputs = with pkgs; [ 
            hdf5
            suitesparse
            mkl
      ];

      cmakeFlags = [
        "-DENABLE_CADET_MEX=OFF" 
        "-DENABLE_TESTS=OFF" 
        "-DBLA_VENDOR=Intel10_64lp"
      ];

    };

    in 
    {

      defaultPackage = pkgs.python3Packages.buildPythonPackage{
        pname = "chromoo";
        version = "0.1";

        src = ./.;

        mnpyreq = mach-nix.mkPython {
          requirements = builtins.readFile ./requirements.txt;
        };

        propagatedBuildInputs = with pkgs; [
          mnpyreq
        ];

        doCheck = false;
      };


      devShell = pkgs.mkShell rec {
            name = "chromoo";

            mnpyreq = mach-nix.mkPython {
              requirements = builtins.readFile ./requirements.txt;
            };

            buildInputs = with pkgs; [
              mnpyreq
              cadet
              git
              which
            ];

            shellHook = ''
              # Tells pip to put packages into $PIP_PREFIX instead of the usual locations.
              # See https://pip.pypa.io/en/stable/user_guide/#environment-variables.
              export PYTHONPATH="$(pwd):$PYTHONPATH"
              export PATH="$(pwd)/bin:$PATH"
              unset SOURCE_DATE_EPOCH
            '';

        };
      });
}
