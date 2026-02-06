# DYNAMIC Fire risk indicator implementation

This repository contains a _simplified version_ of the implementation of the DYNAMIC fire risk indicator
described in the research paper:

>R.D. Strand and L.M. Kristensen: An implementation, evaluation and validation of a dynamic fire and conflagration risk indicator for wooden homes. In volume 238 of Procedia Computer Science, pp. 49-56, 2024. Proceedings of the 15th International Conference on Ambient Systems, Networks and Technologies Networks (ANT). Online: https://www.sciencedirect.com/science/article/pii/S187705092401233X

Compared to the [original repository](https://github.com/webminz/dynamic-frcm) and the associated [PyPI package](https://pypi.org/project/dynamic-frcm/), this repository only contains the **fire risk calculation** itself without the hard-wired integration with the https://met.no integration and the more complex API.

The calculation takes a CSV datasetas input containing time, temperature, relative humidity and wind speed data points, and 
provides the resulting fire risk as _time to flashover (ttf)_.

# Installation

The project is based on using [uv](https://docs.astral.sh/uv/) as the package manager. 

Make sure that you have [uv installed](https://docs.astral.sh/uv/getting-started/installation/).

You can test the library by running

```shell
uv run python src/frcm/__main__.py ./bergen_2026_01_09.csv
```

where `./bergen_2026_01_09.csv` is an example CSV file demonstrating the input format which comes bundled with this repository.


This should provide the following output:

```
Computing FireRisk for given data in 'dynamic-frcm-simple/bergen_2026_01_09.csv' (132 datapoints)

timestamp,ttf
2026-01-07T00:00:00+00:00,6.072481167177002
2026-01-07T01:00:00+00:00,5.7243022443357905
2026-01-07T02:00:00+00:00,5.511503568040109
2026-01-07T03:00:00+00:00,5.3486591429746895
2026-01-07T04:00:00+00:00,5.220546121174422
2026-01-07T05:00:00+00:00,5.122507965859784
2026-01-07T06:00:00+00:00,5.043379927801035
2026-01-07T07:00:00+00:00,4.97841119689852
2026-01-07T08:00:00+00:00,4.9228585219502525
2026-01-07T09:00:00+00:00,4.873359414165299
2026-01-07T10:00:00+00:00,4.836470479216353
...
```

You can also build the project as a package with:

```shell
uv build
```

which will create the package _wheel_ (file ending `.whl`) in the `dist/` directory.
This package can ordinarily be installed with `pip install` and integrated into existing Python applications 
or it can be run standalone using `python -m`.


# Overview

The implementation is organised into the following main folders:

- `datamodel` - contains an implementation of the data model used for weather data and fire risk indications.
- `fireriskmodel` contains an implementation of the underlying fire risk model.

The central method of the application is the method `compute()` in `fireriskmodel.compute`.

