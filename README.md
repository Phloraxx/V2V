# V2V Traffic Management System

A comprehensive prototype demonstrating **Vehicle-to-Vehicle (V2V) communication** for intelligent traffic management, comparing smart V2V-enabled vehicles with legacy non-V2V vehicles.

## 🎯 Key Features

### Core Capabilities
✅ **V2V Communication** - Real-time data exchange between smart vehicles  
✅ **AI-Powered Traffic Optimization** - Machine learning for intelligent speed recommendations  
✅ **Collision Detection & Avoidance** - Predictive collision prevention for V2V vehicles  
✅ **Emergency Vehicle Priority** - Automatic path clearing (V2V vehicles only)  
✅ **Smart Traffic Lights** - Adaptive signal control  
✅ **Real-time Dashboard** - Live visualization and comparison  

### Comparison Features
🆚 **V2V vs Non-V2V Comparison**
- Side-by-side performance metrics
- Collision avoidance effectiveness
- Emergency vehicle response
- Traffic flow efficiency
- Speed optimization

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MOTHER SERVER (Cloud)                     │
│  - Central data processing                                   │
│  - AI-based traffic optimization                            │
│  - V2V message routing                                       │
│  - Collision detection & prevention                          │
└─────────────────────────────────────────────────────────────┘
                            ▲ │
                            │ │
              ┌─────────────┘ └─────────────┐
              │                              │
    ┌─────────▼──────────┐        ┌─────────▼──────────┐
    │  V2V-ENABLED       │        │  NON-V2V VEHICLES  │
    │  VEHICLES          │        │  (Legacy)          │
    │  ✓ Smart routing   │        │  ✗ No coordination │
    │  ✓ Collision avoid │        │  ✗ No warnings     │
    │  ✓ Emergency aware │        │  ✗ No V2V data     │
    └────────────────────┘        └────────────────────┘
              │
    ┌─────────▼──────────┐
    │  EMERGENCY         │
    │  VEHICLES          │
    │  🚑 Priority mode  │
    └────────────────────┘
```

## 📊 What This Prototype Demonstrates

### 1. **V2V-Enabled Vehicles**
- Receive real-time data from nearby vehicles
- Get AI-optimized speed recommendations
- Avoid collisions through predictive analysis
- Automatically yield to emergency vehicles
- Coordinate for smoother traffic flow

### 2. **Non-V2V Vehicles (Legacy)**
- Operate independently without vehicle coordination
- No collision warnings or avoidance
- Cannot detect emergency vehicles until very close
- Less efficient routing
- Higher accident risk

### 3. **Emergency Vehicles**
- Broadcast priority alerts
- V2V vehicles automatically clear path
- Non-V2V vehicles don't receive alerts
- Demonstrates V2V safety advantage

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Install Dependencies

```bash
cd "c:\Users\drvij\Desktop\MuLearn Scet\Microv2"
pip install -r requirements.txt
```

### Step 2: Start the Mother Server

Open a terminal and run:

```bash
cd backend/mother_server
python app.py
```

You should see:
```
🚦 V2V Traffic Management System - Mother Server
📡 Server running on http://localhost:5000
```

### Step 3: Start the Dashboard

Open a **new terminal** and run:

```bash
cd dashboard
streamlit run app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

### Step 4: Run the Vehicle Simulation

Open a **third terminal** and run:

```bash
cd vehicles
python vehicle_simulator.py
```

## 🎮 Usage

### Default Simulation
The simulation runs with:
- **8 V2V-enabled vehicles** (smart, coordinated)
- **8 Non-V2V vehicles** (legacy, uncoordinated)
- **2 Emergency vehicles** (V2V-enabled with priority)

### Customizing the Simulation

Edit `vehicles/vehicle_simulator.py` at the bottom:

```python
simulator = TrafficSimulator(
    num_v2v_vehicles=10,      # Change number of smart vehicles
    num_non_v2v_vehicles=5,   # Change number of legacy vehicles
    num_emergency=2            # Change number of emergency vehicles
)
```

### What to Watch For

1. **Emergency Vehicle Alerts**
   - V2V vehicles: Stop and yield immediately when emergency vehicle is 150m+ away
   - Non-V2V vehicles: No alert, potential conflicts

2. **Collision Avoidance**
   - V2V vehicles: Predictive braking, near-miss avoidance
   - Non-V2V vehicles: Reactive only, potential collisions

3. **Traffic Flow**
   - V2V vehicles: Coordinated speeds, smooth flow
   - Non-V2V vehicles: Independent speeds, stop-and-go

## 📺 Dashboard Features

### Main Metrics
- Total vehicles (V2V vs Non-V2V count)
- Emergency vehicle status
- Real-time counts

### Comparison View
- **V2V Vehicles:**
  - Average speed
  - Traffic efficiency
  - Accidents prevented
  - Near misses avoided
  - Emergency vehicle yields

