const fs = require('fs');
const path = require('path');
const { sanitizeFilename } = require('./sanitize_filename');
const { validateMetadata } = require('./validate_metadata');

function resolveVaultPath(vaultRoot, targetFolder, filename) {
  const root = path.resolve(vaultRoot || process.env.VAULT_PATH || 'vault');
  const folder = String(targetFolder || 'vault/00_Inbox').replace(/\\/g, '/');
  const relativeFolder = folder.replace(/^\.?\/*vault\/*/, '') || '00_Inbox';
  const safeFilename = sanitizeFilename(filename);
  const destination = path.resolve(root, relativeFolder, safeFilename);

  if (destination !== root && !destination.startsWith(`${root}${path.sep}`)) {
    throw new Error('Refusing to write outside the vault path.');
  }

  return {
    root,
    destination,
    safeFilename
  };
}

function writeMarkdown(payload, options = {}) {
  const markdown = String(payload.normalized_markdown || '');
  if (!markdown.trim()) {
    throw new Error('normalized_markdown is required.');
  }

  const metadata = validateMetadata(markdown);
  if (!metadata.valid) {
    throw new Error(`Metadata validation failed: ${metadata.errors.join('; ')}`);
  }

  const { root, destination, safeFilename } = resolveVaultPath(
    options.vaultRoot,
    payload.target_folder,
    payload.suggested_filename
  );

  const allowOverwrite = options.allowOverwrite === true || payload.allow_overwrite === true || process.env.ALLOW_OVERWRITE === 'true';
  if (fs.existsSync(destination) && !allowOverwrite) {
    throw new Error(`Refusing to overwrite existing file: ${destination}`);
  }

  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, markdown, 'utf8');

  return {
    written: true,
    vault_root: root,
    path: destination,
    filename: safeFilename
  };
}

function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => {
      data += chunk;
    });
    process.stdin.on('end', () => {
      resolve(data);
    });
  });
}

async function main() {
  const stdin = await readStdin();
  const payload = JSON.parse(stdin);
  const result = writeMarkdown(payload);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error.message);
    process.exit(1);
  });
}

module.exports = {
  resolveVaultPath,
  writeMarkdown
};
