from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
import threading
import json
from collections import defaultdict
import numpy as np

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False)

# Global data storage
class TrafficDataStore:
    def __init__(self):
        self.vehicles = {}  # {vehicle_id: vehicle_data}
        self.traffic_lights = {}
        self.emergency_vehicles = {}
        self.collision_warnings = []
        self.metrics = {
            'v2v_enabled': {
                'total_vehicles': 0,
                'average_speed': 0,
                'accidents_prevented': 0,
                'traffic_flow_efficiency': 0,
                'near_misses': 0,
                'stops_for_emergency': 0
            },
            'non_v2v': {
                'total_vehicles': 0,
                'average_speed': 0,
                'accidents': 0,
                'traffic_flow_efficiency': 0,
                'near_misses': 0,
                'emergency_conflicts': 0
            }
        }
        self.lock = threading.Lock()
        self.collision_history = []
        self.emergency_events = []
    
    def update_vehicle(self, vehicle_id, data):
        with self.lock:
            data['last_update'] = datetime.now().isoformat()
            self.vehicles[vehicle_id] = data
            self.calculate_metrics()
    
    def remove_vehicle(self, vehicle_id):
        with self.lock:
            if vehicle_id in self.vehicles:
                del self.vehicles[vehicle_id]
                self.calculate_metrics()
    
    def get_nearby_vehicles(self, vehicle_id, radius=100):
        """Get vehicles within radius (meters)"""
        if vehicle_id not in self.vehicles:
            return []
        
        vehicle = self.vehicles[vehicle_id]
        nearby = []
        
        for v_id, v_data in self.vehicles.items():
            if v_id != vehicle_id:
                distance = self.calculate_distance(
                    vehicle['location'], 
                    v_data['location']
                )
                if distance <= radius:
                    nearby.append({
                        'id': v_id,
                        'location': v_data['location'],
                        'speed': v_data['speed'],
                        'destination': v_data['destination'],
                        'distance': distance,
                        'v2v_enabled': v_data.get('v2v_enabled', False),
                        'type': v_data.get('type', 'normal'),
                        'heading': v_data.get('heading', 0)
                    })
        
        return nearby
    
    def calculate_distance(self, loc1, loc2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((loc1['x'] - loc2['x'])**2 + (loc1['y'] - loc2['y'])**2)
    
    def calculate_metrics(self):
        """Calculate system-wide metrics for V2V vs Non-V2V"""
        if not self.vehicles:
            return
        
        v2v_vehicles = [v for v in self.vehicles.values() if v.get('v2v_enabled', False)]
        non_v2v_vehicles = [v for v in self.vehicles.values() if not v.get('v2v_enabled', False)]
        
        # V2V metrics
        if v2v_vehicles:
            speeds = [v['speed'] for v in v2v_vehicles]
            self.metrics['v2v_enabled']['total_vehicles'] = len(v2v_vehicles)
            self.metrics['v2v_enabled']['average_speed'] = np.mean(speeds)
            self.metrics['v2v_enabled']['traffic_flow_efficiency'] = min(100, (np.mean(speeds) / 50) * 100)
        
        # Non-V2V metrics
        if non_v2v_vehicles:
            speeds = [v['speed'] for v in non_v2v_vehicles]
            self.metrics['non_v2v']['total_vehicles'] = len(non_v2v_vehicles)
            self.metrics['non_v2v']['average_speed'] = np.mean(speeds)
            self.metrics['non_v2v']['traffic_flow_efficiency'] = min(100, (np.mean(speeds) / 50) * 100)
    
    def record_collision(self, vehicle1_id, vehicle2_id, severity):
        """Record a collision event"""
        with self.lock:
            event = {
                'timestamp': datetime.now().isoformat(),
                'vehicle1': vehicle1_id,
                'vehicle2': vehicle2_id,
                'severity': severity,
                'v1_v2v': self.vehicles.get(vehicle1_id, {}).get('v2v_enabled', False),
                'v2_v2v': self.vehicles.get(vehicle2_id, {}).get('v2v_enabled', False)
            }
            self.collision_history.append(event)
            
            # Update metrics
            if event['v1_v2v'] or event['v2_v2v']:
                if severity == 'avoided':
                    self.metrics['v2v_enabled']['accidents_prevented'] += 1
                else:
                    self.metrics['v2v_enabled']['near_misses'] += 1
            else:
                if severity == 'collision':
                    self.metrics['non_v2v']['accidents'] += 1
                else:
                    self.metrics['non_v2v']['near_misses'] += 1
    
    def record_emergency_interaction(self, vehicle_id, stopped):
        """Record interaction with emergency vehicle"""
        with self.lock:
            vehicle = self.vehicles.get(vehicle_id, {})
            if vehicle.get('v2v_enabled') and stopped:
                self.metrics['v2v_enabled']['stops_for_emergency'] += 1
            elif not vehicle.get('v2v_enabled') and not stopped:
                self.metrics['non_v2v']['emergency_conflicts'] += 1

traffic_store = TrafficDataStore()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/vehicle/register', methods=['POST'])
def register_vehicle():
    data = request.json
    vehicle_id = data.get('vehicle_id')
    
    traffic_store.update_vehicle(vehicle_id, {
        'location': data.get('location', {'x': 0, 'y': 0}),
        'speed': data.get('speed', 0),
        'destination': data.get('destination', {'x': 0, 'y': 0}),
        'type': data.get('type', 'normal'),
        'v2v_enabled': data.get('v2v_enabled', True),
        'status': 'active',
        'heading': 0
    })
    
    return jsonify({
        'status': 'registered',
        'vehicle_id': vehicle_id,
        'v2v_enabled': data.get('v2v_enabled', True),
        'message': 'Vehicle successfully registered'
    })

@app.route('/api/vehicle/update', methods=['POST'])
def update_vehicle_data():
    data = request.json
    vehicle_id = data.get('vehicle_id')
    v2v_enabled = data.get('v2v_enabled', True)
    
    # Update vehicle data
    traffic_store.update_vehicle(vehicle_id, {
        'location': data.get('location'),
        'speed': data.get('speed'),
        'destination': data.get('destination'),
        'type': data.get('type', 'normal'),
        'heading': data.get('heading', 0),
        'v2v_enabled': v2v_enabled
    })
    
    # For V2V-enabled vehicles, get nearby vehicles and recommendations
    if v2v_enabled:
        nearby_vehicles = traffic_store.get_nearby_vehicles(vehicle_id, radius=150)
        
        # Check for emergency vehicles
        emergency_nearby = [v for v in nearby_vehicles if v.get('type') == 'emergency']
        
        # Calculate recommended speed using AI
        recommended_speed = calculate_optimal_speed(
            vehicle_id, 
            nearby_vehicles, 
            emergency_nearby
        )
        
        # Collision detection
        collision_risk, collision_details = detect_collision_risk(vehicle_id, nearby_vehicles)
        
        # Record collision avoidance if risk was high
        if collision_risk == 'high' and collision_details:
            traffic_store.record_collision(
                vehicle_id, 
                collision_details['vehicle_id'], 
                'avoided'
            )
        
        # Record emergency vehicle interaction
        if emergency_nearby:
            traffic_store.record_emergency_interaction(vehicle_id, recommended_speed == 0)
        
        # Broadcast to other V2V vehicles via WebSocket
        try:
            socketio.emit('vehicle_update', {
                'vehicle_id': vehicle_id,
                'location': data.get('location'),
                'speed': data.get('speed'),
                'type': data.get('type', 'normal'),
                'v2v_enabled': True
            }, broadcast=True)
        except Exception as e:
            # SocketIO emit can fail if no clients connected
            pass
        
        return jsonify({
            'vehicle_id': vehicle_id,
            'v2v_enabled': True,
            'recommended_speed': recommended_speed,
            'nearby_vehicles': nearby_vehicles,
            'emergency_alert': len(emergency_nearby) > 0,
            'emergency_details': emergency_nearby if emergency_nearby else None,
            'collision_risk': collision_risk,
            'collision_details': collision_details,
            'traffic_light_status': get_traffic_light_status(data.get('location'))
        })
    
    else:
        # Non-V2V vehicles don't get intelligent recommendations
        # They use basic rules and can't see other vehicles
        nearby_vehicles = traffic_store.get_nearby_vehicles(vehicle_id, radius=150)
        
        # Simple collision detection (less effective)
        for nearby in nearby_vehicles:
            if nearby['distance'] < 10:
                # Collision occurred!
                traffic_store.record_collision(vehicle_id, nearby['id'], 'collision')
                try:
                    socketio.emit('collision_event', {
                        'vehicle1': vehicle_id,
                        'vehicle2': nearby['id'],
                        'location': data.get('location')
                    }, broadcast=True)
                except Exception:
                    pass
        
        # Check for emergency vehicles (but can't see them unless very close)
        emergency_very_close = [v for v in nearby_vehicles if v.get('type') == 'emergency' and v['distance'] < 20]
        
        if emergency_very_close:
            # Non-V2V vehicle only reacts when emergency is very close
            traffic_store.record_emergency_interaction(vehicle_id, False)
        
        return jsonify({
            'vehicle_id': vehicle_id,
            'v2v_enabled': False,
            'recommended_speed': data.get('speed', 50),  # No recommendation, just echo back
            'nearby_vehicles': [],  # Can't see other vehicles
            'emergency_alert': False,  # Can't detect emergency vehicles early
            'collision_risk': 'unknown',
            'traffic_light_status': get_traffic_light_status(data.get('location'))
        })

@app.route('/api/vehicle/unregister', methods=['POST'])
def unregister_vehicle():
    data = request.json
    vehicle_id = data.get('vehicle_id')
    traffic_store.remove_vehicle(vehicle_id)
    return jsonify({'status': 'unregistered', 'vehicle_id': vehicle_id})

@app.route('/api/emergency/alert', methods=['POST'])
def emergency_alert():
    data = request.json
    vehicle_id = data.get('vehicle_id')
    location = data.get('location')
    
    # Mark as emergency vehicle
    if vehicle_id in traffic_store.vehicles:
        traffic_store.vehicles[vehicle_id]['type'] = 'emergency'
    
    # Get all vehicles in the area
    nearby = traffic_store.get_nearby_vehicles(vehicle_id, radius=300)
    
    # Record emergency event
    event = {
        'timestamp': datetime.now().isoformat(),
        'vehicle_id': vehicle_id,
        'location': location,
        'affected_vehicles': len(nearby),
        'v2v_aware_count': len([v for v in nearby if v.get('v2v_enabled')])
    }
    traffic_store.emergency_events.append(event)
    
    # Broadcast emergency alert (only V2V vehicles will receive and react)
    try:
        socketio.emit('emergency_alert', {
            'emergency_vehicle_id': vehicle_id,
            'location': location,
            'affected_vehicles': [v['id'] for v in nearby if v.get('v2v_enabled')]
        }, broadcast=True)
    except Exception:
        pass
    
    # Update traffic lights to give priority
    update_traffic_lights_for_emergency(location)
    
    return jsonify({
        'status': 'alert_sent',
        'total_vehicles_nearby': len(nearby),
        'v2v_vehicles_alerted': len([v for v in nearby if v.get('v2v_enabled')]),
        'non_v2v_vehicles': len([v for v in nearby if not v.get('v2v_enabled')])
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    return jsonify(traffic_store.metrics)

@app.route('/api/comparison', methods=['GET'])
def get_comparison():
    """Get detailed comparison between V2V and Non-V2V vehicles"""
    v2v = traffic_store.metrics['v2v_enabled']
    non_v2v = traffic_store.metrics['non_v2v']
    
    # Calculate improvements
    speed_improvement = ((v2v['average_speed'] - non_v2v['average_speed']) / max(non_v2v['average_speed'], 1)) * 100 if non_v2v['average_speed'] > 0 else 0
    efficiency_improvement = v2v['traffic_flow_efficiency'] - non_v2v['traffic_flow_efficiency']
    
    return jsonify({
        'v2v_enabled': v2v,
        'non_v2v': non_v2v,
        'improvements': {
            'speed_increase_percent': speed_improvement,
            'efficiency_increase_percent': efficiency_improvement,
            'accidents_prevented': v2v['accidents_prevented'],
            'accidents_occurred': non_v2v['accidents'],
            'emergency_response_better': v2v['stops_for_emergency'] > non_v2v['emergency_conflicts']
        },
        'collision_history': traffic_store.collision_history[-20:],  # Last 20 events
        'emergency_events': traffic_store.emergency_events[-10:]  # Last 10 events
    })

@app.route('/api/vehicles', methods=['GET'])
def get_all_vehicles():
    v2v_vehicles = [v for v in traffic_store.vehicles.values() if v.get('v2v_enabled')]
    non_v2v_vehicles = [v for v in traffic_store.vehicles.values() if not v.get('v2v_enabled')]
    
    return jsonify({
        'all_vehicles': list(traffic_store.vehicles.values()),
        'v2v_vehicles': v2v_vehicles,
        'non_v2v_vehicles': non_v2v_vehicles,
        'total_count': len(traffic_store.vehicles),
        'v2v_count': len(v2v_vehicles),
        'non_v2v_count': len(non_v2v_vehicles)
    })

def calculate_optimal_speed(vehicle_id, nearby_vehicles, emergency_nearby):
    """AI-based speed optimization for V2V vehicles"""
    if vehicle_id not in traffic_store.vehicles:
        return 50
    
    vehicle = traffic_store.vehicles[vehicle_id]
    base_speed = 60  # km/h
    
    # CRITICAL: Stop for emergency vehicles
    if emergency_nearby:
        return 0
    
    # Reduce speed if there are many nearby vehicles (intelligent spacing)
    if len(nearby_vehicles) > 8:
        base_speed *= 0.6
    elif len(nearby_vehicles) > 5:
        base_speed *= 0.75
    elif len(nearby_vehicles) > 3:
        base_speed *= 0.9
    
    # Adjust based on collision risk with predictive analysis
    for nearby in nearby_vehicles:
        if nearby['distance'] < 15:  # Too close
            base_speed *= 0.4
            break
        elif nearby['distance'] < 30:
            base_speed *= 0.7
        elif nearby['distance'] < 50:
            base_speed *= 0.85
    
    # Consider relative speeds for smoother flow
    if nearby_vehicles:
        avg_nearby_speed = np.mean([v['speed'] for v in nearby_vehicles])
        # Adjust to match traffic flow
        base_speed = (base_speed + avg_nearby_speed) / 2
    
    return max(0, min(80, base_speed))

def detect_collision_risk(vehicle_id, nearby_vehicles):
    """Advanced collision detection for V2V vehicles"""
    if vehicle_id not in traffic_store.vehicles:
        return 'none', None
    
    vehicle = traffic_store.vehicles[vehicle_id]
    max_risk = 'low'
    risk_details = None
    
    for nearby in nearby_vehicles:
        # Calculate if vehicles are on collision course
        # Using heading and position to predict
        v1_heading = vehicle.get('heading', 0)
        v2_heading = nearby.get('heading', 0)
        
        # Check if headings are converging
        heading_diff = abs(v1_heading - v2_heading)
        
        distance = nearby['distance']
        
        # High risk if very close and moving
        if distance < 12 and vehicle['speed'] > 15:
            max_risk = 'high'
            risk_details = {
                'vehicle_id': nearby['id'],
                'distance': distance,
                'relative_speed': abs(vehicle['speed'] - nearby['speed'])
            }
            break
        elif distance < 25 and vehicle['speed'] > 30:
            if heading_diff < 30:  # Similar heading = following/converging
                max_risk = 'medium'
                risk_details = {
                    'vehicle_id': nearby['id'],
                    'distance': distance,
                    'relative_speed': abs(vehicle['speed'] - nearby['speed'])
                }
        elif distance < 40 and vehicle['speed'] > 50:
            max_risk = max(max_risk, 'medium') if max_risk != 'high' else max_risk
    
    return max_risk, risk_details

def get_traffic_light_status(location):
    """Get traffic light status at location"""
    # Simple grid-based traffic light system
    grid_x = int(location['x'] // 100)
    grid_y = int(location['y'] // 100)
    
    # Alternate lights based on time and location
    import time
    cycle_time = int(time.time()) % 60
    
    if cycle_time < 30:
        return 'green' if (grid_x + grid_y) % 2 == 0 else 'red'
    else:
        return 'red' if (grid_x + grid_y) % 2 == 0 else 'green'

def update_traffic_lights_for_emergency(location):
    """Update traffic lights to prioritize emergency vehicle path"""
    print(f"🚨 Traffic lights updated for emergency at {location}")
    try:
        socketio.emit('traffic_light_override', {
            'location': location,
            'status': 'emergency_priority'
        }, broadcast=True)
    except Exception:
        pass

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print("=" * 60)
    print("🚦 V2V Traffic Management System - Mother Server")
    print("=" * 60)
    print("📡 Server running on http://localhost:5000")
    print("🔌 WebSocket enabled for real-time communication")
    print("🤖 AI-powered traffic optimization active")
    print("=" * 60)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
