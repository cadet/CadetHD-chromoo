{
  pkgs ? import (builtins.fetchTarball {
    name = "nixpkgs-unstable-2022-08-01";
    url = "https://github.com/nixos/nixpkgs/archive/67f49b2a3854e8b5e3f9df4422225daa0985f451.tar.gz";
    sha256 = "11ra1nqdxq723ggk0yc6vy58kcxn795kjw4qqwfpjrynqbj5dvkr";
  }) {}

}:
let
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

in pkgs.mkShell rec {
  name = "chromoo";

  mnpyreq = mach-nix.mkPython {
    requirements = builtins.readFile ./requirements.txt;
  };

  buildInputs = with pkgs; [
    mnpyreq
    cadet
  ];

  shellHook = ''
    # Tells pip to put packages into $PIP_PREFIX instead of the usual locations.
    # See https://pip.pypa.io/en/stable/user_guide/#environment-variables.
    # export PYTHONPATH="$(pwd):$PYTHONPATH"
    # export PATH="$(pwd)/bin:$PATH"
    export PYTHONPATH="/home/jayghoshter/dev/tools/chromoo:$PYTHONPATH"
    export PATH="/home/jayghoshter/dev/tools/chromoo/bin:$PATH"
    unset SOURCE_DATE_EPOCH
  '';

}
