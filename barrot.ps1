$ErrorActionPreference='Stop'
Set-Location "$HOME\ns_site"
Get-Content vercel.json -Raw | ConvertFrom-Json | Out-Null
$u = (vercel deploy --prod | Select-String 'https://.*\.vercel\.app' | Select-Object -Last 1).Matches.Value
"`nLIVE:   $u"
"PORTAL: $u/portal"
"PRICE:  $u/pricing.html"
