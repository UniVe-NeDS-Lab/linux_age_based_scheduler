# Linux Age-Based Scheduler with AQM

## Running Tests

From inside the `tests/` subfolder, to start all tests run:
```
cd tests
antler run -a
```


## Antler

Antler is included as a git submodule,

We use a custom fork, available on [GitHub](https://github.com/UniVe-NeDS-Lab/antler).
To obtain it, `cd` into its folder and add the fork as remote.
```
cd antler
git remote add fork https://github.com/UniVe-NeDS-Lab/antler
git fetch fork
git switch -C main remotes/fork/main
```

To install it, run:
```
cd antler
go install
```