# 🔧 Troubleshooting Guide

## ✅ ISSUE FIXED: SocketIO Error

The SocketIO error you encountered has been fixed! The issue was:
- SocketIO trying to emit messages before fully initialized
- Missing error handling for when no clients are connected

**Solution Applied:**
- Added `async_mode='threading'` to SocketIO initialization
- Wrapped all `socketio.emit()` calls in try-except blocks
- Updated dependencies for better compatibility

## 🚀 How to Run (Updated)

### Easy Method: Use the Startup Scripts

1. **Double-click:** `start_server.bat`
2. **Double-click:** `start_dashboard.bat` (in a new window)
3. **Double-click:** `start_simulation.bat` (in a new window)

### Manual Method: Use Command Line

**Terminal 1 - Mother Server:**
```bash
cd "c:\Users\drvij\Desktop\MuLearn Scet\Microv2\backend\mother_server"
python app.py
```

**Terminal 2 - Dashboard:**
```bash
cd "c:\Users\drvij\Desktop\MuLearn Scet\Microv2\dashboard"
streamlit run app.py
```

**Terminal 3 - Simulation:**
```bash
cd "c:\Users\drvij\Desktop\MuLearn Scet\Microv2\vehicles"
python vehicle_simulator.py
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Port Already in Use

**Error:**
```
Address already in use
Port 5000 is already allocated
```

**Solution:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with actual number)
taskkill /PID <PID> /F

# Or use a different port by editing app.py (last line)
# Change: socketio.run(app, host='0.0.0.0', port=5000, ...)
# To: socketio.run(app, host='0.0.0.0', port=5001, ...)
```

### Issue 2: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'flask_socketio'
```

**Solution:**
```bash
# Reinstall all dependencies
cd "c:\Users\drvij\Desktop\MuLearn Scet\Microv2"
pip install -r requirements.txt

# Or install individually
pip install flask flask-socketio flask-cors requests numpy pandas streamlit plotly
```

### Issue 3: Dashboard Not Loading

**Error:**
```
streamlit: command not found
```

**Solution:**
```bash
# Install streamlit
pip install streamlit

# Or use Python module syntax
python -m streamlit run app.py
```

### Issue 4: Connection Refused

**Error:**
```
requests.exceptions.ConnectionError: Connection refused
```

**Cause:** Mother server is not running

**Solution:**
1. Make sure Terminal 1 (mother server) is running first
2. Wait for "Server running on http://localhost:5000" message
3. Then start the simulation

### Issue 5: No Data on Dashboard

**Symptoms:**
- Dashboard shows "No vehicles connected"
- Empty map

**Solution:**
1. **Check:** Is the mother server running? (Terminal 1)
2. **Check:** Is the simulation running? (Terminal 3)
3. **Refresh:** Press R in the dashboard browser tab
4. **Wait:** Give it 5-10 seconds for data to appear

### Issue 6: WebSocket Connection Error

**Error:**
```
WebSocket connection failed
```

**Solution:**
```bash
# Update python-socketio
pip install --upgrade python-socketio python-engineio flask-socketio

# Or use the fixed version
pip install python-socketio==5.10.0 python-engineio==4.8.0
```

### Issue 7: Vehicles Not Moving

**Symptoms:**
- Vehicles registered but not updating
- Position not changing

**Solution:**
1. Check if vehicles reached their destinations
2. Restart the simulation with fresh destinations
3. Check terminal for error messages

### Issue 8: Import Errors (Python 3.13)

**Error:**
```
ImportError: cannot import name 'X' from 'Y'
```

**Solution:**
```bash
# Some packages may not be compatible with Python 3.13
# Try using Python 3.10 or 3.11

# Or downgrade specific packages
pip install numpy==1.24.3 pandas==2.0.3
```

---

## 🔍 Debugging Tips

### Check Server Status
```bash
# Test if server is running
curl http://localhost:5000/api/health

# Expected response:
# {"status": "healthy", "timestamp": "..."}
```

### Check Vehicle Registration
```bash
# Check if vehicles are registered
curl http://localhost:5000/api/vehicles

# Should show list of active vehicles
```

### Monitor Logs

**Server Terminal:** Watch for:
- ✅ "Vehicle registered"
- 🚨 "Emergency alert"
- ⚠️ Error messages

**Simulation Terminal:** Watch for:
- 🚗 Vehicle movements
- 🚨 Emergency events
- ⚠️ Collision warnings

**Dashboard:** Check browser console (F12) for errors

---

## 🛠️ Reset Everything

If things are completely broken, try this:

```bash
# 1. Stop all terminals (Ctrl+C in each)

# 2. Kill any hanging processes
taskkill /F /IM python.exe
taskkill /F /IM streamlit.exe

# 3. Reinstall dependencies
cd "c:\Users\drvij\Desktop\MuLearn Scet\Microv2"
pip uninstall -y flask flask-socketio flask-cors streamlit plotly
pip install -r requirements.txt

# 4. Start fresh
# Run the three startup scripts in order
```

---

## 📊 Performance Issues

### Dashboard Slow/Laggy

**Solution:**
- Reduce number of vehicles in simulation
- Increase refresh rate (slider in dashboard)
- Close other browser tabs

### High CPU Usage

**Solution:**
- Reduce number of vehicles
- Increase sleep time in vehicle_simulator.py (line with `time.sleep(1)`)

### Memory Issues

**Solution:**
- Restart the simulation periodically
- Reduce number of vehicles
- Clear browser cache

---

## ✅ Verification Checklist

Before running, verify:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip list | grep flask`)
- [ ] Port 5000 is free
- [ ] Port 8501 is free
- [ ] No firewalls blocking localhost
- [ ] Sufficient RAM (minimum 2GB free)

---

## 🆘 Still Having Issues?

### Check These Files:

1. **app.py** - Should have `async_mode='threading'`
2. **vehicle_simulator.py** - Should have server_url = "http://localhost:5000"
3. **requirements.txt** - Should have all packages listed

### Quick Test:

```bash
# Test 1: Python works
python --version

# Test 2: Packages installed
python -c "import flask, flask_socketio, streamlit, plotly; print('All packages OK')"

# Test 3: Server can start
cd backend/mother_server
python -c "from app import app; print('App imports OK')"
```

---

## 💡 Pro Tips

1. **Always start server first** - Wait for "Server running" message
2. **Check terminals** - Look for errors in all three terminals
3. **Be patient** - Give 5-10 seconds for connections
4. **Use startup scripts** - Easier than typing commands
5. **Monitor all three** - Keep an eye on all terminals

---

## 📝 Common Startup Sequence

```
1. Start server (Terminal 1)
   → Wait for "Server running on http://localhost:5000"
   
2. Start dashboard (Terminal 2)
   → Browser opens automatically
   → Shows "No vehicles connected" (normal)
   
3. Start simulation (Terminal 3)
   → Vehicles start registering
   → Dashboard updates with data
   → Watch the magic happen! ✨
```

---

**The error you encountered has been fixed! Try running again with the startup scripts.** 🚀
