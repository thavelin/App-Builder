# Clear all Next.js and TypeScript caches
Write-Host "Clearing all caches..."

if (Test-Path .next) {
    Remove-Item -Recurse -Force .next
    Write-Host "✓ Cleared .next directory"
}

if (Test-Path node_modules\.cache) {
    Remove-Item -Recurse -Force node_modules\.cache
    Write-Host "✓ Cleared node_modules cache"
}

Get-ChildItem -Recurse -Filter "*.tsbuildinfo" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "✓ Cleared TypeScript build info"

Write-Host "`nAll caches cleared! Please restart the dev server with: npm run dev"

