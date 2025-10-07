Param()
try {
  if (Get-Command pip-compile -ErrorAction SilentlyContinue) {
    pip-compile --output-file=requirements.lock requirements.txt
  }
  else {
    Write-Host "pip-compile not found; falling back to pip freeze (ensure your venv has desired versions)"
    pip freeze > requirements.lock
  }
} catch {
  Write-Error $_
  exit 1
}
