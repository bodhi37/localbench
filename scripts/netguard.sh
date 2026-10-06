#!/bin/bash
# localbench netguard — the entire privileged surface of the egress guard.
#
#   install  <owner> <ports> <targets>
#                              (re)build the guard cgroup + nftables rules,
#                              install the attach helper + sudoers entry,
#                              then prove they enforce what they claim
#                              ports   = comma-separated loopback ports
#                              targets = comma-separated host:port allowlist
#                                        (literal IPv4; loopback entries are
#                                        already covered by the ports set)
#   uninstall                  remove rules, helper, sudoers, stamp, cgroup
#   status                     report; exit 0 only when fully installed
#   verify   <ports>           behavioural self-test of the installed guard
#   exec-as  <cmd> [args...]   attach helper (run *through sudo*): enter the
#                              guard cgroup as root, drop to SUDO_UID, exec
#
# Everything else in localbench runs unprivileged; this file is idempotent and
# touches nothing but:
#   /sys/fs/cgroup/localbench-sandbox      guard cgroup for the sandbox
#   nftables table inet localbench_guard   two hook chains (our own table name,
#                                          so ufw/iptables-nft stay untouched)
#   /usr/local/libexec/localbench-netguard root-owned copy of this file (the
#                                          helper sudo runs; user-editable code
#                                          never runs as root)
#   /etc/sudoers.d/localbench-netguard     NOPASSWD scope: exactly that helper
#   /run/localbench-netguard.stamp         what + when, readable without root
#
# Why a helper: this machine mounts cgroup2 with `nsdelegate`, so an
# unprivileged process can only migrate itself into *descendants* of its own
# cgroup — a root-level guard cgroup is unreachable from uid 1000. The helper
# runs as root for exactly long enough to enter the cgroup, then drops to
# SUDO_UID before exec'ing, so it never grants anything the caller lacks.
#
# Policy (every rule proven by behaviour tests, see `netguard.sh verify`):
#
#   output hook
#     1. loopback packets *sent by the guard cgroup* get mark 0x0b000000
#     2. loopback is passed through (tasks and the endpoint live there)
#     2b. configured non-loopback endpoint targets (a Tailscale/LAN server)
#         get one explicit accept each: that IPv4 host, that TCP port
#     3. every other packet from the guard cgroup is dropped
#        -> the internet, other hosts, other interfaces, raw sockets, UDP, ...
#   input hook — only marked packets are ever considered, i.e. only packets
#   the sandbox itself emitted in rule 1; the host never matches:
#     4. destined to an endpoint port              -> accept
#     5. arriving at a listener inside the cgroup  -> accept (task services)
#     6. part of an established/related flow       -> accept (replies)
#     7. anything else on loopback                 -> drop
#        -> foreign local services, DNS, agent APIs, a second LLM, ...
#
# A flow can only *become* established through rule 4 or 5 (its SYN has to be
# allowed first), so rule 6 cannot be used to sneak past them. Rule 5 matches
# the destination listener via `socket cgroupv2`; rule 1 matches the sending
# socket — the two hooks together give sender *and* receiver identity.
set -u
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export PATH

CGROUP=/sys/fs/cgroup/localbench-sandbox
CGROUP_NAME=localbench-sandbox          # must equal CGROUP's basename: rule key
TABLE=localbench_guard
MARK=0x0b000000                         # bits 24-31: no host subsystem uses them
STAMP=/run/localbench-netguard.stamp
VERSION=3
HELPER=/usr/local/libexec/localbench-netguard
SUDOERS=/etc/sudoers.d/localbench-netguard
SELF=$(readlink -f "$0" 2>/dev/null || printf '%s' "$0")

die() { echo "netguard: $*" >&2; exit 1; }
need_root() { [ "$(id -u)" = 0 ] || die "must run as root (sudo $0 ...)"; }

