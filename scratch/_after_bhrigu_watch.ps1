# Poll VPS until Bhrigu complete, restart engine, wake screen, flag for P0 work.
$Vps = "root@46.28.44.225"
function Wake-Screen {
    try { & (Join-Path $PSScriptRoot "wake_screen.ps1") } catch {}
    [Console]::Beep(880, 200)
    [Console]::Beep(1100, 300)
    # Toggle scroll lock � often wakes display without admin
    $ws = New-Object -ComObject WScript.Shell
    $ws.SendKeys("{SCROLLLOCK}{SCROLLLOCK}")
}
$Flag = Join-Path $PSScriptRoot "BHIGRU_DONE_CONTINUE_B.flag"
$Log = Join-Path $PSScriptRoot "after_bhrigu_watch.log"

function Log($msg) {
    $line = "$(Get-Date -Format o) $msg"
    Add-Content -Path $Log -Value $line
    Write-Host $line
}

Log "Watching Bhrigu on $Vps (screen wake on complete only) ..."
while ($true) {
    $line = ssh -o BatchMode=yes -o ConnectTimeout=15 $Vps "cd /opt/astro && ./venv/bin/python scratch/_book_progress.py 2>/dev/null | grep Bhrigu_Samhita"
    Log $line
    if ($line -match "219/219" -and $line -match "complete=True") {
        Log "Bhrigu complete � restarting astro-engine"
        ssh -o BatchMode=yes $Vps "pm2 restart astro-engine && ./venv/bin/python scratch/_corpus_stats_once.py 2>/dev/null | tail -1"
        "Bhrigu extraction complete. Continue: lagna filter + fusion (option B)." | Set-Content -Path $Flag -Encoding utf8
        Wake-Screen
        # Windows toast
        try {
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $xml.GetElementsByTagName("text").Item(0).AppendChild($xml.CreateTextNode("Astro")) | Out-Null
            $xml.GetElementsByTagName("text").Item(1).AppendChild($xml.CreateTextNode("Bhrigu done. Engine restarted. Continue option B.")) | Out-Null
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Astro").Show([Windows.UI.Notifications.ToastNotification]::new($xml))
        } catch { Log "Toast skipped: $_" }
        Log "Done. Flag: $Flag"
        break
    }
    Start-Sleep -Seconds 300
}
