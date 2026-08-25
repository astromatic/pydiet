## Python API documentation

When creating or modifying Python code, keep the public API documentation complete and consistent.

Use `src/pydiet/server/types/quantity.py` as the reference for docstring style, structure, terminology, level of detail, and examples. Inspect it before making substantial documentation changes.

For public classes, methods, functions, and properties:

- Add missing docstrings and complete incomplete ones.
- Preserve good existing prose; do not rewrite docstrings unnecessarily.
- Document actual behavior based on the implementation, including arguments, defaults, return values, public attributes, relevant side effects, assumptions, and exceptions where useful.
- Consult tests and existing call sites when needed to understand intended usage.
- Never infer or invent behavior merely from names or type annotations.
- Do not document private implementation details unless they are important for understanding the public API.

### Examples

Add useful `Examples` sections to new and existing docstrings where appropriate, following the reference module.

Examples must:

- use doctest syntax (`>>>`);
- demonstrate realistic, common usage with small, deterministic inputs;
- be executable whenever reasonably possible;
- use actual verified output, never guessed output;
- avoid network access, external files, expensive computations, nondeterminism, and platform-dependent output when possible;
- remain compact, especially for numerical arrays and other verbose objects.

Treat doctest examples as tests. Run new or modified examples and the relevant doctests/tests whenever possible. Do not use ellipses, output suppression, or similar tricks merely to hide an incorrect result.

### Scope

Keep documentation changes focused: do not refactor or alter program behavior merely to improve docstrings.

If an existing docstring disagrees with the implementation, update stale documentation when the intended behavior is clear. If the discrepancy may instead reveal a code bug, do not silently change the code; report it.

Document the public Python API of this package according to the docstring rules in AGENTS.md.

Use src/pydiet/server/types/quantity.py as the reference module.

Add or complete docstrings and doctest examples throughout the package, preserving good existing documentation. Run the relevant doctests/tests after making the changes and report any implementation/documentation inconsistencies you encounter.

## ECMAScript API documentation

When creating or modifying ECMAScript code, keep the public API documentation complete and consistent.

Use example.js as the reference for JSDoc style, structure, terminology, level of detail, tags, and examples. Inspect it before making substantial documentation changes.

For public classes, constructors, methods, functions, properties, getters/setters, and other exported API elements:

- Add missing JSDoc comments and complete incomplete ones.
- Preserve good existing documentation; do not rewrite it unnecessarily.
- Document actual behavior based on the implementation, including parameters, defaults, return values, public properties, relevant side effects, assumptions, and thrown exceptions where useful.
- Follow the reference module for the use and formatting of JSDoc tags such as `@param`, `@returns`, `@throws`, `@property`, `@typedef`, and `@example`.
- Consult tests and existing call sites when needed to understand intended usage.
- Never infer or invent behavior merely from names or type annotations.
- Do not document private implementation details unless they are important for understanding the public API.
- Keep JSDoc type expressions consistent with the conventions already used by the project.

### Examples

Add useful `@example` sections to new and existing JSDoc comments where appropriate, following the reference module.

Examples must:

- demonstrate realistic, common usage with small, deterministic inputs;
- use the public API rather than implementation details;
- be executable whenever reasonably possible;
- contain only behavior and output that have been verified from the implementation;
- avoid network access, external files, expensive computations, nondeterminism, and platform-dependent behavior when possible;
- remain compact and focused on illustrating the documented API.

Treat examples as code that should remain valid. Run or otherwise verify new or modified examples whenever practical, and run the relevant tests and documentation/JSDoc checks provided by the project.

### Scope

Keep documentation changes focused: do not refactor or alter program behavior merely to improve JSDoc comments.

If existing documentation disagrees with the implementation, update stale documentation when the intended behavior is clear. If the discrepancy may instead reveal a code bug, do not silently change the code; report it.
