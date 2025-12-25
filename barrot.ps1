$ErrorActionPreference='Stop'

# Import SHRM Version 2 Configuration
$configPath = "config/shrm_v2.yaml"
if (Test-Path $configPath) {
    Write-Host "Loading SHRM v2 configuration from $configPath"
    $configContent = Get-Content $configPath | Out-String
    # Assuming there is some logic to use the content of the config file
    # This demonstration just announces the content being loaded
    # Example Integration
    $ConfigData = ConvertFrom-Yaml -Yaml ($configContent)
    Write-Host "SHRM v2 Config Loaded: " $ConfigData
} else {
    Write-Warning "SHRM v2 configuration file not found at $configPath - continuing without it"
}

# Deploy to Vercel if in the correct directory
if (Test-Path "$HOME\ns_site") {
    Set-Location "$HOME\ns_site"
    Get-Content vercel.json -Raw | ConvertFrom-Json | Out-Null
    $u = (vercel deploy --prod | Select-String 'https://.*\.vercel\.app' | Select-Object -Last 1).Matches.Value
    "`nLIVE:   $u"
    "PORTAL: $u/portal"
    "PRICE:  $u/pricing.html"
} else {
    Write-Host "Vercel deployment directory not found - skipping deployment"
}
