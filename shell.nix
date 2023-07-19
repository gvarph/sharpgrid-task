{ pkgs ? import <nixpkgs> { } }:


pkgs.mkShell {
  buildInputs = [
    pkgs.python311
    pkgs.poetry
  ];
  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
}
