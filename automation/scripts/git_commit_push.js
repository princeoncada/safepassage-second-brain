const { execFileSync } = require('child_process');

function run(command, args, options = {}) {
  return execFileSync(command, args, {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    ...options
  }).trim();
}

function hasChanges() {
  const status = run('git', ['status', '--short']);
  return status.length > 0;
}

function gitCommitPush(message) {
  run('git', ['add', '.']);

  if (!hasChanges()) {
    return {
      committed: false,
      pushed: false,
      reason: 'No changes to commit.'
    };
  }

  const commitMessage = message || process.env.GIT_COMMIT_MESSAGE || 'chore: ingest structured knowledge';
  run('git', ['commit', '-m', commitMessage], { stdio: ['ignore', 'pipe', 'pipe'] });
  run('git', ['push', 'origin', 'master'], { stdio: ['ignore', 'pipe', 'pipe'] });

  return {
    committed: true,
    pushed: true,
    branch: 'master',
    message: commitMessage
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
  let message = process.argv.slice(2).join(' ');

  if (!message && stdin.trim()) {
    try {
      const parsed = JSON.parse(stdin);
      message = parsed.commit_message || '';
    } catch {
      message = stdin.trim();
    }
  }

  const result = gitCommitPush(message);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

if (require.main === module) {
  main().catch((error) => {
    console.error(error.message);
    process.exit(1);
  });
}

module.exports = {
  gitCommitPush
};
