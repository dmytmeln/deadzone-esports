## Writing Style
Write all responses in strict compliance with ASD-STE100 (Simplified Technical English).

You are operating in an environment where `ast-grep` is installed.
For any code search that requires understanding of syntax or code structure, you should default to using `ast-grep --lang [language] -p '<pattern>'`.
Adjust the `--lang` flag as needed for the specific programming language.
Avoid using text-only search tools unless a plain-text search is explicitly requested.

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->
