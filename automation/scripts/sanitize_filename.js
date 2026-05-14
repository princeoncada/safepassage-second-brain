const path = require('path');

function sanitizeFilename(input) {
  const fallback = 'untitled-ingestion.md';
  const raw = String(input || '').trim();
  const withoutExtension = raw.replace(/\.md$/i, '') || fallback.replace(/\.md$/i, '');

  const cleaned = withoutExtension
    .toLowerCase()
    .replace(/[\\/:*?"<>|]/g, ' ')
    .replace(/[^a-z0-9\s._-]/g, ' ')
    .replace(/[\s._-]+/g, '-')
    .replace(/^-+|-+$/g, '');

  const basename = cleaned || fallback.replace(/\.md$/i, '');
  return `${basename}.md`;
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
  let value = process.argv.slice(2).join(' ');

  if (!value && stdin.trim()) {
    try {
      const parsed = JSON.parse(stdin);
      value = parsed.suggested_filename || parsed.filename || parsed.title || '';
    } catch {
      value = stdin;
    }
  }

  const sanitized = sanitizeFilename(value);
  const safeBasename = path.basename(sanitized);
  process.stdout.write(`${safeBasename}\n`);
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error.message);
    process.exit(1);
  });
}

module.exports = {
  sanitizeFilename
};
