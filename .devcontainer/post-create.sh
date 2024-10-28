#!/usr/bin/env bash

mkdir -p /workspaces/sessionsvc/.vscode
cp /workspaces/sessionsvc/.devcontainer/vscode/* /workspaces/sessionsvc/.vscode

make bootstrap
