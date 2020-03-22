@echo off
CALL activate configEnv

call :TESTS
IF "%errorlevel%"=="0" CALL :DEPLOY %1

CALL conda deactivate
PAUSE > nul
GOTO :EOF


:TESTS
SET PYTHONPATH=%cd%
cd tests
SET pass=123456
python -m pytest
SET test_result=%errorlevel%
cd ..
EXIT /B %test_result%

:DEPLOY
set env=%1

IF "%env%"=="" set /p env=(Test/Production)?
IF /I "%env%"=="Test" call :DEPLOY_TEST_PYPI
IF /I "%env%"=="Production" call :DEPLOY_PYPI
GOTO :EOF


:DEPLOY_PYPI
SET Test=False
python -m pip install --user --upgrade twine
python setup.py sdist bdist_wheel && python -m twine upload --skip-existing -u __token__ -p %pypi_token% dist/*
GOTO :EOF

:DEPLOY_TEST_PYPI
SET Test=True
python -m pip install --user --upgrade twine
python setup.py sdist bdist_wheel && python -m twine upload --repository-url https://test.pypi.org/legacy/ --skip-existing -u __token__ -p %pypi_test_token% dist/*
GOTO :EOF
