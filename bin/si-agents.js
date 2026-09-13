#!/usr/bin/env node

'use strict';

const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const VERSION = '0.1.0';
const PYTHON_PACKAGE = 'si-agents';

function commandExists(command) {
  const result = spawnSync(command, ['--version'], { stdio: 'ignore', shell: false });
  return result.status === 0;
}

function pythonCandidates() {
  if (process.env.SI_AGENTS_PYTHON) return [process.env.SI_AGENTS_PYTHON];
  return process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python'];
}

function findPython() {
  return pythonCandidates().find(commandExists) || null;
}

function canImport(python) {
  const result = spawnSync(python, ['-c', 'import core.cli.dispatch'], {
    stdio: 'ignore',
    shell: false,
  });
  return result.status === 0;
}

function execPython(python, args) {
  const result = spawnSync(python, ['-m', 'core.cli.dispatch', ...args], {
    stdio: 'inherit',
    shell: false,
  });
  if (result.error) {
    console.error(`si-agents: failed to start Python runtime: ${result.error.message}`);
    process.exit(1);
  }
  process.exit(result.status === null ? 1 : result.status);
}

function pipInstall(python) {
  console.log(`si-agents: installing Python package ${PYTHON_PACKAGE}==${VERSION}...`);
  const result = spawnSync(python, ['-m', 'pip', 'install', `${PYTHON_PACKAGE}==${VERSION}`], {
    stdio: 'inherit',
    shell: false,
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}

function localSourceRoot() {
  const candidate = path.resolve(__dirname, '..');
  return fs.existsSync(path.join(candidate, 'pyproject.toml')) ? candidate : null;
}

function printSetupHelp(python) {
  console.error('si-agents: the SI-Agents Python runtime is not installed or is not importable.');
  if (python) {
    console.error('  Run: npx si-agents setup');
    console.error(`  Or:  ${python} -m pip install ${PYTHON_PACKAGE}==${VERSION}`);
  } else {
    console.error('  Install Python 3.11+ and ensure it is available on PATH.');
  }
  console.error('  For a source checkout, run the Python package from the repository environment.');
}

function main() {
  const args = process.argv.slice(2);
  if (args[0] === '--version' || args[0] === '-V') {
    console.log(VERSION);
    return;
  }
  if (args[0] === 'help' && args.length === 1) {
    console.log(`SI-Agents ${VERSION}\n\nUsage:\n  si-agents [command] [options]\n  si-agents setup\n\nThe npm package is a launcher/bootstrapper; the Python SI runtime remains authoritative.`);
    return;
  }

  const python = findPython();
  if (!python) {
    printSetupHelp(null);
    process.exit(1);
  }

  if (args[0] === 'setup') {
    if (canImport(python)) {
      console.log('si-agents: Python runtime is already available.');
      return;
    }
    pipInstall(python);
    if (!canImport(python)) {
      console.error('si-agents: Python package installation completed but the runtime is still not importable.');
      process.exit(1);
    }
    console.log('si-agents: Python runtime is ready.');
    return;
  }

  if (canImport(python)) {
    execPython(python, args);
  }

  const sourceRoot = localSourceRoot();
  if (sourceRoot) {
    console.error(`si-agents: Python is available but the source runtime is not importable from ${sourceRoot}.`);
    console.error('  Activate/install the repository Python environment, then retry.');
    process.exit(1);
  }

  printSetupHelp(python);
  process.exit(1);
}

main();
