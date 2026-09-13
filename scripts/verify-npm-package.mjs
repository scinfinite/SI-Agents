#!/usr/bin/env node

import { readFileSync, existsSync, mkdtempSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const pyproject = readFileSync(join(root, 'pyproject.toml'), 'utf8');
const versionMatch = pyproject.match(/^version\s*=\s*"([^"]+)"/m);
if (!versionMatch) throw new Error('Could not read Python package version from pyproject.toml');
if (pkg.version !== versionMatch[1]) throw new Error(`Version mismatch: npm ${pkg.version} != Python ${versionMatch[1]}`);
if (pkg.license !== 'Apache-2.0') throw new Error(`Unexpected npm license: ${pkg.license}`);
if (!pkg.bin?.['si-agents']) throw new Error('si-agents executable is not declared');

const launcher = join(root, pkg.bin['si-agents']);
for (const required of [launcher, join(root, 'LICENSE'), join(root, 'NOTICE'), join(root, 'README.npm.md')]) {
  if (!existsSync(required)) throw new Error(`Missing npm distribution file: ${required}`);
}

const temp = mkdtempSync(join(tmpdir(), 'si-agents-npm-'));
try {
  const packed = execFileSync(
    'npm',
    ['pack', '--ignore-scripts', '--json', '--pack-destination', temp],
    { cwd: root, encoding: 'utf8' },
  );
  const metadata = JSON.parse(packed);
  const tarball = join(temp, `${pkg.name}-${pkg.version}.tgz`);
  if (!existsSync(tarball)) throw new Error(`npm pack did not create ${tarball}`);
  const files = metadata[0]?.files?.map((entry) => entry.path).sort() ?? [];
  const expected = [
    'LICENSE',
    'NOTICE',
    'README.md',
    'README.npm.md',
    'bin/si-agents.js',
    'package.json',
  ];
  if (JSON.stringify(files) !== JSON.stringify(expected)) {
    throw new Error(`Unexpected npm tarball contents:\n${files.join('\n')}`);
  }

  const version = execFileSync('node', [launcher, '--version'], { encoding: 'utf8' }).trim();
  if (version !== pkg.version) throw new Error(`Launcher version mismatch: ${version} != ${pkg.version}`);
  execFileSync('node', [launcher, 'help'], { stdio: 'inherit' });
} finally {
  rmSync(temp, { recursive: true, force: true });
}

console.log('npm distribution verification passed');
