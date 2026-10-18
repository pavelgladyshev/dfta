# Known-defect check for the test system's components

Date of check: 2026-10-18.

The paper presumes the standard components of the test system to behave as
specified and records their versions. Its first guideline asks that the
published defect lists for those versions be checked for the functions the
bespoke code relies on. This note records that check.

## Versions

Read from the test virtual machine (Multipass instance `primary`, Ubuntu
24.04.1 LTS) with `dpkg-query` on the date of the check:

| Component | Upstream version in the paper | Ubuntu package on the VM |
|---|---|---|
| Apache httpd | 2.4.58 | apache2 2.4.58-1ubuntu8.13 |
| PHP (as mod_php; php8.3-fpm is not installed) | 8.3.6 | php8.3, libapache2-mod-php8.3 8.3.6-0ubuntu0.24.04.9 |
| phpredis (PHP Redis extension) | 5.3.7 | php8.3-redis 5.3.7+4.3.0-3ubuntu1 |
| Redis | 7.0.15 | redis-server 5:7.0.15-1ubuntu0.24.04.4 |

Apache modules loaded that bear on the functions relied on: log_config
(static), auth_basic, authn_file, php (mod_php), deflate. The Ubuntu
change logs consulted below are those of the later patch levels current on
the date of the check (apache2 2.4.58-1ubuntu8.16, php8.3
8.3.6-0ubuntu0.24.04.11, redis 5:7.0.15-1ubuntu0.24.04.5), which include
the VM's patch levels; the difference is later security backports only.

## Functions relied on

- Apache: basic authentication (mod_auth_basic with a file provider),
  invocation of the PHP scripts, and the `%b` field written by
  mod_log_config under the `clf_body` format described in README.md.
- PHP: execution of parkinfo.php, reserve.php and release.php, which use
  `echo`, `htmlspecialchars`, `in_array`, `$_SERVER['PHP_AUTH_USER']`,
  `$_SERVER['REQUEST_METHOD']` and `$_POST`.
- phpredis: `Redis::connect`, `Redis::get`, `Redis::set` (no optional
  arguments).
- Redis: `GET` and `SET` on string keys (and `SETNX` in install.sh).

## Sources (all retrieved 2026-10-18)

- Apache change log: https://downloads.apache.org/httpd/CHANGES_2.4
  (entries for 2.4.59 to 2.4.69).
- Apache security list: https://httpd.apache.org/security/vulnerabilities_24.html
- Ubuntu apache2 package change log:
  https://changelogs.ubuntu.com/changelogs/pool/main/a/apache2/apache2_2.4.58-1ubuntu8.16/changelog
- PHP change log: https://www.php.net/ChangeLog-8.php (entries for 8.3.7 to 8.3.35).
- phpredis change log: https://github.com/phpredis/phpredis/blob/develop/CHANGELOG.md
  (entries after 5.3.7, i.e. 6.0.0 to 6.1.0).
- Redis release notes for the 7.0, 7.2 and 7.4 branches:
  https://raw.githubusercontent.com/redis/redis/7.0/00-RELEASENOTES (and `7.2`, `7.4`).
- Individual items read in full: httpd commit ca0bb271d3 (trunk r1921305,
  bugzilla PR 65222, GitHub pull request #490); phpredis commit f73f5fcc;
  php-src issues GH-14553, GH-14808, GH-20352.

## Method

Every change-log and security entry issued after the deployed upstream
version was searched for keywords naming the functions relied on, and every
matching entry was read in full. Entries matching no keyword were not read,
so a defect described in other words could have been missed.

Keywords: Apache -- mod_log_config, %b, bytes sent, response body,
Content-Length, chunk, mod_auth_basic, mod_authn, mod_authz, http_filters,
core output, mod_cgi, mod_proxy_fcgi, mod_php, brigade, keepalive, HTTP/1.1,
request body, ap_log, logging, access log, mod_deflate, and entries whose
first line begins with "core". PHP -- apache2handler, apache,
htmlspecialchars, PHP_AUTH, in_array, output buffer, ob_, echo, print,
Content-Length, SAPI, header(, $_SERVER, redis. phpredis -- get, set,
connect, auth, string, reply, unix, socket, session. Redis -- SET, GET,
SETNX, string command, t_string, CVE.

## Findings

Apache httpd, 2.4.59 to 2.4.69 (about 250 change-log entries, 74 CVEs).
One entry touches the logging module: 2.4.63, "mod_log_config: Fix merging
for the LogFormat directive" (PR 65222). The fix is a one-line change in
`merge_config_log_state` (modules/loggers/mod_log_config.c) that swaps the
order of `apr_table_overlay(p, base->formats, add->formats)`, i.e. the
precedence between a LogFormat nickname defined at server level and the
same nickname defined again in a virtual host. The test configuration
defines `clf_body` once, so it is not affected, and the conformance walk
compares the logged `%b` value with the response-body length after every
one of its 5016 requests in any case. Ubuntu did not backport this fix (it
is not a security fix), so it was present on the test system. On the
security list, mod_auth_basic does not appear anywhere in the history of
2.4; mod_log_config appears in CVE-2014-0098 (fixed in 2.4.8) and in
CVE-2024-47252 (fixed in 2.4.64), which concerns the escaping of mod_ssl
variables logged with `%{varname}x` or `%{varname}c`, not used in
`clf_body`. The other CVEs fixed after 2.4.58 concern HTTP/2, mod_rewrite,
mod_proxy and its submodules, mod_dav, mod_ssl, mod_auth_digest, SSI, CGI
scripts, mod_session, mod_userdir and response-header splitting; none
changes what `%b` counts. CVE-2024-39884 and CVE-2024-40725 (source
disclosure with handlers configured via AddType) do not apply to Ubuntu's
mod_php configuration, which uses SetHandler.

PHP, 8.3.7 to 8.3.35. No entry concerns htmlspecialchars, in_array,
PHP_AUTH_USER, $_SERVER or the Apache SAPI. Three output-related entries:
GH-14553 (8.3.10, `echo` output truncated at a NUL byte) affects only the
phpdbg SAPI, and the scripts emit no NUL bytes; GH-14808 (8.3.10) and
GH-20352 (8.3.30) concern `ob_*` output handlers, which the scripts do not
use.

phpredis, 6.0.0 to 6.1.0. The fixes to `SET` (argument order when options
are given, commit f73f5fcc; PXAT/EXAT; KEEPTTL; IFEQ) all concern optional
arguments, which the scripts do not pass. No fix concerns `get` or
`connect`; the pipeline-reconnect fix concerns a mode the scripts do not
use.

Redis. 7.0.15 is the last release of the 7.0 branch. The bug fixes and
CVEs in the 7.2 and 7.4 branches concern Lua scripting, ACL selectors,
HyperLogLog, SORT_RO, the order of listen(2) and chmod(2), unbounded output
buffers and redis-check-aof; none concerns `GET`, `SET` or `SETNX`.

## Result

No published defect in the deployed versions of Apache, PHP, phpredis or
Redis affects the functions the parkinfo scripts rely on. The one fix to
Apache's logging module concerns a configuration the test system does not
use.
