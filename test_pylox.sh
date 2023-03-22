#!/usr/bin/env zsh
DIR="$HOME/src/craftinginterpreters"
TEST="$DIR/tool/bin/test.dart"
LOX="$HOME/src/pylox/pylox"
pushd $DIR
dart $TEST chap11_resolving --interpreter $LOX
popd
