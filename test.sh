#!/bin/sh

# Write down the current git version just for future reference.
mkdir -p .coverage-results
git log | head -1 > .coverage-results/version-stamp.txt

# This script depends on trialcoverage >= 0.3.5 and on coverage.py >= 3.3.2a1z8.
# The following lines will print an ugly warning message if those two are not
# installed.
python -c 'import pkg_resources;pkg_resources.require("trialcoverage>=0.3.5")' &&
python -c 'import pkg_resources;pkg_resources.require("coverage>=3.3.2a1z8")' &&

python -tt setup.py flakes
RETVAL=$?
if [ ${RETVAL} != 0 ] ; then
    echo "FAILED: pyflakes reported warnings -- exiting"
    exit ${RETVAL}
fi

# Now run the tests once just to make sure all test_requires dependencies are 
# installed before we start paying attention to code coverage.

python setup.py trial > /dev/null 2> /dev/null

python -tt setup.py trial --reporter=bwverbose-coverage --rterrors
RETVAL=$?
echo "To see coverage details run 'coverage report' or open htmlcov/index.html."
coverage html
if [ ${RETVAL} = 0 ]; then
  echo SUCCESS
fi
exit $RETVAL
