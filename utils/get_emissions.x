#! /bin/bash
for am in 1.0 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.0 2.5 3.0; do
    ./skycalc.py -q -a $am MKO_emission.dark.AM${am}.fits
done
for am in 1.0 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.0 2.5 3.0; do
    ./skycalc.py -q -m -p 66.4 -a $am MKO_emission.grey.AM${am}.fits
done
for am in 1.0 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.0 2.5 3.0; do
    ./skycalc.py -q -m -p 101.5 -a $am MKO_emission.bright.AM${am}.fits
done