valid_owner() { case "${1:-}" in ""|*[!A-Za-z0-9_.-]*) return 1;; *) return 0;; esac; }
valid_ports() { case "${1:-}" in *[!0-9,]*) return 1;; *) return 0;; esac; }
valid_targets() {
  # comma-separated host:port, literal IPv4 hosts only: DNS is blocked inside
  # the sandbox by design, so a hostname could never resolve there anyway
  local t h p rest=${1:-}
  [ -z "$rest" ] && return 0
  case "$rest" in *[!0-9A-Za-z.,:_-]*) return 1;; esac
  while [ -n "$rest" ]; do
    t=${rest%%,*}; rest=${rest#"$t"}; rest=${rest#,}
    h=${t%:*}; p=${t##*:}
    [ -n "$h" ] && [ -n "$p" ] && [ "$h" != "$t" ] || return 1
    case "$h" in 127.0.0.1|"::1"|localhost) ;;
      *.*.*.*) case "$h" in *[!0-9.]*) return 1;; esac;;
      *) return 1;;
    esac
    case "$p" in *[!0-9]*|"") return 1;; esac
    [ "$p" -ge 1 ] 2>/dev/null && [ "$p" -le 65535 ] 2>/dev/null || return 1
  done
  return 0
}

stamp_version_ok() { [ -f "$STAMP" ] && grep -qx "version=$VERSION" "$STAMP"; }

# --------------------------------------------------------------------------- #
# rules
# --------------------------------------------------------------------------- #

write_rules() {
  # ports arrive as a comma-separated list: nft set literals need commas
  # between elements (a single element is fine either way)
  local ports="$1" targets="${2:-}"
  [ -n "$ports" ] || ports=0
  # Non-loopback targets get one explicit accept each (that host, that TCP
  # port). Loopback is already covered by the oifname rules; anything not
  # listed still falls through to the cgroup drop. Replies need no rule:
  # unmarked non-loopback input is accepted by chain policy, and a flow can
  # only exist if its SYN passed one of these accepts.
  local extras="" t h p
  for t in ${targets//,/ }; do
    [ -n "$t" ] || continue
    h=${t%:*}; p=${t##*:}
    case "$h" in 127.0.0.1|"::1"|localhost|"") continue;; esac
    extras="${extras}		socket cgroupv2 level 1 \"$CGROUP_NAME\" ip daddr $h tcp dport $p accept
"
  done
  cat <<EOF
table inet $TABLE {
	chain out {
		type filter hook output priority filter; policy accept;
		oifname "lo" socket cgroupv2 level 1 "$CGROUP_NAME" meta mark set $MARK
		oifname "lo" accept
${extras}		socket cgroupv2 level 1 "$CGROUP_NAME" counter drop
	}
	chain in {
		type filter hook input priority filter; policy accept;
		iif "lo" meta mark $MARK tcp dport { $ports } accept
		iif "lo" meta mark $MARK socket cgroupv2 level 1 "$CGROUP_NAME" counter accept
		iif "lo" meta mark $MARK ct state established,related accept
		iif "lo" meta mark $MARK counter drop
	}
}
EOF
}

# --------------------------------------------------------------------------- #
# helpers for verify
# --------------------------------------------------------------------------- #

tcp_open() { timeout 1 bash -c "exec 3<>/dev/tcp/$1/$2" 2>/dev/null; }

free_port() {
  free_port_on 127.0.0.1
}

free_port_on() { # $1=ip -> a free TCP port on that address
  python3 - "$1" <<'EOF'
import socket, sys
s = socket.socket()
s.bind((sys.argv[1], 0))
print(s.getsockname()[1])
s.close()
EOF
}

pick_port() { # a free port that is not one of the guarded endpoint ports
  pick_port_on 127.0.0.1 "$1"
}

pick_port_on() { # $1=ip $2=csv-ports-to-avoid
  local ip=$1 avoid=$2 p i=0
  while [ "$i" -lt 20 ]; do
    p=$(free_port_on "$ip") || return 1
    case ",$avoid," in *",$p,"*) i=$((i + 1)); continue;; esac
    printf '%s\n' "$p"
    return 0
  done
  return 1
}

start_listener() { # $1=port [$2=bind-ip] -> prints pid; fails unless listening
  start_listener_on "${2:-127.0.0.1}" "$1"
}

