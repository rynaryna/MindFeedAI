import asyncio
import logging
import subprocess
from exceptions.parser_exceptions import AIClientException

logger = logging.getLogger(__name__)


def _run_claude_process(prompt: str) -> str:
    logger.debug('Invoking Claude CLI (prompt length=%d chars).', len(prompt))
    try:
        result = subprocess.run(
            ['claude', '-p', '-'],
            input=prompt,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise AIClientException('Claude CLI not found. Make sure "claude" is installed and on PATH.')
    except OSError as e:
        raise AIClientException('Failed to start Claude CLI process.') from e

    if result.returncode != 0:
        raise AIClientException(
            f'Claude CLI exited with code {result.returncode}. stderr: {result.stderr.strip()}'
        )

    if not result.stdout.strip():
        raise AIClientException('Claude CLI returned an empty response.')

    return result.stdout


async def invoke_claude_cli(prompt: str) -> str:
    return await asyncio.to_thread(_run_claude_process, prompt=prompt)