- **Non-V2V Vehicles:**
  - Average speed
  - Traffic efficiency
  - Accidents occurred
  - Emergency conflicts
  - No collision avoidance

### Performance Improvements
- Speed increase percentage (V2V vs Non-V2V)
- Efficiency gains
- Safety improvements
- Emergency response comparison

### Real-time Map
- 🚑 Red stars = Emergency vehicles
- 🔵 Blue circles = V2V-enabled vehicles
- ⚫ Gray X's = Non-V2V vehicles

### Recent Events
- Collision events (avoided vs occurred)
- Emergency vehicle interactions
- Near-miss incidents

## 🧪 Testing Different Scenarios

### Scenario 1: Emergency Response
```python
# High emergency vehicle density
simulator = TrafficSimulator(
    num_v2v_vehicles=15,
    num_non_v2v_vehicles=15,
    num_emergency=5  # More emergencies
)
```

**Expected Result:** V2V vehicles clear path, Non-V2V vehicles cause delays

### Scenario 2: Dense Traffic
```python
# High vehicle density
simulator = TrafficSimulator(
    num_v2v_vehicles=20,
    num_non_v2v_vehicles=5,
    num_emergency=1
)
```

**Expected Result:** V2V vehicles coordinate efficiently, maintain flow

### Scenario 3: Legacy Traffic
```python
# Mostly non-V2V vehicles
simulator = TrafficSimulator(
    num_v2v_vehicles=5,
    num_non_v2v_vehicles=20,
    num_emergency=2
)
```

**Expected Result:** More collisions, poor emergency response

## 📈 Performance Metrics

The system tracks and displays:

### V2V Vehicles
- ✅ Accidents prevented
- ✅ Near misses avoided
- ✅ Emergency stops (coordinated)
- ✅ Higher average speed
- ✅ Better traffic flow efficiency

### Non-V2V Vehicles
- ❌ Collisions occurred
- ❌ Emergency conflicts
- ❌ No predictive avoidance
- ❌ Lower average speed
- ❌ Lower traffic efficiency

## 🔧 API Endpoints

### Vehicle Registration
```
POST /api/vehicle/register
Body: {
  "vehicle_id": "V001",
  "location": {"x": 100, "y": 200},
  "destination": {"x": 500, "y": 600},
  "type": "normal",
  "v2v_enabled": true
}
```

### Vehicle Update
```
POST /api/vehicle/update
Body: {
  "vehicle_id": "V001",
  "location": {"x": 105, "y": 205},
  "speed": 50,
  "heading": 45,
  "v2v_enabled": true
}
```

### Emergency Alert
```
POST /api/emergency/alert
Body: {
  "vehicle_id": "EMG01",
  "location": {"x": 300, "y": 400}
}
```

### Get Metrics
```
GET /api/metrics
Returns: V2V vs Non-V2V comparison data
```

### Get Comparison
```
GET /api/comparison
Returns: Detailed comparison and improvements
```

## 🎓 Educational Value

This prototype demonstrates:

1. **Safety Benefits of V2V**
   - Collision avoidance
   - Emergency vehicle priority
   - Predictive warnings

2. **Traffic Efficiency**
   - Coordinated speed management
   - Reduced congestion
   - Smoother flow

3. **AI Integration**
   - Real-time decision making
   - Predictive analytics
   - Optimal routing

4. **Cloud Infrastructure**
   - Centralized data processing
   - Scalable architecture
   - Real-time communication

## 📝 Technical Details

### V2V Communication Protocol
- WebSocket for real-time updates
- REST API for data exchange
- 1-second update interval
- 150m communication radius

### AI Decision Making
- Collision prediction algorithm
- Speed optimization based on traffic density
- Emergency vehicle priority routing
- Traffic light coordination

### Collision Detection
- Predictive analysis using heading and speed
- Distance-based risk assessment
- Multi-vehicle coordination
- Real-time warnings

## 🚧 Future Enhancements

- [ ] Machine learning for traffic prediction
- [ ] Real GPS integration
- [ ] Mobile app interface
- [ ] Weather condition factors
- [ ] Road infrastructure integration
- [ ] Multi-intersection coordination
- [ ] Historical data analysis
- [ ] Route optimization algorithms

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill the process if needed
taskkill /PID <PID> /F
```

### Dashboard not updating
- Ensure mother server is running
- Check browser console for errors
- Verify server URL is correct

### No vehicles appearing
- Make sure vehicle_simulator.py is running
- Check terminal for connection errors
- Verify server is accessible

## 📄 License

MIT License - Feel free to use for educational and research purposes

## 👥 Contributors

Built for MuLearn SCET - Traffic Management System Prototype

---

**Ready to see the difference V2V makes?**

Run all three components and watch the dashboard to see V2V-enabled vehicles outperform legacy vehicles in safety, efficiency, and emergency response! 🚦🚗✨
