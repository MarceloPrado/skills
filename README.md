# Skills

Agent skills for iOS engineers, by [Marcelo Prado](https://github.com/MarceloPrado).

## Install

```bash
npx skills@latest add MarceloPrado/skills
```

The skills follow the Agent Skills format, so Claude Code, Codex, Cursor, and other agents that read `SKILL.md` can use them.

## Skills

| Skill | What it does |
| --- | --- |
| [iphone-duo](./skills/iphone-duo/SKILL.md) | Takes an iPhone app to iPhone Duo end to end. It learns what the app is for, audits every screen in every pose on the simulator, proposes layouts from Apple's Human Interface Guidelines, builds them in SwiftUI or UIKit, and proves the result with before and after screenshots. |

## Development

`tests/run.sh` runs the tests and type-checks every Swift snippet against the iOS 27.1 SDK.

## License

MIT