# NOTE: not `python3 -m http.server`: http.server calls getfqdn() on the bind
# address before listening, and reverse-DNS for a Tailscale IP stalls here —
# the listener would never come up. A raw socket has no such lookup.
start_listener_on() { # $1=ip $2=port -> prints pid
  local ip=$1 port=$2 pid i
  python3 - "$ip" "$port" >/dev/null 2>&1 <<'EOF' &
import socket, sys
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((sys.argv[1], int(sys.argv[2])))
s.listen(5)
while True:
    c, _ = s.accept()
    try:
        c.recv(4096)
    except OSError:
        pass
    try:
        c.sendall(b"HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nok")
    except OSError:
        pass
    c.close()
EOF
  pid=$!
  for i in $(seq 1 15); do
    if timeout 1 bash -c "exec 3<>/dev/tcp/$ip/$port" 2>/dev/null; then
      printf '%s\n' "$pid"; return 0
    fi
    kill -0 "$pid" 2>/dev/null || return 1
    sleep 0.2
  done
  kill "$pid" 2>/dev/null
  return 1
}

# --------------------------------------------------------------------------- #
# install / uninstall / status
# --------------------------------------------------------------------------- #

cmd_install() {
  need_root
  local owner="${1:-}" ports="${2:-}" targets="${3:-}"
  valid_owner "$owner" || die "bad owner '${owner}' (letters, digits, _ . - only)"
  valid_ports "$ports" || die "bad ports '${ports}' (comma separated integers only)"
  valid_targets "$targets" || die "bad targets '${targets}' (comma separated host:port, literal IPv4 only)"
  # canonical form: sorted, unique — the stamp must not depend on caller order
  ports=$(printf '%s' "$ports" | tr ',' '\n' | sort -nu | paste -sd, -)
  targets=$(printf '%s' "$targets" | tr ',' '\n' | sort -u | paste -sd, -)
  command -v nft >/dev/null 2>&1 || die "nft not found"
  command -v python3 >/dev/null 2>&1 || die "python3 not found (verify needs it)"

  # 1. the guard cgroup — created once, always delegated to the benchmark user
  mkdir -p "$CGROUP" || die "cannot create $CGROUP"
  chown -R "$owner" "$CGROUP" || die "cannot delegate $CGROUP to $owner"

  # 2. the attach helper: a root-owned copy of this very file, plus the
  #    one NOPASSWD sudoers line that scopes root to exactly that copy.
  #    sudoers is validated *before* it is installed (visudo -c rejects it
  #    otherwise we would lock ourselves out of sudo entirely).
  command -v visudo >/dev/null 2>&1 || die "visudo not found"
  command -v setpriv >/dev/null 2>&1 || die "setpriv not found (util-linux)"
  mkdir -p "$(dirname "$HELPER")" || die "cannot create $(dirname "$HELPER")"
  if [ "$SELF" != "$HELPER" ]; then
    install -m 0755 -o root -g root "$SELF" "$HELPER" || die "cannot install $HELPER"
  fi
  local sudotmp
  sudotmp=$(mktemp) || die "mktemp failed"
  printf '%s ALL=(root) NOPASSWD: %s *\n' "$owner" "$HELPER" > "$sudotmp"
  chmod 0440 "$sudotmp"
  if ! visudo -cf "$sudotmp" >/dev/null 2>&1; then
    rm -f "$sudotmp"
    die "generated sudoers entry failed visudo -c"
  fi
  mv "$sudotmp" "$SUDOERS" || die "cannot install $SUDOERS"

  # 3. the rules — delete + rebuild (only happens on first install or when the
  #    configured endpoint ports change; no sandbox runs while we install)
  local tmp
  tmp=$(mktemp) || die "mktemp failed"
  write_rules "$ports" "$targets" > "$tmp"
  nft delete table inet "$TABLE" 2>/dev/null || true
  if ! nft -f "$tmp"; then
    rm -f "$tmp"
    die "failed to load nftables rules"
  fi
  rm -f "$tmp"

  # 4. the stamp so unprivileged code can check freshness (helper_sha pins the
  #    installed helper/rules to this exact version of the script)
  printf 'version=%s\ntargets=%s\nowner=%s\nhelper_sha=%s\ninstalled_at=%s\n' \
    "$VERSION" "$targets" "$owner" \
    "$(sha256sum "$SELF" | cut -d' ' -f1)" \
    "$(date -Is 2>/dev/null || date)" >"$STAMP" ||
    die "cannot write $STAMP"

  echo "netguard: installed (endpoints: ${targets:-none}, helper: $HELPER)"
  cmd_verify "$ports" "$targets" || die "post-install verification FAILED — guard not usable"
}

