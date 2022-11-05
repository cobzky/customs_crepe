# Customs Crepe
## Author Jacob Westman

This repo contains code to extract information from access-to-market. It's crepe cause everyone loves pancakes.

## Intall
Download the repo or clone using:
```
git clone https://github.com/cobzky/customs_crepe
```
and make sure that all dependencies are installed via

```
pip install -r requirements.txt
```

## Use

The main functionality can be accessed via the `crepe_cli.py` module. In order to set it
in interactive configuration mode use `-i` option when calling from command line, as:
```
python crepe_cli.py -i
```

Otherwise you can also point to a correctly configures input file via the `-f` tack, and
specify and output file with `-o`. For example:

```
python crepe_cli.py -f test_input.csv -o test_ouput.csv
```

## Licence
MIT
