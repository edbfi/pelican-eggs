# Panel export CI

Every PR and default-branch push validates the repository's 2 panel exports,
all tracked JSON/YAML data, unique JSON keys, required export fields, environment
variable uniqueness and embedded installation-script syntax. The validator accepts
the actual PTDL/PLCN versions present here, including native Pelican YAML. It is a
focused repository contract, not a replacement for a real panel import test.

Run `uv run --no-project --with-requirements .github/requirements.txt python .github/scripts/check-eggs.py`
locally with Python, uv 0.12.10, Bash and BusyBox. PyYAML is versioned in the CI
requirements file and maintained by Renovate. Embedded CRLF is normalized exactly
as Wings does before execution; Bash parses with extglob enabled, and ash scripts
use BusyBox ash. Parsing never downloads or installs a game server.

The shared `ci / required` gate rejects failed, cancelled, missing or skipped
prerequisites and checks explicit PR dispatch identities before and after checks.
Tokens are read-only and action references use full version tags. Shared changes
arrive as version updates from `edbfi/automation`; repository checks remain
local so panel-specific behavior can evolve independently.

No application formatter or fake test suite is imposed on panel-generated data.
Real panel imports, container availability and game-server installation/startup
remain manual checks. Generated export corrections must also be reflected in the
source panel to survive re-export. Upstream paths and container choices remain
unchanged by CI adoption.

No branch protections or rulesets are configured; automerge remains off.
Manually review exact head/base, full diff, author/DCO, every expected CI job and
relevant artifacts before merging through the maintainer ghmerge function.

HumanitZ also runs `check-pair.py` with the same uv environment to compare startup,
config, installation, file denylist and variable behavior across its two formats.
`python3 -m unittest discover -s tests -v` tests the actual INI helper using
temporary files: player settings survive, missing keys/sections are added,
repeated runs are idempotent, missing inputs and write failures stay nonfatal.
No panel export or shipped helper behavior changes are needed for this baseline.
