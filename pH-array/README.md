# Python scripts for creating arrays of buffers at various pH values with citric acid / phosphate buffers.

* `create-pH-worklist.py` - original experiment to measure compound fluorescence as a function of pH
* `create-pH-worklist-bindingassay.py` - modified experiment to measure binding affinity as a function of pH in 96-well format, stages to deepwell plates
* `create-pH-worklist-1mL.py` - modified experiment to create pH array, stages to deepwell plates
* `citric-phosphate.txt` - complete range of recipes for available pH
* `citric-phosphate-8.txt` - limited range of 8 conditions
* `ph-worklist.gwl` - example output worklist

## Binding affinity assay notes

Use `create-pH-worklist-bindingassay.py`.

Output:
```
BUFFER CONSUMPTION

citric acid:        9798.466 uL ['0.1M Citric Acid' in '100 mL Trough']
sodium phosphate:  38201.534 uL ['0.1M Sodium Phosphate' in '100 mL Trough']

WASTE PROFILE

citric acid:         192.000 uL (   3.689 mg)
sodium phosphate:    192.000 uL (   2.726 mg)
```

