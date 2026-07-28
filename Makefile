# Apex — top-level verification runner.
#
# One command verifies the whole monorepo:
#
#     make test
#
# Each lane is a separate Python project with its own dependency set, so tests
# CANNOT be run from a single interpreter — `pytest` at the repo root collects
# all eight lanes into one environment and dies during collection. `uv run`
# inside each lane directory is the only correct invocation, and it bootstraps
# the environment on a clean clone.
#
# Tests that need live ClickHouse skip themselves rather than fail, so `make
# test` is green on a machine with no infrastructure running. `make verify-e2e`
# is the separate, infrastructure-dependent gate.

SHELL := /bin/bash
.DEFAULT_GOAL := help

PY_LANES := engine serve memory verify
UV       := uv

# ANSI, but only when stdout is a TTY (keeps CI logs clean).
ifneq (,$(findstring xterm,$(TERM)))
  G := \033[0;32m
  R := \033[0;31m
  Y := \033[0;33m
  B := \033[1m
  N := \033[0m
endif

.PHONY: help test test-py test-jar test-root $(addprefix test-,$(PY_LANES)) verify-e2e verify-ddl clean lanes

help: ## Show this help
	@printf "$(B)Apex$(N) — agentic performance intelligence for Apache Spark\n\n"
	@printf "$(B)Verification$(N)\n"
	@grep -hE '^[a-z][a-zA-Z0-9_-]*:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
	@printf "\n$(B)Lanes$(N)  dev → jar → collect → infra → engine → serve  (+ memory, verify)\n"
	@printf "Contract: CONTRACT.md — the frozen interface every lane obeys.\n"

## ---------------------------------------------------------------------------
## test — the whole repo, one command
## ---------------------------------------------------------------------------

test: ## Run every test suite (Python lanes + jar + root gate); non-zero if any fail
	@failed=""; \
	for lane in $(PY_LANES); do \
	  printf "$(B)── %s ─────────────────────────────────────$(N)\n" "$$lane"; \
	  if ( cd $$lane && $(UV) run --extra dev pytest -q -p no:warnings ); then \
	    :; \
	  else \
	    failed="$$failed $$lane"; \
	  fi; \
	done; \
	printf "$(B)── root (six-lane gate) ──────────────────$(N)\n"; \
	if ( cd engine && $(UV) run --extra dev pytest ../tests -q -p no:warnings ); then \
	  :; \
	else \
	  failed="$$failed root"; \
	fi; \
	printf "$(B)── jar (Scala) ───────────────────────────$(N)\n"; \
	if ! command -v sbt >/dev/null 2>&1; then \
	  printf "$(R)NOT RUN$(N)  sbt is not installed — the jar suite was NOT verified.\n"; \
	  printf "         brew install sbt, or rely on CI. Refusing to report green.\n"; \
	  failed="$$failed jar(sbt-missing)"; \
	else \
	  jv=$$( cd jar && sbt -batch 'eval System.getProperty("java.specification.version")' 2>/dev/null \
	         | grep -oE 'ans: String = [0-9]+' | grep -oE '[0-9]+$$' ); \
	  $(MAKE) --no-print-directory _jar-cells JV="$$jv" || failed="$$failed jar"; \
	fi; \
	echo; \
	if [ -n "$$failed" ]; then \
	  printf "$(R)$(B)FAILED:$(N)$$failed\n"; exit 1; \
	fi; \
	printf "$(G)$(B)ALL SUITES GREEN$(N)\n"

test-py: ## Run only the Python lane suites
	@for lane in $(PY_LANES); do ( cd $$lane && $(UV) run --extra dev pytest -q -p no:warnings ) || exit 1; done

test-jar: ## Run only the jar (Scala) suite (4 cross-build cells; 4.x needs JDK 17/21)
	@command -v sbt >/dev/null 2>&1 || { echo "sbt not installed"; exit 1; }
	@jv=$$( cd jar && sbt -batch 'eval System.getProperty("java.specification.version")' 2>/dev/null \
	        | grep -oE 'ans: String = [0-9]+' | grep -oE '[0-9]+$$' ); \
	 $(MAKE) --no-print-directory _jar-cells JV="$$jv"

# build.sbt is a 4-cell matrix: apex_35 x {2.12, 2.13} run on JDK 8/11/17, but
# apex_40 and apex_41 need JDK 17+ (Spark 4 dropped 11). sbt's forked test JVM
# inherits sbt's own JVM — Test/javaHome is None and $JAVA_HOME does NOT override
# it — so on a JDK 11 sbt the 4.x cells abort with UnsupportedClassVersionError.
# Run what CAN be verified and say plainly what could not. A blanket failure that
# doesn't distinguish "broken" from "wrong JDK" is how 2 of 4 published cells went
# unverified in the first place.
.PHONY: _jar-cells
_jar-cells:
	@if [ -z "$(JV)" ]; then echo "could not determine sbt's JVM version"; exit 1; fi
	@if [ "$(JV)" -ge 17 ] 2>/dev/null; then \
	  printf "  sbt JVM: Java $(JV) — all 4 cells verifiable\n"; \
	  cd jar && sbt -batch -error test; \
	else \
	  printf "  sbt JVM: Java $(JV)\n"; \
	  printf "$(Y)  PARTIAL$(N)  apex_35 (Scala 2.12 + 2.13) only.\n"; \
	  printf "$(R)  NOT VERIFIED$(N)  apex_40, apex_41 — Spark 4.x requires JDK 17+.\n"; \
	  printf "           sbt runs on Java $(JV) and its forked test JVM inherits that;\n"; \
	  printf "           JAVA_HOME does not override it. Install JDK 17 or 21 and make it\n"; \
	  printf "           sbt's JVM, or set Test/javaHome in build.sbt. CI matrixes both.\n"; \
	  cd jar && sbt -batch -error 'apex_35/test' && \
	    { printf "$(Y)  apex_35 green; 2 of 4 cells unverified — not reporting jar green.$(N)\n"; exit 1; }; \
	fi

test-root: ## Run only the root six-lane gate unit tests
	@cd engine && $(UV) run --extra dev pytest ../tests -q -p no:warnings

$(addprefix test-,$(PY_LANES)): test-%:
	@cd $* && $(UV) run --extra dev pytest -q -p no:warnings

## ---------------------------------------------------------------------------
## verify — needs live infrastructure
## ---------------------------------------------------------------------------

verify-ddl: ## Assert every ClickHouse table matches its contract DDL (needs infra up)
	@$(MAKE) -C infra verify-ddl

verify-e2e: ## Live six-lane gate against a real submitted job. Usage: make verify-e2e JOB=<app-id>
	@test -n "$(JOB)" || { echo "usage: make verify-e2e JOB=<spark-app-id>"; exit 2; }
	@echo "NOTE: use a job_id with no pre-existing apex.findings rows, OR hold"
	@echo "      \$$APEX_CLUSTER_SLOTS constant across everything that persists"
	@echo "      for this job — severity is width-dependent, so env drift alone"
	@echo "      produces persisted_finding_mismatch."
	@cd engine && $(UV) run --extra dev python ../scripts/e2e_six_lanes.py --job-id $(JOB)

lanes: ## Show tracked file count per lane
	@for d in dev jar collect infra engine serve memory verify contract docs; do \
	  printf "  %-9s %4s files\n" "$$d" "$$(git ls-files $$d | wc -l | tr -d ' ')"; \
	done

clean: ## Remove Python caches and build artifacts (does NOT touch docker volumes)
	@find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf jar/target jar/project/target
	@echo "clean"
