# F01 Tokenize
Shipped `words()`: lowercase, then runs of a–z. Non-ASCII letters separate words (decision F01-ascii).
Known gap: `café` counts as `caf`. That matches the mission, but may surprise users.
