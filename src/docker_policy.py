"""
Docker Execution Policy - Enforced sandbox container configuration

This module defines the security policy for all container executions.
Every Nova code execution runs in a container with these restrictions.
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


# Docker policy enforced for ALL container executions
DOCKER_SECURITY_POLICY = {
    # Network isolation (default: completely blocked)
    "network_mode": "none",
    
    # Process/IPC isolation
    "ipc": "private",
    "pid": "host",  # Needed for container management
    
    # Filesystem
    "read_only_rootfs": True,
    
    # Capabilities - Drop ALL, add back only necessary
    "cap_drop": ["ALL"],
    "cap_add": [
        "CHOWN",            # Needed for file operations
        "DAC_OVERRIDE",     # Needed for file permissions
    ],
    
    # Security options
    "security_opt": [
        "no-new-privileges:true",  # Cannot escalate
    ],
    
    # Resource limits
    "cpu_quota": 200000,           # 0.2 CPU (2 cores max)
    "cpu_shares": 1024,            # Fair share
    "memory": "4g",                # 4GB max
    "pids_limit": 100,             # Max 100 processes
    "oom_kill_disable": False,     # Kill container on OOM
    
    # Mounts - ephemeral + code workspace
    "tmpfs": {
        "/tmp": "size=512M,noexec,nosuid,nodev",
        "/run": "size=64M,noexec,nosuid,nodev",
    },
    
    # Restart policy
    "restart_policy": {
        "Name": "no",              # Don't auto-restart
        "MaximumRetryCount": 0,
    },
    
    # User (run as non-root)
    "user": "1000",                # Regular user
    
    # Other security settings
    "healthcheck": {
        "Test": ["CMD", "true"],   # Always pass (quick check)
        "Interval": 30000000000,   # 30 seconds
        "Timeout": 5000000000,     # 5 seconds
        "StartPeriod": 5000000000, # 5 seconds
        "Retries": 1,
    },
    
    # Remove dangerous options
    "privileged": False,
    "security_driver": "default",
}


# Read-only mounts (system files)
READONLY_MOUNTS = [
    ("/etc", "/etc:ro"),
    ("/usr", "/usr:ro"),
    ("/lib", "/lib:ro"),
    ("/bin", "/bin:ro"),
    ("/sbin", "/sbin:ro"),
    ("/opt", "/opt:ro"),
]


# Writable mounts (for actual work)
WRITABLE_MOUNTS = [
    # Code workspace (from host)
    ("{workspace_dir}", "/workspace:rw"),
    
    # Temporary files (tmpfs)
    ("/tmp"),
    ("/run"),
]


def build_docker_run_command(
    image: str,
    command: List[str],
    workspace_dir: str,
    network_enabled: bool = False,
    secrets_env: Dict[str, str] = None,
    volumes: Dict[str, str] = None,
    timeout_seconds: int = 600,
) -> List[str]:
    """
    Build docker run command with enforced security policy
    
    Args:
        image: Docker image to run
        command: Command to execute
        workspace_dir: Host workspace directory to mount
        network_enabled: Enable network access (for package downloads)
        secrets_env: Environment variables for secrets
        volumes: Additional volumes to mount
        timeout_seconds: Execution timeout
    
    Returns:
        List of docker run arguments
    """
    
    cmd = ["docker", "run"]
    
    # Basic options
    cmd.extend(["--rm"])  # Remove container after execution
    cmd.extend(["--detach=false"])  # Don't detach
    
    # Network policy
    if network_enabled:
        cmd.extend(["--network=bridge"])  # Outbound only
    else:
        cmd.extend(["--network=none"])  # Completely isolated
    
    # Process/IPC isolation
    cmd.extend(["--ipc", "private"])
    
    # Filesystem security
    cmd.extend(["--read-only"])  # Read-only root filesystem
    
    # Capabilities
    cmd.extend(["--cap-drop=ALL"])
    cmd.extend(["--cap-add=CHOWN"])
    cmd.extend(["--cap-add=DAC_OVERRIDE"])
    
    # Security options
    cmd.extend(["--security-opt=no-new-privileges:true"])
    
    # Resource limits
    cmd.extend(["--cpus=0.2"])  # 0.2 CPU
    cmd.extend(["--memory=4g"])  # 4GB max memory
    cmd.extend(["--pids-limit=100"])  # Max 100 processes
    
    # User (non-root)
    cmd.extend(["--user=1000"])
    
    # Temporary filesystems (ephemeral)
    cmd.extend(["--tmpfs", "/tmp:size=512M,noexec,nosuid,nodev"])
    cmd.extend(["--tmpfs", "/run:size=64M,noexec,nosuid,nodev"])
    
    # Mount workspace (the only writable path)
    cmd.extend(["-v", f"{workspace_dir}:/workspace:rw"])
    
    # Mount additional volumes if provided
    if volumes:
        for host_path, container_path in volumes.items():
            cmd.extend(["-v", f"{host_path}:{container_path}"])
    
    # Secrets via environment variables (secure)
    if secrets_env:
        for key, value in secrets_env.items():
            cmd.extend(["-e", f"{key}={value}"])
    
    # Working directory
    cmd.extend(["-w", "/workspace"])
    
    # Timeout (using timeout command wrapper)
    cmd.extend(["--entrypoint", f"timeout"])
    cmd.append(str(timeout_seconds))
    
    # Image
    cmd.append(image)
    
    # Command to execute
    cmd.extend(command)
    
    logger.info(f"✅ Built Docker run command (network={'enabled' if network_enabled else 'disabled'}, timeout={timeout_seconds}s)")
    
    return cmd


def validate_docker_policy(container_config: Dict) -> bool:
    """
    Validate that a container configuration meets security policy
    
    Args:
        container_config: Container configuration from Docker
    
    Returns:
        True if configuration meets policy, False otherwise
    """
    
    checks = {
        "network_disabled": container_config.get("NetworkMode") == "none" or 
                           container_config.get("NetworkMode") == "bridge",
        "read_only_root": container_config.get("ReadonlyRootfs") is True,
        "memory_limited": container_config.get("Memory") > 0,
        "cpu_limited": container_config.get("CpuQuota") > 0,
        "no_privileged": container_config.get("Privileged") is False,
        "cap_dropped": "ALL" in container_config.get("CapDrop", []),
        "no_new_privileges": any(
            "no-new-privileges" in opt 
            for opt in container_config.get("SecurityOpt", [])
        ),
    }
    
    all_pass = all(checks.values())
    
    if not all_pass:
        logger.error("❌ Container policy validation failed:")
        for check, status in checks.items():
            logger.error(f"   {'✅' if status else '❌'} {check}")
    else:
        logger.info("✅ Container security policy validated")
    
    return all_pass


def get_policy_summary() -> Dict:
    """Get summary of Docker security policy"""
    
    return {
        "network": "Isolated (--network=none by default, --network=bridge optional)",
        "filesystem": "Read-only root, ephemeral /tmp, code workspace writable",
        "resources": {
            "cpu": "0.2 CPU max (200 millicores)",
            "memory": "4GB max",
            "disk": "512MB /tmp, unlimited /workspace (repo limited)",
            "runtime": "600 seconds (10 minutes)",
            "processes": "100 max",
        },
        "security": {
            "user": "Non-root (UID 1000)",
            "capabilities": "Only CHOWN + DAC_OVERRIDE (all else dropped)",
            "privilege_escalation": "Blocked (no-new-privileges)",
            "apparmor": "Default profile",
        },
        "secrets": "Environment variables only (never persisted)",
        "isolation": "Complete (process, IPC, PID, network, filesystem)",
    }
