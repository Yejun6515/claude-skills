# Claude Code task-complete notification (sound + toast)
# Lives in the claude-skills GitHub repo so it travels across all PCs.
# Called from each machine's ~/.claude/settings.json Stop hook.
# ASCII-only to avoid Windows PowerShell 5.1 codepage issues.

# 1) Play sound synchronously so it is heard before PowerShell exits
try {
    $sound = New-Object System.Media.SoundPlayer "$env:WINDIR\Media\Windows Notify System Generic.wav"
    $sound.PlaySync()
} catch {
    try { [System.Media.SystemSounds]::Asterisk.Play(); Start-Sleep -Milliseconds 700 } catch {}
}

# 2) Windows toast notification
try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $texts = $template.GetElementsByTagName("text")
    $texts.Item(0).AppendChild($template.CreateTextNode("Claude Code")) | Out-Null
    $texts.Item(1).AppendChild($template.CreateTextNode("Task complete")) | Out-Null

    $toast = New-Object Windows.UI.Notifications.ToastNotification $template
    $appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast)
} catch {
    # If toast is unavailable, the sound alone is enough
}
