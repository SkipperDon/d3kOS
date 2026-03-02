# Network Performance Investigation & Recommendations
**Date:** 2026-03-02
**Issue:** TrueNAS ping latency is 88ms (should be <5ms)

---

## 🚨 Problem Identified

**Current Performance:**
- Laptop → Workstation: **6ms** ✅ (Good)
- Laptop → TrueNAS: **88ms** ❌ (VERY BAD for local network)

**Expected Performance:**
- 10 Gig Ethernet: <2ms
- 1 Gig Ethernet: <5ms
- WiFi (same building): 10-30ms
- **88ms is 18-44× slower than expected!**

---

## 🔍 Investigation Steps

### Step 1: Check Laptop Connection Type

**From laptop (WSL Ubuntu), run:**
```bash
ip addr show
```

**Look for:**
- `eth0` = Wired connection ✅
- `wlan0` = WiFi connection ⚠️

**If WiFi:** That could explain high latency to TrueNAS

---

### Step 2: Check TrueNAS Network Configuration

**In TrueNAS Web UI (you're logged in now):**

1. Navigate to: **Network → Interfaces**
2. Check which interface is active
3. Look for:
   - Speed: Should show **10000 Mbps** (10 Gig) or **1000 Mbps** (1 Gig)
   - Status: Should be **ACTIVE**
   - MTU: Should be **1500** or **9000** (jumbo frames)

**Screenshot or note:**
- Interface name: (e.g., igb0, em0, etc.)
- Speed: _____ Mbps
- Duplex: Full or Half?
- MTU: _____

---

### Step 3: Check Physical Connections

**TrueNAS:**
- Which switch is it connected to?
  - [ ] 1 Gig switch
  - [ ] QNAP 10 Gig switch
- Which port on TrueNAS?
  - [ ] Built-in network port
  - [ ] PCIe 10 Gig network card

**Workstation:**
- Which switch is it connected to?
  - [ ] 1 Gig switch
  - [ ] QNAP 10 Gig switch
- Network card type?
  - [ ] Built-in 1 Gig
  - [ ] Built-in 2.5 Gig
  - [ ] PCIe 10 Gig card

---

### Step 4: Test Direct Path (Bypass Routing)

**From laptop, test both systems:**

```bash
# Test workstation (6ms - good baseline)
ping -c 10 192.168.1.39

# Test TrueNAS (88ms - problem)
ping -c 10 192.168.1.102

# Check route to TrueNAS
traceroute 192.168.1.102
```

**If traceroute shows multiple hops:**
- Traffic is being routed incorrectly
- Should be 1 hop only (direct)

---

### Step 5: Test TrueNAS Network from TrueNAS

**In TrueNAS Web UI:**

1. **Shell** (top right corner)
2. Run diagnostic commands:

```bash
# Check network interface status
ifconfig

# Check if 10 Gig link is active
ifconfig | grep -A 5 "flags=.*UP"

# Ping laptop back (reverse direction)
ping -c 10 192.168.1.XXX  # Replace with laptop IP

# Check routing table
netstat -rn

# Check link speed
dmesg | grep -i "link speed\|ethernet"
```

---

## 💡 Recommendations

### Immediate Recommendations (BEFORE Ollama Deployment)

**Option 1: Fix Network First (RECOMMENDED)**
- Investigate 88ms latency issue
- Fix network performance
- **THEN** deploy Ollama
- **Benefit:** Ollama will be fast and responsive

**Option 2: Deploy Despite Network Issue**
- Deploy Ollama to TrueNAS now
- Accept slower performance (88ms + inference time)
- Fix network later
- **Drawback:** Every Ollama call will have 176ms overhead

---

### Long-Term Network Improvements

**Priority 1: Optimize TrueNAS Connection (HIGH IMPACT)**

**If TrueNAS has 10 Gig port:**
1. ✅ Connect TrueNAS to QNAP 10 Gig switch (if not already)
2. ✅ Use Cat6a or Cat7 cable (supports 10 Gig)
3. ✅ Verify 10 Gig link negotiation in TrueNAS
4. ✅ Expected result: Ping drops to <2ms

**If TrueNAS only has 1 Gig port:**
1. ✅ Connect to QNAP 2.5 Gig port (if available)
2. ✅ Or connect to 1 Gig switch with quality cable
3. ✅ Expected result: Ping drops to <5ms

---

**Priority 2: Optimize Workstation Connection (MEDIUM IMPACT)**

**If workstation has 10 Gig capability:**
1. ✅ Verify connected to QNAP 10 Gig switch
2. ✅ Check if RTX 3060 Ti system has 10 Gig NIC
3. ✅ Current 6ms is already good, could drop to <1ms with 10 Gig

**Estimated improvement:**
- Workstation: 6ms → <1ms (minor improvement)
- TrueNAS: **88ms → <2ms (44× faster!)**

---

**Priority 3: Laptop Connection (LOW IMPACT)**

**If laptop on WiFi:**
- Consider wired connection for development work
- Reduces latency from 20-50ms to <5ms
- More stable for large Ollama API calls

**If laptop already wired:**
- Current 6ms to workstation is good
- No changes needed

---

**Priority 4: Network Segregation (OPTIONAL)**

**Future improvement:**
```
Create separate VLAN for AI/compute traffic:
- TrueNAS, Workstation, d3kOS Pi on VLAN 10 (10 Gig switch)
- General devices on VLAN 1 (1 Gig switch)
- Reduces broadcast traffic, improves performance
```

**Benefit:**
- Isolated high-speed network for AI workloads
- No interference from other devices
- Better security

---

## 📊 Expected Performance After Fixes

### Current (Before Fix)

| Task | Laptop → TrueNAS Ollama | Time Breakdown |
|------|------------------------|----------------|
| Simple code | 176ms network + 30s inference | **30.2s** |
| Complex code | 176ms network + 90s inference | **90.2s** |
| Documentation | 176ms network + 45s inference | **45.2s** |

**Network overhead:** 176ms per request (negligible, but annoying)

---

### After Network Fix (TrueNAS 10 Gig)

| Task | Laptop → TrueNAS Ollama | Time Breakdown |
|------|------------------------|----------------|
| Simple code | 4ms network + 30s inference | **30.0s** |
| Complex code | 4ms network + 90s inference | **90.0s** |
| Documentation | 4ms network + 45s inference | **45.0s** |

**Network overhead:** 4ms per request (imperceptible)

---

### If Laptop Also on 10 Gig (Future)

| Task | Laptop → Workstation Ollama | Time Breakdown |
|------|----------------------------|----------------|
| Simple code | 1ms network + 8s inference (GPU) | **8.0s** ⚡ |
| Complex code | 1ms network + 15s inference (GPU) | **15.0s** ⚡ |
| Documentation | 1ms network + 10s inference (GPU) | **10.0s** ⚡ |

**Network overhead:** 1ms per request (negligible)

---

## 🎯 Recommendation

**BEFORE deploying Ollama:**

1. **Investigate TrueNAS network** (5-10 minutes)
   - Check interface speed in TrueNAS UI
   - Check physical connection
   - Identify root cause of 88ms latency

2. **Fix if simple** (10-30 minutes)
   - Move cable to correct switch
   - Replace bad cable
   - Configure interface correctly

3. **Deploy Ollama with good network** (1.5 hours)
   - Enjoy fast, responsive AI
   - No regrets later

**OR:**

**Deploy Ollama now, fix network later:**
- Accept slower performance temporarily
- Fix network when you have time
- Ollama will automatically become faster after network fix

---

## 🔧 Quick Network Check (Do Now)

**In TrueNAS Web UI (you're logged in):**

1. Click **Network** → **Interfaces**
2. Note the interface settings
3. Tell me:
   - **Link Speed:** _____ Mbps
   - **Interface Name:** _____ (e.g., igb0)
   - **Status:** UP or DOWN?

**This will tell us if it's connected at 10 Gig, 1 Gig, or slower.**

**Takes 1 minute - shall we check now?** 🔍
