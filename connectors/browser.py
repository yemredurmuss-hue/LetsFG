"""
Shared browser launcher for BoostedTravel connectors.

Provides Chrome discovery, stealth CDP launch (off-screen, no-focus),
and Playwright helpers. All CDP Chrome connectors should use these
instead of rolling their own launch logic.

Environment variables:
    CHROME_PATH         — Override Chrome executable path.
    BOOSTED_BROWSER_VISIBLE — Set to "1" to show browser windows (debugging).
"""

from __future__ import annotations

import asyncio
import logging
import os
import platform
import shutil
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

# ── Chrome discovery ────────────────────────────────────────────────────────────

_WIN_CANDIDATES = [
    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
]

_LINUX_CANDIDATES = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
]

_MAC_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def find_chrome() -> str:
    """Find Chrome executable on the system. Raises RuntimeError if not found."""
    env = os.environ.get("CHROME_PATH", "")
    if env and os.path.isfile(env):
        return env

    system = platform.system()
    if system == "Windows":
        candidates = _WIN_CANDIDATES
    elif system == "Darwin":
        candidates = _MAC_CANDIDATES
    else:
        candidates = _LINUX_CANDIDATES

    # Also try PATH
    which = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
    if which:
        candidates = [which] + candidates

    for c in candidates:
        if c and os.path.isfile(c):
            return c

    raise RuntimeError(
        "Chrome not found. Install Google Chrome or set CHROME_PATH env var."
    )


# ── Stealth window args ────────────────────────────────────────────────────────

def _is_visible() -> bool:
    """Check if browsers should be visible (for debugging)."""
    return os.environ.get("BOOSTED_BROWSER_VISIBLE", "").strip() in ("1", "true", "yes")


def stealth_args() -> list[str]:
    """
    Chrome CLI args that push the window off-screen and minimize it.

    When BOOSTED_BROWSER_VISIBLE=1, returns empty list (normal window).
    """
    if _is_visible():
        return []
    return [
        "--window-position=-2400,-2400",
        "--window-size=800,600",
    ]


def stealth_position_arg() -> list[str]:
    """Off-screen window position only (for connectors that set their own --window-size)."""
    if _is_visible():
        return []
    return ["--window-position=-2400,-2400"]


def stealth_popen_kwargs() -> dict:
    """
    Extra kwargs for subprocess.Popen to suppress the Chrome window on Windows.

    Uses STARTUPINFO with SW_SHOWMINNOACTIVE so the window starts minimized
    without stealing focus. On Linux/Mac, suppresses stdout/stderr.
    """
    kwargs: dict = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }

    if _is_visible():
        return kwargs

    if platform.system() == "Windows":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 7  # SW_SHOWMINNOACTIVE — minimized, no focus steal
        kwargs["startupinfo"] = si
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs


# ── CDP Chrome launch ──────────────────────────────────────────────────────────

async def launch_cdp_chrome(
    port: int,
    user_data_dir: str,
    *,
    extra_args: Optional[list[str]] = None,
    start_url: str = "about:blank",
    startup_wait: float = 2.0,
) -> subprocess.Popen:
    """
    Launch a real Chrome instance for CDP connection.

    The window is pushed off-screen and minimized so it doesn't
    disturb the user. Set BOOSTED_BROWSER_VISIBLE=1 to override.

    Args:
        port: CDP debugging port (e.g. 9460).
        user_data_dir: Path to Chrome user data directory.
        extra_args: Additional Chrome CLI flags.
        start_url: Initial URL to load (default: about:blank).
        startup_wait: Seconds to wait after launch for Chrome to be ready.

    Returns:
        The subprocess.Popen handle.
    """
    chrome = find_chrome()
    os.makedirs(user_data_dir, exist_ok=True)

    args = [
        chrome,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled",
        *stealth_args(),
        *(extra_args or []),
        start_url,
    ]

    proc = subprocess.Popen(args, **stealth_popen_kwargs())
    await asyncio.sleep(startup_wait)
    logger.info("Chrome launched on CDP port %d (pid %d, visible=%s)",
                port, proc.pid, _is_visible())
    return proc


async def connect_cdp(port: int):
    """
    Connect Playwright to an existing Chrome via CDP.

    Returns the Playwright Browser object.
    """
    from playwright.async_api import async_playwright
    pw = await async_playwright().start()
    browser = await pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
    return browser


async def get_or_launch_cdp(
    port: int,
    user_data_dir: str,
    *,
    extra_args: Optional[list[str]] = None,
    start_url: str = "about:blank",
    startup_wait: float = 2.0,
):
    """
    Try connecting to existing Chrome on port, or launch a new one.

    Returns (browser, proc_or_None).
    """
    from playwright.async_api import async_playwright

    # Try connecting to already-running Chrome
    try:
        pw = await async_playwright().start()
        browser = await pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        logger.info("Connected to existing Chrome on port %d", port)
        return browser, None
    except Exception:
        pass

    # Launch new Chrome
    proc = await launch_cdp_chrome(
        port, user_data_dir,
        extra_args=extra_args,
        start_url=start_url,
        startup_wait=startup_wait,
    )
    pw = await async_playwright().start()
    browser = await pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
    return browser, proc


# ── Playwright headed launch ───────────────────────────────────────────────────

async def launch_headed_browser(
    *,
    channel: str = "chrome",
    extra_args: Optional[list[str]] = None,
):
    """
    Launch a headed Playwright browser with stealth window positioning.

    Used by connectors that need Playwright.launch(headless=False) instead of CDP.
    Window is pushed off-screen unless BOOSTED_BROWSER_VISIBLE=1.

    Returns the Playwright Browser object.
    """
    from playwright.async_api import async_playwright

    args = [*stealth_args(), *(extra_args or [])]

    pw = await async_playwright().start()
    try:
        browser = await pw.chromium.launch(
            headless=False,
            channel=channel,
            args=args if args else None,
        )
    except Exception:
        # Fallback: no channel (use bundled Chromium)
        browser = await pw.chromium.launch(
            headless=False,
            args=args if args else None,
        )
    logger.info("Headed browser launched (channel=%s, visible=%s)", channel, _is_visible())
    return browser
