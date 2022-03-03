#!/bin/bash
set -e


VERSIONS=('2.7' '3.4' '3.5' '3.6' '3.7' '3.8')


function runFlake8() {
    echo '<--------------------------------------------->'
    # run flake8 and exit on error
    # it will check the code base against coding style (PEP8) and programming errors
    echo "Running flake8..."
    flake8 || { echo 'You increased the number of flak8 errors'; exit 1; }
}

function runPyTest() {
    echo '<--------------------------------------------->'
    python_version=${1}
    test_venv="venv_test_${python_version//.}"

    echo "Creating virtualenv ${test_venv}..."
    virtualenv -p python${python_version} ${test_venv}

    echo "Activating virtualenv ${test_venv}..."

    if [ -f ${test_venv}/bin/activate ]; then
        source ${test_venv}/bin/activate
    fi

    if [ -f ${test_venv}/Scripts/activate ]; then
        source ${test_venv}/Scripts/activate
    fi

    echo 'Installing dependencies...'
    pip install -r requirements.txt

    runFlake8

    echo 'Running pytest...'
    py.test

    echo "Deactivating virtualenv..."
    deactivate
}

echo 'Removing all existing virtualenv'
rm -rf venv_test_* | true

for i in "${VERSIONS[@]}"
do
    runPyTest ${i}
done

echo 'Done'
