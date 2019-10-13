[![PyPI version](https://badge.fury.io/py/hsc.svg)](https://badge.fury.io/py/hsc)

# Hackerrank-Solution-Crawler
Crawls solutions of hackerrank and stores as local files.

## How to use it
- Pip install the package `pip install hsc`
- Run the command `hsc`
- Login with your Hackerrank Credentials
- Enter the limit of successful solutions you want to be crawled
- A new folder with name **Hackerrank** would be created with all your solutions in it

## Options to use while running script
Script `hsc` supports following options
- help:     -h or --help
- username: -u or --username -> username of hackerrank profile
- password: -p or --password -> password of hackerrank profile
- limit:    -l or --limit    -> no. of solutions to be downloaded
- offset:   -o or --offset   -> crawl solutions starting from this number
- config:   -c or --config   -> path of config file

Usage:
We can use above script helpers as
```bash
hsc -l 34 -p testpassword -u testuser
```

We can also use config file to download solutions
Let config file be /etc/user.yaml
```yaml
username: testuser
```

```bash
hsc -c /etc/user.yaml -l 34 -p testpassword
```
