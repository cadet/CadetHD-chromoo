{
  inputs = { nixpkgs.url = "github:nixos/nixpkgs/67f49b2a3854e8b5e3f9df4422225daa0985f451"; };
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
  flake-utils.lib.eachDefaultSystem (system:
  let 
    pkgs = nixpkgs.legacyPackages.${system}; 

    # builtins.toString still makes a nix store path for purity
    PROJECT_ROOT = builtins.toString ./.;

    mach-nix = import (builtins.fetchGit {
      url = "https://github.com/DavHau/mach-nix";
      ref = "refs/tags/3.5.0";
    }) {};

    ## CADET package
    ## Can also be placed in ~/.nixpkgs/config.nix
    cadet = pkgs.stdenv.mkDerivation rec {

      name = "cadet";

      version = "4.4.0";

      src = pkgs.fetchgit {
        url = "https://github.com/modsim/CADET";
        rev = "6dfe1f04231aa62874ac4ab3ca4cdbf295708cf0";
        sha256 = "KCpwcNq2byqL9zEuWAz9w5KDFKEiPUofwEs9slrtWeQ=";
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

            # Setting and using PROJECT_ROOT like this allows us to 
            # run `nix develop <thisflakedir> --impure --command zsh`
            # from any directory and get the develop shell.
            # This comes at the expense of copying the source into the 
            # nix store on each invocation, and requiring reloads of 
            # the shell on changes to the source code.
            shellHook = ''
              export PYTHONPATH="'' + PROJECT_ROOT + '':$PYTHONPATH"
              export PATH="'' + PROJECT_ROOT + ''/bin:$PATH"
              unset SOURCE_DATE_EPOCH
            '';

        };
      });
}