cmd_uninstall() {
  need_root
  nft delete table inet "$TABLE" 2>/dev/null || true
  rm -f "$STAMP" "$SUDOERS" "$HELPER"
  if [ -d "$CGROUP" ]; then
    local pids pid n=0
    pids=$(cat "$CGROUP/cgroup.procs" 2>/dev/null || true)
    while read -r pid; do
      [ -n "$pid" ] || continue
      echo "$pid" > /sys/fs/cgroup/cgroup.procs 2>/dev/null && n=$((n + 1))
    done <<<"$pids"
    if [ "$n" -gt 0 ]; then
      echo "netguard: warning: moved $n live process(es) back to the root cgroup" >&2
    fi
    rmdir "$CGROUP" 2>/dev/null || true
  fi
  echo "netguard: removed"
}

cmd_status() {
  local rc=0 targets
  if stamp_version_ok; then
    targets=$(sed -n 's/^targets=//p' "$STAMP")
    echo "stamp:  ok (version=$VERSION, endpoints: ${targets:-none})"
  else
    echo "stamp:  missing or stale ($STAMP)"
    rc=1
  fi
  if [ -d "$CGROUP" ]; then
    echo "cgroup: ok ($CGROUP)"
  else
    echo "cgroup: missing ($CGROUP)"
    rc=1
  fi
  if [ -x "$HELPER" ] && [ -f "$SUDOERS" ]; then
    echo "helper: ok ($HELPER)"
  else
    echo "helper: missing ($HELPER / $SUDOERS)"
    rc=1
  fi
  local err
  if err=$(nft list table inet "$TABLE" 2>&1); then
    echo "nft:    ok (table inet $TABLE)"
  elif printf '%s' "$err" | grep -qiE 'permission|not permitted|operation not'; then
    echo "nft:    present? (cannot check without root: sudo $0 status)"
  else
    echo "nft:    missing (table inet $TABLE)"
    rc=1
  fi
  return "$rc"
}

# --------------------------------------------------------------------------- #
# exec-as — the attach helper. Runs under sudo, as root, from the sandbox's
# start path: enter the guard cgroup (root may cross nsdelegate boundaries),
# then drop to the invoking user *before* exec so nothing runs privileged.
# --------------------------------------------------------------------------- #

cmd_exec_as() {
  [ "$#" -ge 1 ] || die "exec-as: no command given"
  [ -d "$CGROUP" ] || die "exec-as: guard cgroup $CGROUP missing — run: sudo $0 install <owner> <ports>"
  suid="${SUDO_UID:-}"
  echo $$ > "$CGROUP/cgroup.procs" || die "exec-as: cannot enter $CGROUP"
  if [ -n "$suid" ] && [ "$suid" -ne 0 ] 2>/dev/null; then
    grp=$(id -g "$suid") || die "exec-as: unknown uid $suid"
    home=$(awk -F: -v u="$suid" '$3 == u {print $6}' /etc/passwd)
    # drop env sudoers consider its own, then exec as the invoking user
    unset SUDO_UID SUDO_GID SUDO_USER SUDO_COMMAND
    export HOME="${home:-/}"
    exec setpriv --reuid "$suid" --regid "$grp" --init-groups "$@"
  fi
  exec "$@"
}

# --------------------------------------------------------------------------- #
# verify — spawn a process inside the cgroup and assert its real behaviour
# --------------------------------------------------------------------------- #

