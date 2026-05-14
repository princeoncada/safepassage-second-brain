const ALLOWED_CLASSIFICATIONS = new Set([
  '',
  'post_order',
  'sop',
  'incident',
  'qa_rule',
  'script',
  'workflow',
  'briefing',
  'visitor_log',
  'code_snippet',
  'automation',
  'training',
  'community_profile',
  'unknown'
]);

const ALLOWED_PRIORITIES = new Set(['', 'low', 'medium', 'high', 'critical']);

function validatePayload(payload) {
  const errors = [];

  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return {
      valid: false,
      errors: ['Payload must be a JSON object.']
    };
  }

  if (!payload.input_text || typeof payload.input_text !== 'string') {
    errors.push('input_text is required and must be a non-empty string.');
  }

  if (!payload.source || typeof payload.source !== 'string') {
    errors.push('source is required and must be a non-empty string.');
  }

  if (!payload.received_at || typeof payload.received_at !== 'string') {
    errors.push('received_at is required and must be an ISO-8601 string.');
  } else if (Number.isNaN(Date.parse(payload.received_at))) {
    errors.push('received_at must parse as a valid date.');
  }

  if (payload.classification && !ALLOWED_CLASSIFICATIONS.has(payload.classification)) {
    errors.push(`classification is not supported: ${payload.classification}`);
  }

  if (payload.priority && !ALLOWED_PRIORITIES.has(payload.priority)) {
    errors.push(`priority is not supported: ${payload.priority}`);
  }

  for (const field of ['community', 'target_folder', 'suggested_filename', 'normalized_markdown']) {
    if (payload[field] !== undefined && payload[field] !== null && typeof payload[field] !== 'string') {
      errors.push(`${field} must be a string when provided.`);
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
  const payload = JSON.parse(stdin);
  const result = validatePayload(payload);
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
  ALLOWED_CLASSIFICATIONS,
  ALLOWED_PRIORITIES,
  validatePayload
};
