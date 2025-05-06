# Troubleshooting

This page covers common issues and their solutions when using Gaphor.

---

## Invisible UI on Windows 10 (Intel + NVIDIA Graphics)

**Problem:**

Some Windows 10 users with Intel integrated graphics (especially older GPUs like the Intel HD 4000 / 4600 series) — often in systems that also have NVIDIA GPUs — may experience an **invisible UI** when launching Gaphor. The window appears, and UI elements are clickable (buttons, menus), but nothing is visible.

This issue is tracked upstream in GTK:
👉 [GNOME/gtk#7283](https://gitlab.gnome.org/GNOME/gtk/-/issues/7283)

### Example:

*In the images below, the Gaphor window is open but the UI is not visible.*

![Invisible UI Example 1](./images/invisible-ui-example1.png)

![Invisible UI Example 2](./images/invisible-ui-example2.png)

---

## Solution: Set the `GSK_RENDERER=gl` Environment Variable

To fix this issue, you can force GTK to use the OpenGL-based renderer by setting the environment variable `GSK_RENDERER=gl`.

### Option 1️⃣: Update the Gaphor Shortcut

1. **Right-click the Gaphor shortcut** (Desktop or Start Menu) and select **Properties**.
2. In the **Shortcut** tab, locate the **Target** field.
3. Replace the existing target with the following PowerShell command:

   ```powershell
   powershell -Command "$env:GSK_RENDERER='gl'; Start-Process 'C:\Program Files\Gaphor\gaphor.exe'"
   ```

   *Note: Adjust the path if your Gaphor installation is in a different folder.*

4. Click **Apply** and then **OK**.

✅ Now, whenever you launch Gaphor via this shortcut, it will apply the fix automatically.

---

### Option 2️⃣: Set a Permanent Environment Variable

1. Press `Win + S` and search for **Environment Variables**.
2. Select **“Edit the system environment variables” → Environment Variables**.
3. Under **User variables**, click **New**:
   - **Variable name:** `GSK_RENDERER`
   - **Variable value:** `gl`
4. Save and restart your computer.

✅ This will apply the fix globally for Gaphor (and any other GTK-based apps).

---

## Affected Systems

- **Windows 10**
- Intel HD 4000 / 4600 series graphics (or similar)
- Often combined with NVIDIA GPU setups

---

*Thanks to the Gaphor community and contributors for identifying and confirming this workaround!*
