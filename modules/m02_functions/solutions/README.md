# Reference solutions — STOP

Do not read these until your own version passes all tests.

Reading a solution before you've struggled produces the illusion of understanding. You'll nod
along, recognize every construct, and then be unable to write it a week later. The struggle *is*
the encoding step.

## How to use this folder properly

1. Get all tests green with your own code.
2. Commit your version.
3. *Then* open the reference and diff it against yours.
4. For every difference, ask: **is this shorter, or is it clearer?** Sometimes the reference is
   just terser and yours is better. Sometimes it uses an idiom you didn't know existed — that's
   the one to write down.

Things worth looking for in the diff:

- `dict.fromkeys` for ordered dedup
- `defaultdict` vs `setdefault` — when each reads better
- a tuple sort key `(-count, name)` for "descending by X, ascending by Y"
- `itertools.accumulate`
- `zip(values, values[1:])` as a sliding window
- the walrus operator inside a comprehension filter
- `str.translate` + `str.maketrans` for bulk character replacement
- `str.partition` when you need "split on the first separator, and tell me if there was one"
- `shlex.split` instead of a hand-rolled quote parser
- strict-primitive / lenient-wrapper (`parse_line` raises, `parse_lines` doesn't)

If your solution is longer but a colleague would understand it faster, keep yours. Idiomatic
does not mean short.
