# nejm-skills Installation Guide

This fork is a local Codex skill repository, not a Python or npm package.

## Clone

```bash
git clone https://github.com/wangyichen25/nejm-skills.git ~/.codex/repos/nejm-skills
cd ~/.codex/repos/nejm-skills
```

## Install NEJM-Style Skills

```bash
mkdir -p ~/.codex/skills
for d in skills/nejm-*; do
  ln -sfn "$PWD/$d" ~/.codex/skills/$(basename "$d")
done
```

## Install NEJM-Style and Nature-Style Skills

```bash
mkdir -p ~/.codex/skills
for d in skills/nejm-* skills/nature-*; do
  ln -sfn "$PWD/$d" ~/.codex/skills/$(basename "$d")
done
```

Restart Codex after changing installed skills.

## Update an Existing Clone

```bash
git pull
for d in skills/nejm-* skills/nature-*; do
  ln -sfn "$PWD/$d" ~/.codex/skills/$(basename "$d")
done
```

## Current Machine

On this machine, the active skills are managed as symlinks from:

```text
~/.codex/skills/
```

to the fork checkout under:

```text
~/.codex/repos/nejm-skills/
```

If the checkout moves, recreate the symlinks with the install commands above.
