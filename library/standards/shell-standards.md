# Shell / Bash Scripting Standards

## Scope: Safe scripting, portability, error handling
**Authority:** Google Shell Style Guide, ShellCheck wiki  
**Tools:** ShellCheck, shfmt, bats (testing)  

## Script Header

```bash
#!/usr/bin/env bash
#
# Description: Brief purpose of this script
# Usage: ./script.sh <arg1> [arg2]
#

set -euo pipefail  # ALWAYS — exit on error, undefined vars, pipe failures
```

## Variable Rules

```bash
# ALWAYS quote variables
echo "$file"             # NOT: echo $file
rm -- "$path"            # -- prevents flag injection

# Use readonly for constants
readonly CONFIG_DIR="/etc/myapp"
readonly LOG_FILE="$CONFIG_DIR/app.log"

# Use local in functions
my_func() {
    local result
    result=$(compute_something)
    echo "$result"
}

# Use ${var} in strings for clarity
echo "Processing ${filename} in ${dir}/"
```

## Safety Patterns

```bash
# Trap for cleanup
cleanup() { rm -f "$tmpfile"; }
trap cleanup EXIT
tmpfile=$(mktemp)

# Check dependencies
command -v jq >/dev/null 2>&1 || { echo "jq required" >&2; exit 1; }

# Validate inputs
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <filename>" >&2
    exit 1
fi
[[ -f "$1" ]] || { echo "File not found: $1" >&2; exit 1; }

# Use [[ ]] not [ ] (bash-specific but safer)
# Use $(cmd) not backticks `cmd`
```

## Anti-Patterns

| Anti-Pattern | Better |
|-------------|--------|
| No `set -euo pipefail` | Always set strict mode |
| Unquoted variables | Always quote: `"$var"` |
| `cd dir; command` | `cd dir && command` or `(cd dir; command)` |
| Parsing `ls` output | Use globs: `for f in *.txt` |
| `cat file \| grep` | `grep pattern file` |
| Backticks `` `cmd` `` | `$(cmd)` (nestable, readable) |
| `eval "$user_input"` | Never eval untrusted input |
