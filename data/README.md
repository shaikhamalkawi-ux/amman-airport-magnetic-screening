# Central analysis input

`analysis_input.csv` is included. `python code/prepare_analysis_input.py` maps the hash-locked `endpoint_extension/Source_Reconstructed_Master_44.csv` into the earlier central script's schema without rounding or changing numerical values.

`Block` copies `StationNumber`; `Distance_m` copies `Distance_numeric_m`; `Fine_LF` and `Coarse_LF` copy the reconstructed LF fields. Other selected columns keep their names. LF units are 10^-8 m^3 kg^-1, FD is percent, distance is metres, and chemistry is mg kg^-1. The master has 44 rows; the code uses the common 43-row paired cohort, excluding sample 24 with missing coarse readings.

See [DATA_DICTIONARY.md](../docs/DATA_DICTIONARY.md) for source cells, all 31 master columns and mass rules. The adapter is new release code, not the historical master generator.
