# Script de demonstration - Teleconsultation API
# A executer avec le serveur deja lance (python run.py) dans un autre terminal
# Usage : .\demo.ps1

$base = "http://localhost:5000"

Write-Host "`n=== 1. Healthcheck ===" -ForegroundColor Cyan
Invoke-WebRequest "$base/health" | Select-Object StatusCode, Content

Write-Host "`n=== 2. Inscription medecin ===" -ForegroundColor Cyan
$doctor = Invoke-RestMethod -Uri "$base/api/v1/auth/register" -Method Post -ContentType "application/json" `
    -Body '{"email":"demo.doc@ex.com","password":"secret123","role":"doctor","name":"Dr Demo","specialty":"Generaliste"}'
$doctor

Write-Host "`n=== 3. Inscription patient ===" -ForegroundColor Cyan
$patient = Invoke-RestMethod -Uri "$base/api/v1/auth/register" -Method Post -ContentType "application/json" `
    -Body '{"email":"demo.pat@ex.com","password":"secret123","role":"patient","name":"Patient Demo"}'
$patient

Write-Host "`n=== 4. Connexion medecin ===" -ForegroundColor Cyan
$docLogin = Invoke-RestMethod -Uri "$base/api/v1/auth/login" -Method Post -ContentType "application/json" `
    -Body '{"email":"demo.doc@ex.com","password":"secret123"}'
$docToken = $docLogin.access_token
Write-Host "Token medecin recupere."

Write-Host "`n=== 5. Connexion patient ===" -ForegroundColor Cyan
$patLogin = Invoke-RestMethod -Uri "$base/api/v1/auth/login" -Method Post -ContentType "application/json" `
    -Body '{"email":"demo.pat@ex.com","password":"secret123"}'
$patToken = $patLogin.access_token
Write-Host "Token patient recupere."

Write-Host "`n=== 6. Le medecin cree un creneau ===" -ForegroundColor Cyan
$slot = Invoke-RestMethod -Uri "$base/api/v1/slots/" -Method Post -ContentType "application/json" `
    -Headers @{Authorization = "Bearer $docToken" } `
    -Body '{"start_time":"2026-11-05T09:00:00","end_time":"2026-11-05T09:30:00"}'
$slot

Write-Host "`n=== 7. Le patient reserve ce creneau ===" -ForegroundColor Cyan
$appt = Invoke-RestMethod -Uri "$base/api/v1/appointments/" -Method Post -ContentType "application/json" `
    -Headers @{Authorization = "Bearer $patToken" } `
    -Body (@{slot_id = $slot.id; reason = "consultation demo" } | ConvertTo-Json)
$appt

Write-Host "`n=== 8. Le patient consulte ses rendez-vous ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "$base/api/v1/appointments/" -Headers @{Authorization = "Bearer $patToken" }

Write-Host "`n=== 9. Le medecin consulte SES rendez-vous (avec infos patient) ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "$base/api/v1/appointments/" -Headers @{Authorization = "Bearer $docToken" }

Write-Host "`n=== 10. Regle metier : double reservation refusee (409 attendu) ===" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$base/api/v1/appointments/" -Method Post -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $patToken" } -Body (@{slot_id = $slot.id } | ConvertTo-Json)
}
catch {
    Write-Host "-> Refuse comme attendu : $($_.Exception.Response.StatusCode)" -ForegroundColor Green
}

Write-Host "`n=== 11. Controle de role : un patient ne peut pas creer de creneau (403 attendu) ===" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$base/api/v1/slots/" -Method Post -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $patToken" } `
        -Body '{"start_time":"2026-11-05T10:00:00","end_time":"2026-11-05T10:30:00"}'
}
catch {
    Write-Host "-> Refuse comme attendu : $($_.Exception.Response.StatusCode)" -ForegroundColor Green
}

Write-Host "`n=== 12. Sans jeton du tout (401 attendu) ===" -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$base/api/v1/appointments/" -Method Post -ContentType "application/json" `
        -Body (@{slot_id = $slot.id } | ConvertTo-Json)
}
catch {
    Write-Host "-> Refuse comme attendu : $($_.Exception.Response.StatusCode)" -ForegroundColor Green
}

Write-Host "`n=== Demo terminee ===" -ForegroundColor Cyan
