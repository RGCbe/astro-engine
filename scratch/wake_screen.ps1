# Wake display + optional toast (run locally on Windows)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class ScreenWake {
  [DllImport("user32.dll")]
  public static extern int SendMessage(IntPtr hWnd, int Msg, IntPtr wParam, IntPtr lParam);
  [DllImport("user32.dll")]
  public static extern void mouse_event(int dwFlags, int dx, int dy, int cButtons, int dwExtraInfo);
}
"@
# SC_MONITORPOWER / monitor on
[void][ScreenWake]::SendMessage([IntPtr](-1), 0x0112, [IntPtr]0xF170, [IntPtr]2)
[ScreenWake]::mouse_event(0x0001, 2, 2, 0, 0)
[System.Threading.Thread]::Sleep(100)
[ScreenWake]::mouse_event(0x0001, 0, 0, 0, 0)
Write-Host "Screen wake sent at $(Get-Date -Format o)"
