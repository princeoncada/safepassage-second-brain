const REQUIRED_FIELDS = [
  'title',
  'type',
  'community',
  'priority',
  'effective_date',
  'source',
  'status',
  'tags',
  'last_updated',
  'version'
];

function extractFrontmatter(markdown) {
  const text = String(markdown || '');
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  return match ? match[1] : null;
}

function parseFrontmatterKeys(frontmatter) {
  const keys = new Set();
  for (const line of String(frontmatter || '').split(/\r?\n/)) {
    const match = line.match(/^([A-Za-z0-9_-]+):/);
    if (match) {
      keys.add(match[1]);
    }
  }
  return keys;
}

function validateMetadata(markdown) {
  const errors = [];
  const frontmatter = extractFrontmatter(markdown);

  if (!frontmatter) {
    return {
      valid: false,
      errors: ['Missing YAML frontmatter block.']
    };
  }

  const keys = parseFrontmatterKeys(frontmatter);
  for (const field of REQUIRED_FIELDS) {
    if (!keys.has(field)) {
      errors.push(`Missing required frontmatter field: ${field}`);
    }
  }

  return {
    valid: errors.length === 0,
    errors
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
  let markdown = stdin;

  try {
    const parsed = JSON.parse(stdin);
    markdown = parsed.normalized_markdown || parsed.markdown || '';
  } catch {
    markdown = stdin;
  }

  const result = validateMetadata(markdown);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  if (!result.valid) {
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error.message);
    process.exit(1);
  });
}

module.exports = {
  REQUIRED_FIELDS,
  validateMetadata
};
