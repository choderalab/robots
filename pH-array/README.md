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

citric acid:        5515.207 uL ['0.1M Citric Acid' in 'Trough 100ml']
sodium phosphate:  42484.793 uL ['0.1M Sodium Phosphate' in 'Trough 100ml']

WASTE PROFILE

citric acid:         192.000 uL (   3.689 mg)
sodium phosphate:    192.000 uL (   2.726 mg)

```
See `citric-phosphate-bindingassay.txt` for plate layout:
```
#
# plate 1
#
7.6 6.35 93.65
7.6 6.35 93.65
7.6 6.35 93.65
7.6 6.35 93.65
7.4 9.15 90.85
7.4 9.15 90.85
7.4 9.15 90.85
7.4 9.15 90.85
#
# plate 2
#
7.2 13.05 86.95
7.2 13.05 86.95
7.2 13.05 86.95
7.2 13.05 86.95
7.0 17.65 82.35
7.0 17.65 82.35
7.0 17.65 82.35
7.0 17.65 82.35
#
# plate 3
#
6.8 22.75 77.25
6.8 22.75 77.25
6.8 22.75 77.25
6.8 22.75 77.25
6.6 27.25 72.75
6.6 27.25 72.75
6.6 27.25 72.75
6.6 27.25 72.75
#
# plate 4
#
6.4 30.75 69.25
6.4 30.75 69.25
6.4 30.75 69.25
6.4 30.75 69.25
6.2 33.90 66.10
6.2 33.90 66.10
6.2 33.90 66.10
6.2 33.90 66.10
```
