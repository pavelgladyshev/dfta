# parkinfo: model and conformance-test harness

Files
- `parkinfo/` — the PHP web application (parkinfo.php, reserve.php, release.php, parkinfo.css).
- `model.py` — the formal model: sets O, L, V, S; lpark(); the 209 valid states and the 16 states of A (1056 bytes).
- `measure_sizes.py` — the conformance-test harness. `python3 measure_sizes.py --walk` builds the input-complete
  transition graph (1088 state-changing transitions + 3928 rejected requests as self-loops = 5016 edges), constructs an
  Eulerian circuit with Hierholzer's algorithm, executes it against the live system, and after every request checks
  the Redis state, the response-body length, and the size field Apache logged, all against the model.

Test system used in the paper
- Ubuntu 24.04.1 LTS (Multipass VM), Apache 2.4.58, PHP 8.3.6 with the redis extension, Redis 7.0.15, Python 3.12.3.
- The application is served from the Apache document root; basic authentication with the users
  `johnson`, `anonymous`, `lowry`, `hyde` (password `parkpass`, see `PASSWORD` in the harness).
- Apache must write a body-length access log, because Ubuntu's stock `common` and `combined` formats record `%O`
  (bytes sent including headers), not `%b`. Add to the site configuration and reload Apache:

      LogFormat "%h %l %u %t \"%r\" %>s %b" clf_body
      CustomLog /var/log/parkinfo_clf.log clf_body

- Run the harness inside the VM: `python3 measure_sizes.py --walk`.
