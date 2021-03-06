{ pkgs ? import <nixpkgs> {},
  # ignore untracked files in local checkout
  src ? if builtins.pathExists ./.git then builtins.fetchGit { url = ./.; } else ./. }:
with pkgs.python3Packages;
let
  python = import ./requirements.nix { inherit pkgs; };
  pypi = python.packages;
  click_git = click.overrideAttrs (attrs: {
    src = builtins.fetchGit { url = https://github.com/pallets/click.git; rev = "f537a208591088499b388b06b2aca4efd5445119"; };
  });
in buildPythonApplication rec {
  name = "temci-${version}";
  version = "local";
  inherit src;
  checkInputs = [ pytest pytestrunner ];
  propagatedBuildInputs = [
    click_git
    pypi.humanfriendly
    fn
    pytimeparse
    pypi.cpuset-py3
    wcwidth
    pypi.rainbow-logging-handler
    tablib unicodecsv
    scipy seaborn
    pyyaml
  ] ++ pkgs.lib.optional pkgs.stdenv.isLinux pkgs.linuxPackages.perf;
  postInstall = ''
    $out/bin/temci setup
  '';
  postPatch = ''
    substituteInPlace temci/run/cpuset.py --replace python3 ${pkgs.python3.withPackages (ps: [ pypi.cpuset-py3 ])}/bin/python3
    substituteInPlace temci/run/run_driver.py \
      --replace /usr/bin/time ${pkgs.time}/bin/time \
      --replace gtime ${pkgs.time}/bin/time
  '';
  preCheck = ''export PATH=$PATH:$out/bin'';
}
