# Meeting minutes exercise · editorial candidate R1

This candidate places a bilingual exercise immediately after the heading targeted by the video's `#section-4` link. Readers compare the approved design with an AI-generated assignment, then reveal the answer using a native HTML disclosure. Each language has one editable fragment.

From the repository root, prepare and check the UTF-8 page diff:

```sh
python docs/release-candidates/meeting-notes-r1-20261123/prepare.py > meeting-notes.patch
git apply --check meeting-notes.patch
```

The script checks the SHA-256 of each input page and writes the patch to standard output. Use a disposable copy of the static site to preview the diff. The candidate keeps the current release manifest, route roster and deployed files intact. A future release needs the current production parent and matching Next/Markdown sources in the normal admission process.

Prepared against main commit `2444bd77f7616ba916c37b2b3bcba11898926be0`. On 23 November 2026 the public RU and EN article bytes matched the two checked inputs. At that time the full public manifest SHA-256 was `c70f71cc58d4977b82600adf5b12db773606542573d28ad309cde4ad39d94799` and the main branch manifest SHA-256 was `66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5`.