cmd_verify() {
  need_root
  local ports="${1:-}" targets="${2:-}"
  valid_ports "$ports" || die "bad ports '${ports}'"
  valid_targets "$targets" || die "bad targets '${targets}'"
  nft list table inet "$TABLE" >/dev/null 2>&1 || die "table inet $TABLE not loaded"
  [ -d "$CGROUP" ] || die "cgroup $CGROUP missing"
  command -v python3 >/dev/null 2>&1 || die "python3 not found"

  echo "netguard: verifying (ports: ${ports:-none} targets: ${targets:-none}) ..."

  # listeners: one "endpoint" (first guarded port), one foreign host service,
  # and later one service started *inside* the cgroup
  local eport efirst fport oport ep_pid="" fp_pid="" op_pid=""
  efirst=$(printf '%s' "$ports" | cut -d, -f1)
  if [ -z "$efirst" ] || [ "$efirst" = "0" ]; then
    eport=""                       # no loopback endpoint ports configured
  elif tcp_open 127.0.0.1 "$efirst"; then
    eport=$efirst                      # the real endpoint is already up
  else
    if ep_pid=$(start_listener "$efirst"); then
      eport=$efirst
    else
      die "cannot listen on endpoint port $efirst (needed for the test)"
    fi
  fi
  fport=$(pick_port "$ports") || die "no free test port"
  fp_pid=$(start_listener "$fport") || die "cannot start foreign test listener"
  oport=$(pick_port "$ports") || die "no free test port"

  # non-loopback targets: one listener per target host (temp unless the real
  # endpoint is already answering), plus one foreign listener on the first
  # such host to prove anything unlisted stays blocked there too
  local taddrs="" tp_pids="" t h p tp_pid
  for t in ${targets//,/ }; do
    [ -n "$t" ] || continue
    h=${t%:*}; p=${t##*:}
    case "$h" in 127.0.0.1|"::1"|localhost) continue;; esac
    taddrs="${taddrs} $t"
    if tcp_open "$h" "$p"; then
      : # the real endpoint is already up — probe it directly
    else
      tp_pid=$(start_listener_on "$h" "$p") \
        || die "cannot listen on target $t (needed for the test)"
      tp_pids="${tp_pids} $tp_pid"
    fi
  done
  local neg_host="" neg_port="" neg_pid=""
  for t in $taddrs; do
    neg_host=${t%:*}
    neg_port=$(pick_port_on "$neg_host" "$ports") || die "no free test port on $neg_host"
    neg_pid=$(start_listener_on "$neg_host" "$neg_port") \
      || die "cannot start foreign $neg_host listener"
    break
  done

  local res
  res=$(mktemp) || die "mktemp failed"

  # ---- inside the guard cgroup (this is what the sandbox experiences) ----
  bash -c '
    cg=$1; eport=$2; fport=$3; oport=$4; out=$5; taddrs=$6; neg=$7
    if ! echo $$ > "$cg/cgroup.procs" 2>/dev/null; then
      echo "attach:FAIL" > "$out"; exit 0
    fi
    ( exec python3 -m http.server "$4" --bind 127.0.0.1 >/dev/null 2>&1 ) &
    ownpid=$!
    sleep 0.6
    if ! kill -0 "$ownpid" 2>/dev/null; then
      echo "own:STARTFAIL" >> "$out"; exit 0
    fi
    echo "ownpid:$ownpid" >> "$out"
    if [ -n "$eport" ]; then
      if timeout 3 bash -c "exec 3<>/dev/tcp/127.0.0.1/$eport" 2>/dev/null; then
        echo "endpoint:OK" >> "$out"; else echo "endpoint:BLOCKED" >> "$out"; fi
    else
      echo "endpoint:SKIP" >> "$out"
    fi
    if timeout 3 bash -c "exec 3<>/dev/tcp/127.0.0.1/$oport" 2>/dev/null; then
      echo "own:OK" >> "$out"; else echo "own:BLOCKED" >> "$out"; fi
    if timeout 3 bash -c "exec 3<>/dev/tcp/127.0.0.1/$fport" 2>/dev/null; then
      echo "foreign:OK" >> "$out"; else echo "foreign:BLOCKED" >> "$out"; fi
    if timeout 3 bash -c "exec 3<>/dev/tcp/1.1.1.1/443" 2>/dev/null; then
      echo "remote:OK" >> "$out"; else echo "remote:BLOCKED" >> "$out"; fi
    if timeout 3 python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(2)
s.sendto(bytes.fromhex(\"123401000001000000000000076578616d706c6503636f6d0000010001\"),
         (\"127.0.0.53\", 53))
s.recvfrom(512)
" 2>/dev/null; then
      echo "dns:OK" >> "$out"; else echo "dns:BLOCKED" >> "$out"; fi
    for t in $taddrs; do
      h=${t%:*}; p=${t##*:}
      if timeout 3 bash -c "exec 3<>/dev/tcp/$h/$p" 2>/dev/null; then
        echo "target:$t:OK" >> "$out"; else echo "target:$t:BLOCKED" >> "$out"; fi
    done
    if [ -n "$neg" ]; then
      h=${neg%:*}; p=${neg##*:}
      if timeout 3 bash -c "exec 3<>/dev/tcp/$h/$p" 2>/dev/null; then
        echo "targetneg:OK" >> "$out"; else echo "targetneg:BLOCKED" >> "$out"; fi
    fi
  ' _ "$CGROUP" "$eport" "$fport" "$oport" "$res" "$taddrs" "${neg_host:+$neg_host:$neg_port}"

  # ---- host side (the host must keep working) ----
  local host_foreign host_endpoint
  if tcp_open 127.0.0.1 "$fport"; then host_foreign=OK; else host_foreign=BLOCKED; fi
  if tcp_open 127.0.0.1 "$eport"; then host_endpoint=OK; else host_endpoint=BLOCKED; fi

  # ---- assert ----
  local fails=0 line
  expect() { # label expected actual
    if [ "$2" = "$3" ]; then
      echo "  PASS  $1"
    else
      echo "  FAIL  $1 (expected $2, got $3)"
      fails=$((fails + 1))
    fi
  }
  get() { sed -n "s/^$1://p" "$res" | head -1; }

  if grep -qx "attach:FAIL" "$res"; then
    echo "  FAIL  could not enter the guard cgroup"
    fails=$((fails + 1))
  else
    if [ "$(get endpoint)" = "SKIP" ]; then
      echo "  SKIP  no loopback endpoint ports configured"
    else
      expect "sandbox -> endpoint port"            OK    "$(get endpoint)"
    fi
    expect "sandbox -> its own local service"      OK    "$(get own)"
    expect "sandbox -> foreign local service"      BLOCKED "$(get foreign)"
    expect "sandbox -> internet"                   BLOCKED "$(get remote)"
    expect "sandbox -> DNS (127.0.0.53)"           BLOCKED "$(get dns)"
    expect "host    -> foreign local service"      OK    "$host_foreign"
    expect "host    -> endpoint port"              OK    "$host_endpoint"
    for t in $taddrs; do
      expect "sandbox -> endpoint target $t"       OK    "$(get "target:$t")"
    done
    if [ -n "$neg_host" ]; then
      if tcp_open "$neg_host" "$neg_port"; then neg_host_state=OK; else neg_host_state=BLOCKED; fi
      expect "host    -> foreign $neg_host service" OK  "$neg_host_state"
      expect "sandbox -> foreign $neg_host service" BLOCKED "$(get targetneg)"
    fi
  fi

  # ---- cleanup ----
  op_pid=$(sed -n 's/^ownpid://p' "$res" | head -1)
  [ -n "$op_pid" ] && kill "$op_pid" 2>/dev/null
  [ -n "$ep_pid" ] && kill "$ep_pid" 2>/dev/null
  [ -n "$fp_pid" ] && kill "$fp_pid" 2>/dev/null
  [ -n "$neg_pid" ] && kill "$neg_pid" 2>/dev/null
  for tp_pid in $tp_pids; do kill "$tp_pid" 2>/dev/null; done
  rm -f "$res"
  sleep 0.2

  if [ "$fails" -gt 0 ]; then
    echo "netguard: $fails check(s) FAILED"
    return 1
  fi
  echo "netguard: all checks passed"
  return 0
}

# --------------------------------------------------------------------------- #

cmd="${1:-}"
case "$cmd" in
  install)   shift; cmd_install "$@" ;;
  uninstall) shift; cmd_uninstall "$@" ;;
  status)    shift; cmd_status "$@" ;;
  verify)    shift; cmd_verify "$@" ;;
  exec-as)   shift; cmd_exec_as "$@" ;;
  *) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
