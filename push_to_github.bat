@echo off
echo ======================================================
echo PUSHING TO GITHUB...
echo ======================================================
echo.
echo If a popup appears, please sign in.
echo If asked for a password in this window, type your GitHub Token.
echo.

git push -u origin main

echo.
if %errorlevel% neq 0 (
    echo ======================================================
    echo ERROR: Push Failed!
    echo ======================================================
    echo check the error message above.
) else (
    echo ======================================================
    echo SUCCESS: Code pushed to GitHub!
    echo ======================================================
)
echo.
pause
