<div align="center">
  <img src="docs/logo.png" alt="Arplio Voice" width="88" />
  <h1>Arplio Voice</h1>
  <p><strong>Voice cloning, voice design, video dubbing, transcription and audiobooks in 646 languages — part of Arplio Studio.</strong></p>
  <p>
    <a href="https://arplio.com">Website</a> ·
    <a href="#run-from-source">Run from source</a> ·
    <a href="#documentation">Docs</a> ·
    <a href="LICENSE">AGPL-3.0</a>
  </p>
</div>

Arplio Voice is the voice module of [Arplio Studio](https://arplio.com). It is a
rebranded fork of [VoiceStudio](https://github.com/debpalash/VoiceStudio) by
Palash Debnath and the VoiceStudio contributors, redesigned for creators: a
simpler workspace, the Arplio look, and none of the upstream project's
promotion or telemetry.

## What you can do

| Create | Produce | Listen & read |
| :--- | :--- | :--- |
| Clone a voice from a short recording | Dub videos with timed speech | Transcribe audio and video |
| Design a new voice from a description | Batch-dub many videos | Turn text into stories and audiobooks |
| Pick a ready-made voice from the gallery | Keep work in projects | Save and reuse your voices |

Models run on the machine that hosts the backend (CUDA, Apple Silicon or CPU).
Nothing is sent anywhere unless you turn a feature on.

## Run from source

```bash
git clone https://github.com/Goldenjohnny-art/arpliovoice.git
cd arpliovoice
bun install
bun run setup:api   # prepare the Python backend
bun run dev         # desktop app
# or: bun run dev:web   # browser UI at http://localhost:3901
```

Prerequisites, GPU notes and platform guides: [macOS](docs/install/macos.md) ·
[Windows](docs/install/windows.md) · [Linux](docs/install/linux.md) ·
[Docker](docs/install/docker.md) · [Troubleshooting](docs/install/troubleshooting.md).
Those guides were written for upstream VoiceStudio; the steps are the same.

Open **Voice cloning**, add a clean reference recording or pick a voice, enter
your text and generate. Install the required model when prompted.

## Documentation

| Need | Start here |
|---|---|
| Setup help | [Troubleshooting](docs/install/troubleshooting.md) · [Model downloads](docs/downloading-models.md) |
| Models & audio quality | [Engine guides](docs/engines/README.md) · [Benchmarks](docs/benchmarks.md) |
| Development | [Electron](electron/README.md) · [Changelog](CHANGELOG.md) |

## License & responsible use

Arplio Voice is free software under the [GNU AGPL-3.0](LICENSE), like the
VoiceStudio code it is based on (© 2024-present Palash Debnath and VoiceStudio
contributors; see [license notice](LICENSE-NOTICE.md)). If you run a modified
version for other people over a network, you must offer them its source code;
the app's **Settings → Source code** link points here.

Model weights, tokenizers and generated-output conditions are licensed
separately by their authors. The default `k2-fsa/OmniVoice` weights and the
NLLB translation model are **non-commercial (CC-BY-NC)**; paid or commercial
use must pick engines whose licences allow it. Model Manager shows each model's
declared licence. Clone a voice only with its owner's permission.
