# GitHub release — fast path

## Important naming note

This package uses **EngiProof** as the public-release working name.

This is a practical collision check, not trademark/legal clearance.

## Recommended first push

From the EngiProof root:

```bat
git init
git branch -M main
git add .
git commit -m "EngiProof v0.1.0 initial engineering evidence release"
```

Create an empty GitHub repository named `EngiProof`, then:

```bat
git remote add origin https://github.com/YOUR_ACCOUNT/EngiProof.git
git push -u origin main
git tag -a v0.1.0 -m "EngiProof v0.1.0"
git push origin v0.1.0
```

## With GitHub CLI

If `gh auth status` works:

```bat
gh repo create EngiProof --private --source=. --remote=origin --push
```

or, when you intentionally want a public repository:

```bat
gh repo create EngiProof --public --source=. --remote=origin --push
```

Then create the release:

```bat
git tag -a v0.1.0 -m "EngiProof v0.1.0"
git push origin v0.1.0
gh release create v0.1.0 --title "EngiProof v0.1.0" --notes-file RELEASE_NOTES_v0.1.0.md
```

## Before public release

The repository intentionally excludes source PDFs. Check that `git status` does not show private papers, credentials, machine paths, Abaqus/OrcaFlex proprietary models, or client data.

Keep the first public claim narrow: **source-bounded reproducible engineering studies with explicit evidence classes**. Do not claim full paper reproduction where only analytical/regression targets are reproduced.
