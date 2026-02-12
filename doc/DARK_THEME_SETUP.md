# Dark Theme Configuration for d3kOS

**Date:** 2026-02-09
**System:** Debian Trixie (Raspberry Pi 4B)
**Desktop:** Raspberry Pi Desktop (LXDE/Openbox)

---

## ✅ Configurations Applied

### 1. GTK3 Applications (Modern Apps)
**File:** `~/.config/gtk-3.0/settings.ini`

**Theme:** Adwaita-dark
**Features:**
- Dark window decorations
- Dark menus and dialogs
- Dark file browsers
- Forced dark mode preference

### 2. GTK2 Applications (Legacy Apps)
**File:** `~/.gtkrc-2.0`

**Theme:** Adwaita-dark
**Features:**
- Consistent dark theme for older applications
- Matches GTK3 appearance

### 3. Window Manager (Openbox)
**File:** `~/.config/openbox/rc.xml`

**Theme:** Onyx
**Features:**
- Dark window borders and title bars
- Dark right-click menu
- Dark system decorations

### 4. Desktop Background
**File:** `~/.config/pcmanfm/LXDE-pi/desktop-items-0.conf`

**Colors:**
- Background: Pure black (#000000)
- Foreground: White (#FFFFFF)
- Shadow: Black (#000000)

### 5. Terminal (LXTerminal)
**File:** `~/.config/lxterminal/lxterminal.conf`

**Colors:**
- Background: Black (rgb(0,0,0))
- Foreground: White (rgb(255,255,255))
- Green accent: rgb(0,204,0)
- Custom color palette for syntax highlighting

### 6. Web Browser (Chromium)
**File:** `~/.config/chromium/Default/Preferences`

**Features:**
- Dark mode enabled
- Force dark mode on websites
- Black new tab page
- System theme integration

---

## 🔄 Applying the Changes

### Option A: Restart Desktop Session (Recommended)
1. Connect to the Pi's display (HDMI monitor or VNC)
2. Log out and log back in
3. All dark themes will be active

### Option B: Reload Components
```bash
# Reload Openbox window manager
openbox --reconfigure

# Restart desktop file manager
pcmanfm --desktop --profile LXDE-pi &

# Close and reopen any applications
```

### Option C: Reboot Pi
```bash
sudo reboot
```

---

## 🖥️ Accessing the Desktop

### Via HDMI Monitor
1. Connect HDMI cable from Pi to monitor
2. Connect USB keyboard and mouse
3. Desktop should display automatically
4. Dark theme will be active

### Via VNC (Remote Desktop)
**Install VNC Server (if not installed):**
```bash
sudo apt-get update
sudo apt-get install -y realvnc-vnc-server realvnc-vnc-viewer
sudo systemctl enable vncserver-x11-serviced
sudo systemctl start vncserver-x11-serviced
```

**Configure VNC:**
```bash
sudo raspi-config
# Navigate to: Interface Options > VNC > Enable
```

**Connect from Ubuntu:**
1. Install VNC Viewer: `sudo apt-get install remmina`
2. Open Remmina
3. Create new VNC connection to: `192.168.1.237:5900`
4. Login with d3kos credentials

### Via Web VNC (No Client Needed)
**Install noVNC:**
```bash
sudo apt-get install -y novnc websockify
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &
```

**Access:** http://192.168.1.237:6080/vnc.html

---

## 🎨 Color Scheme

### Desktop Theme Colors
| Element | Color | Hex |
|---------|-------|-----|
| Background | Black | #000000 |
| Foreground | White | #FFFFFF |
| Accent | Green | #00CC00 |
| Window borders | Dark gray | #2E2E2E |
| Menu background | Dark gray | #222222 |

### Terminal Colors
| Color | Normal | Bright |
|-------|--------|--------|
| Black | rgb(0,0,0) | rgb(127,127,127) |
| Red | rgb(205,0,0) | rgb(255,0,0) |
| Green | rgb(0,204,0) | rgb(0,255,0) |
| Yellow | rgb(205,205,0) | rgb(255,255,0) |
| Blue | rgb(0,0,238) | rgb(92,92,255) |
| Magenta | rgb(205,0,205) | rgb(255,0,255) |
| Cyan | rgb(0,205,205) | rgb(0,255,255) |
| White | rgb(229,229,229) | rgb(255,255,255) |

---

## 🌐 Web Browser Dark Mode

### Chromium Configuration
**Features:**
- Automatic dark mode for websites
- Black new tab page
- Dark developer tools
- Dark settings pages

**Manual Override:**
- Settings → Appearance → Theme → Dark
- Flags: chrome://flags/#enable-force-dark

### Firefox (If Installed)
**Configure:**
1. Open Firefox
2. Settings → General → Theme
3. Select "Dark" theme
4. Enable: `ui.systemUsesDarkTheme` = 1 in `about:config`

---

## 🔍 Verification

### Check GTK Theme
```bash
gsettings get org.gnome.desktop.interface gtk-theme
# Should output: 'Adwaita-dark'
```

### Check Desktop Background
```bash
cat ~/.config/pcmanfm/LXDE-pi/desktop-items-0.conf | grep desktop_bg
# Should output: desktop_bg=#000000
```

### Check Terminal Theme
```bash
cat ~/.config/lxterminal/lxterminal.conf | grep bgcolor
# Should output: bgcolor=rgb(0,0,0)
```

---

## 🛠️ Troubleshooting

### Issue: Theme Not Applied
**Solution:**
```bash
# Reload GTK settings
gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'

# Restart LXDE panel
lxpanelctl restart
```

### Issue: Desktop Background Still Light
**Solution:**
```bash
# Manually set background
pcmanfm --set-wallpaper-color='#000000'

# Or restart file manager
pkill pcmanfm
pcmanfm --desktop --profile LXDE-pi &
```

### Issue: Terminal Still Light
**Solution:**
1. Close all terminal windows
2. Reopen LXTerminal
3. Check: Edit → Preferences → Colors → "Custom" selected

### Issue: Browser Not Dark
**Solution:**
```bash
# Clear Chromium cache
rm -rf ~/.cache/chromium/*
rm -rf ~/.config/chromium/Default/Cache/*

# Restart Chromium
pkill chromium
chromium-browser --force-dark-mode &
```

---

## 📦 Available Dark Themes

If you want to try different themes:

### GTK Themes
```bash
ls /usr/share/themes/ | grep -i dark
```
- Adwaita-dark (current)
- Nightmare
- Nightmare-01, 02, 03

### Openbox Themes
```bash
ls /usr/share/themes/ | grep -iE 'onyx|dark'
```
- Onyx (current)
- Onyx-Citrus
- Nightmare variants

### Change Theme
**GTK:**
```bash
echo 'gtk-theme-name=Nightmare' >> ~/.config/gtk-3.0/settings.ini
```

**Openbox:**
```bash
sed -i 's|<name>Onyx</name>|<name>Nightmare</name>|' ~/.config/openbox/rc.xml
openbox --reconfigure
```

---

## 🎯 Next Steps

1. **Connect to Desktop:**
   - Via HDMI monitor, or
   - Install and configure VNC server

2. **Verify Theme:**
   - Log out and log back in
   - Check all applications use dark theme
   - Test web browser dark mode

3. **Customize (Optional):**
   - Try different dark themes
   - Adjust terminal colors
   - Configure desktop icons

---

## 📝 Files Modified

1. `~/.config/gtk-3.0/settings.ini` - GTK3 theme
2. `~/.gtkrc-2.0` - GTK2 theme
3. `~/.config/openbox/rc.xml` - Window manager theme
4. `~/.config/pcmanfm/LXDE-pi/desktop-items-0.conf` - Desktop background
5. `~/.config/lxterminal/lxterminal.conf` - Terminal colors
6. `~/.config/chromium/Default/Preferences` - Browser dark mode

**Backup Command:**
```bash
tar -czf ~/d3kos-theme-backup-$(date +%Y%m%d).tar.gz \
  ~/.config/gtk-3.0/ \
  ~/.gtkrc-2.0 \
  ~/.config/openbox/ \
  ~/.config/pcmanfm/ \
  ~/.config/lxterminal/ \
  ~/.config/chromium/Default/Preferences
```

---

**Dark theme setup completed:** 2026-02-09
**Status:** Ready to activate (logout/login required)
