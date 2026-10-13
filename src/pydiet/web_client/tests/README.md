# Web client tests

From `src/pydiet/web_client`, with Node.js 22.8 or later:

```sh
npm test
npm run test:coverage
```

The suite uses Node's built-in test runner; no npm install or live server is
needed. Each browser module runs in a fresh VM context with explicit DOM,
storage, network, timer, and third-party-library doubles. Single-process test
execution is safe because those contexts keep module state isolated.

The coverage command reports application modules rather than test helpers and
requires at least 90% line, branch, and function coverage. VM modules use their
source file URLs so Node can attribute coverage to the original JavaScript.
Coverage only counts loaded modules, so new modules still need explicit tests.

GitHub Actions runs the coverage command for web-client and workflow changes.
These are unit tests: they verify application behavior and chart inputs, while
actual browser rendering, Ionic components, and Chart.js interactions still
need browser testing.
