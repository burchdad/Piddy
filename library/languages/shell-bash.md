# Shell / Bash Quick Reference

## Language: Bash 5.x / POSIX sh
**Paradigm:** Command-line scripting  
**Typing:** Untyped (everything is a string)  
**Platforms:** Linux, macOS, WSL, Git Bash  

## Script Setup

```bash
#!/usr/bin/env bash
set -euo pipefail    # exit on error, undefined vars, pipe failures

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <filename>" >&2
    exit 1
fi
```

## Variables & Strings

```bash
name="Piddy"
echo "Hello $name"
echo "${#name}"               # length: 5
echo "${name,,}"              # lowercase
echo "${filename%.txt}"       # remove suffix
echo "${path##*/}"            # basename

# Default values
value="${VAR:-default}"       # use default if unset
value="${VAR:?'required'}"    # error if unset

# Arrays
arr=(one two three)
arr+=(four)
echo "${arr[@]}"              # all elements
echo "${#arr[@]}"             # length
```

## Control Flow

```bash
if [[ -f "$file" ]]; then echo "exists"; fi

# Test operators
[[ -f file ]]       # file exists
[[ -d dir ]]        # directory exists
[[ -z "$var" ]]     # empty string
[[ "$a" == "$b" ]]  # string equal
[[ $n -gt 10 ]]     # numeric greater

for file in *.txt; do echo "$file"; done
for i in {1..10}; do echo "$i"; done

case "$action" in
    start)  start_service ;;
    stop)   stop_service ;;
    *)      echo "Unknown" >&2; exit 1 ;;
esac
```

## Functions & Patterns

```bash
log() {
    local level="$1" message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >&2
}

# Cleanup trap
cleanup() { rm -f "$tmpfile"; }
trap cleanup EXIT
tmpfile=$(mktemp)
```

## Essential Commands

| Command | Purpose |
|---------|---------|
| `grep -rn pattern dir/` | Search text recursively |
| `find . -name "*.ext"` | Find files by pattern |
| `sed 's/old/new/g' file` | Stream editing |
| `awk '{print $1, $3}'` | Column processing |
| `xargs` | Build command from stdin |
| `jq '.key'` | JSON processing |
| `curl -sL url` | HTTP requests |
