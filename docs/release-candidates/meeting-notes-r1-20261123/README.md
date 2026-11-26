# Meeting minutes exercise · editorial candidate R1

The two Markdown fragments are the sole sources of the exercise copy. They add a practical example at the start of the adult guide’s fourth section. Readers compare the meeting notes with an AI-generated assignment and write down their answers before reading the worked example below.

From the repository root, generate a single UTF-8 patch for both canonical guides and both static articles:

```sh
python -B docs/release-candidates/meeting-notes-r1-20261123/prepare.py > meeting-notes.patch
git apply --check meeting-notes.patch
```

For a preview, apply the patch in a disposable checkout. The generator verifies the SHA-256 of all four inputs and verifies that the repository's guide renderer produces the complete original article body. It uses the same renderer to generate the revised body while preserving each page's surrounding bytes. The existing Next and Python renderers support all markup in the fragments.

The committed candidate leaves the current Markdown, release manifest, deployed files and admission checks intact. Incorporate the four-file patch when preparing a new release from the authoritative production parent. Its source and static hashes will need separate admission for that successor.

Prepared against main commit `2444bd77f7616ba916c37b2b3bcba11898926be0`. On 23 November 2026 the public RU and EN article bytes matched the checked static inputs. The full public manifest SHA-256 was `c70f71cc58d4977b82600adf5b12db773606542573d28ad309cde4ad39d94799`; the main branch manifest SHA-256 was `66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5`.
