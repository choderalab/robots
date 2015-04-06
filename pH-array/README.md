# Python scripts for creating arrays of buffers at various pH values with citric acid / phosphate buffers.

## Original files:
* `create-pH-worklist.py` - original experiment to measure compound fluorescence as a function of pH
* `citric-phosphate.txt` - complete range of recipes for available pH
* `ph-worklist.gwl` - example output worklist

## pH dependent binding affinity assay
* `create-pH-worklist-bindingassay.py` - modified experiment to measure binding affinity as a function of pH in 96-well format, stages to deepwell plates
* `citric-phosphate-bindingassay.txt` - complete range of recipes for available pH for plate setup for `create-pH-worklist-bindingassay.py`
* `ph-worklist-bindingassay.gwl` - example output worklist

Output of Python script:
```
BUFFER CONSUMPTION

citric acid:        9798.466 uL ['0.1M Citric Acid' in '100 mL Trough']
sodium phosphate:  38201.534 uL ['0.1M Sodium Phosphate' in '100 mL Trough']

WASTE PROFILE

citric acid:         192.000 uL (   3.689 mg)
sodium phosphate:    192.000 uL (   2.726 mg)
```
See `citric-phosphate-bindingassay.txt` for plate layout:
```
# plate 1
#
7.6 6.35 93.65 (row A)
7.6 6.35 93.65 (row B)
7.4 9.15 90.85 (row C)
7.4 9.15 90.85 (...)
7.2 13.05 86.95
7.2 13.05 86.95
7.0 17.65 82.35
7.0 17.65 82.35
#
# plate 2
#
6.8 22.75 77.25 (row A)
6.8 22.75 77.25 ...
6.6 27.25 72.75
6.6 27.25 72.75
6.4 30.75 69.25
6.4 30.75 69.25
6.2 33.90 66.10
6.2 33.90 66.10
#
# plate 3
#
6.0 36.85 63.15
6.0 36.85 63.15
5.8 39.55 60.45
5.8 39.55 60.45
5.6 42.00 58.00
5.6 42.00 58.00
5.4 44.25 55.75
5.4 44.25 55.75
#
# plate 4
#
5.2 46.40 53.60
5.2 46.40 53.60
5.0 48.50 51.50
5.0 48.50 51.50
4.8 50.70 49.30
4.8 50.70 49.30
4.6 53.25 46.75
4.6 53.25 46.75
```
