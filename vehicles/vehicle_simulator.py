import requests
import time
import random
import numpy as np
import threading
import json
from datetime import datetime

class Vehicle:
    def __init__(self, vehicle_id, start_location, destination, vehicle_type='normal', v2v_enabled=True):
        self.vehicle_id = vehicle_id
        self.location = start_location
        self.destination = destination
        self.speed = random.uniform(40, 60) if vehicle_type == 'normal' else random.uniform(80, 100)
        self.heading = self.calculate_heading()
        self.vehicle_type = vehicle_type
        self.v2v_enabled = v2v_enabled
        self.is_running = True
        self.server_url = "http://v2v.mulearnscet.in"
        self.collision_count = 0
        self.near_miss_count = 0
        self.emergency_stops = 0
        self.total_distance = 0
        self.start_time = time.time()
        
    def calculate_heading(self):
        """Calculate heading towards destination"""
        dx = self.destination['x'] - self.location['x']
        dy = self.destination['y'] - self.location['y']
        return np.degrees(np.arctan2(dy, dx))
    
    def register(self):
        """Register with mother server"""
        try:
            response = requests.post(
                f"{self.server_url}/api/vehicle/register",
                json={
                    'vehicle_id': self.vehicle_id,
                    'location': self.location,
                    'destination': self.destination,
                    'speed': self.speed,
                    'type': self.vehicle_type,
                    'v2v_enabled': self.v2v_enabled
                },
                timeout=5
            )
            v2v_status = "V2V" if self.v2v_enabled else "Non-V2V"
            type_icon = "🚑" if self.vehicle_type == 'emergency' else "🚗"
            print(f"✅ {type_icon} Vehicle {self.vehicle_id} ({v2v_status}) registered")
        except requests.exceptions.RequestException as e:
            print(f"❌ Registration failed for {self.vehicle_id}: {e}")
    
    def update_position(self, dt=1.0):
        """Update vehicle position based on speed and heading"""
        # Convert speed from km/h to m/s
        speed_ms = self.speed / 3.6
        
        # Calculate distance moved
        distance_moved = speed_ms * dt
        self.total_distance += distance_moved
        
        # Update position
        self.location['x'] += speed_ms * np.cos(np.radians(self.heading)) * dt
        self.location['y'] += speed_ms * np.sin(np.radians(self.heading)) * dt
        
        # Update heading towards destination
        self.heading = self.calculate_heading()
        
        # Check if reached destination
        distance_to_dest = np.sqrt(
            (self.destination['x'] - self.location['x'])**2 +
            (self.destination['y'] - self.location['y'])**2
        )
        
        if distance_to_dest < 10:  # Within 10 meters
            elapsed_time = time.time() - self.start_time
            avg_speed = (self.total_distance / elapsed_time) * 3.6 if elapsed_time > 0 else 0
            v2v_status = "V2V" if self.v2v_enabled else "Non-V2V"
            print(f"🎯 {self.vehicle_id} ({v2v_status}) reached destination!")
            print(f"   ⏱️  Time: {elapsed_time:.1f}s | Avg Speed: {avg_speed:.1f} km/h")
            print(f"   📊 Stats - Collisions: {self.collision_count} | Near misses: {self.near_miss_count} | Emergency stops: {self.emergency_stops}")
            self.is_running = False
    
    def send_update(self):
        """Send update to mother server and receive recommendations"""
        try:
            response = requests.post(
                f"{self.server_url}/api/vehicle/update",
                json={
                    'vehicle_id': self.vehicle_id,
                    'location': self.location,
                    'speed': self.speed,
                    'destination': self.destination,
                    'heading': self.heading,
                    'type': self.vehicle_type,
                    'v2v_enabled': self.v2v_enabled
                },
                timeout=5
            )
            
            data = response.json()
            
            if self.v2v_enabled:
                # V2V vehicles get intelligent recommendations
                recommended_speed = data.get('recommended_speed', self.speed)
                
                # Check if stopping for emergency
                if data.get('emergency_alert') and recommended_speed == 0:
                    emergency_details = data.get('emergency_details', [])
                    if emergency_details:
                        self.emergency_stops += 1
                        print(f"🚨 {self.vehicle_id} (V2V): STOPPING for emergency vehicle {emergency_details[0]['id']}")
                
                # Adjust speed based on recommendation
                self.adjust_speed(recommended_speed)
                
                # Handle collision warnings
                collision_risk = data.get('collision_risk', 'low')
                if collision_risk == 'high':
                    self.near_miss_count += 1
                    collision_details = data.get('collision_details')
                    if collision_details:
                        print(f"⚠️  {self.vehicle_id} (V2V): Near miss avoided! Distance: {collision_details['distance']:.1f}m")
                elif collision_risk == 'medium':
                    print(f"⚡ {self.vehicle_id} (V2V): Slowing for safety")
                
                return data
            else:
                # Non-V2V vehicles don't get recommendations
                # They maintain their speed and can't avoid collisions well
                
                # Simple behavior: slow down at intersections only
                grid_x = int(self.location['x'] // 100)
                grid_y = int(self.location['y'] // 100)
                
                # Random slow down to simulate normal driving
                if random.random() < 0.05:  # 5% chance to slow down
                    self.speed = max(20, self.speed * 0.8)
                else:
                    # Gradually accelerate back to target
                    target_speed = 50
                    self.speed = min(target_speed, self.speed * 1.05)
                
                return data
            
        except requests.exceptions.RequestException as e:
            # print(f"❌ Update failed for {self.vehicle_id}: {e}")
            return None
    
    def adjust_speed(self, target_speed):
        """Gradually adjust speed to target (V2V only)"""
        # Smooth acceleration/deceleration
        speed_diff = target_speed - self.speed
        
        if abs(speed_diff) > 20:
            # Emergency braking or quick acceleration
            self.speed += speed_diff * 0.5
        else:
            # Smooth adjustment
            self.speed += speed_diff * 0.3
        
        self.speed = max(0, min(100, self.speed))  # Clamp between 0 and 100
    
    def run(self):
        """Main vehicle loop"""
        self.register()
        time.sleep(0.5)  # Initial delay
        
        while self.is_running:
            self.update_position(dt=1.0)
            server_response = self.send_update()
            
            # Log status periodically (every 5 seconds)
            if int(time.time()) % 5 == 0:
                v2v_status = "V2V ✓" if self.v2v_enabled else "Non-V2V ✗"
                type_icon = "🚑" if self.vehicle_type == 'emergency' else "🚗"
                if server_response and self.v2v_enabled:
                    nearby_count = len(server_response.get('nearby_vehicles', []))
                    print(f"{type_icon} {self.vehicle_id} [{v2v_status}]: "
                          f"Pos({self.location['x']:.0f}, {self.location['y']:.0f}) | "
                          f"Speed: {self.speed:.1f} km/h | Nearby: {nearby_count}")
                elif not self.v2v_enabled:
                    print(f"{type_icon} {self.vehicle_id} [{v2v_status}]: "
                          f"Pos({self.location['x']:.0f}, {self.location['y']:.0f}) | "
                          f"Speed: {self.speed:.1f} km/h | No V2V data")
            
            time.sleep(1)  # Update every second
        
        # Unregister when done
        try:
            requests.post(
                f"{self.server_url}/api/vehicle/unregister",
                json={'vehicle_id': self.vehicle_id},
                timeout=5
            )
        except:
            pass

class TrafficSimulator:
    def __init__(self, num_v2v_vehicles=10, num_non_v2v_vehicles=10, num_emergency=2):
        self.vehicles = []
        self.threads = []
        self.num_v2v_vehicles = num_v2v_vehicles
        self.num_non_v2v_vehicles = num_non_v2v_vehicles
        self.num_emergency = num_emergency
        
    def create_vehicles(self):
        """Create multiple vehicles with random start/end points"""
        # Define a grid area (0-1000 meters)
        grid_size = 1000
        vehicle_count = 0
        
        # Create emergency vehicles (always V2V enabled)
        for i in range(self.num_emergency):
            start = {
                'x': random.uniform(0, grid_size),
                'y': random.uniform(0, grid_size)
            }
            dest = {
                'x': random.uniform(0, grid_size),
                'y': random.uniform(0, grid_size)
            }
            
            vehicle = Vehicle(
                f"EMG{i:02d}", 
                start, 
                dest, 
                vehicle_type='emergency',
                v2v_enabled=True
            )
            self.vehicles.append(vehicle)
            vehicle_count += 1
        
        # Create V2V-enabled regular vehicles
        for i in range(self.num_v2v_vehicles):
            start = {
                'x': random.uniform(0, grid_size),
                'y': random.uniform(0, grid_size)
            }
            dest = {
                'x': random.uniform(0, grid_size),
                'y': random.uniform(0, grid_size)
            }
            
            vehicle = Vehicle(
                f"V2V{i:03d}", 
                start, 
                dest, 
                vehicle_type='normal',
                v2v_enabled=True
            )
            self.vehicles.append(vehicle)
            vehicle_count += 1
        
        # Create Non-V2V vehicles
        for i in range(self.num_non_v2v_vehicles):
            start = {
                'x': random.uniform(0, grid_size),
                'y': random.uniform(0, grid_size)
            }
            dest = {
                'x': random.uniform(0, grid_size),
                'y': random.uniform(0, grid_size)
            }
            
            vehicle = Vehicle(
                f"OLD{i:03d}", 
                start, 
                dest, 
                vehicle_type='normal',
                v2v_enabled=False
            )
            self.vehicles.append(vehicle)
            vehicle_count += 1
    
    def start_simulation(self):
        """Start all vehicle threads"""
        print("=" * 80)
        print("🚦 V2V TRAFFIC MANAGEMENT SYSTEM - SIMULATION STARTING")
        print("=" * 80)
        print(f"📊 Simulation Parameters:")
        print(f"   🚑 Emergency Vehicles (V2V): {self.num_emergency}")
        print(f"   ✓  V2V-Enabled Vehicles: {self.num_v2v_vehicles}")
        print(f"   ✗  Non-V2V Vehicles: {self.num_non_v2v_vehicles}")
        print(f"   📈 Total Vehicles: {self.num_emergency + self.num_v2v_vehicles + self.num_non_v2v_vehicles}")
        print("=" * 80)
        print("🎯 Watch for differences:")
        print("   - V2V vehicles coordinate and avoid collisions")
        print("   - Non-V2V vehicles operate independently")
        print("   - Emergency vehicles get priority from V2V vehicles only")
        print("=" * 80)
        
        self.create_vehicles()
        
        # Start emergency vehicles first
        emergency_vehicles = [v for v in self.vehicles if v.vehicle_type == 'emergency']
        for vehicle in emergency_vehicles:
            thread = threading.Thread(target=vehicle.run, daemon=True)
            thread.start()
            self.threads.append(thread)
            time.sleep(0.3)
        
        # Then start regular vehicles
        regular_vehicles = [v for v in self.vehicles if v.vehicle_type != 'emergency']
        for vehicle in regular_vehicles:
            thread = threading.Thread(target=vehicle.run, daemon=True)
            thread.start()
            self.threads.append(thread)
            time.sleep(0.2)  # Stagger starts
        
        print("\n🚀 All vehicles initialized and running...")
        print("📺 Open the dashboard at http://localhost:8501 to visualize\n")
        
        # Wait for all vehicles to finish
        try:
            while any(t.is_alive() for t in self.threads):
                time.sleep(2)
                # Print periodic summary
                active_vehicles = sum(1 for v in self.vehicles if v.is_running)
                if active_vehicles > 0:
                    print(f"📍 Active vehicles: {active_vehicles}/{len(self.vehicles)}")
        except KeyboardInterrupt:
            print("\n" + "=" * 80)
            print("🛑 Simulation stopped by user")
            print("=" * 80)
            for vehicle in self.vehicles:
                vehicle.is_running = False
        
        print("\n" + "=" * 80)
        print("✅ SIMULATION COMPLETED")
        print("=" * 80)
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print final statistics"""
        v2v_vehicles = [v for v in self.vehicles if v.v2v_enabled and v.vehicle_type != 'emergency']
        non_v2v_vehicles = [v for v in self.vehicles if not v.v2v_enabled]
        
        print("\n📊 FINAL STATISTICS:")
        print("-" * 80)
        
        if v2v_vehicles:
            total_collisions = sum(v.collision_count for v in v2v_vehicles)
            total_near_misses = sum(v.near_miss_count for v in v2v_vehicles)
            total_emergency_stops = sum(v.emergency_stops for v in v2v_vehicles)
            print(f"✓  V2V Vehicles ({len(v2v_vehicles)}):")
            print(f"   - Collisions: {total_collisions}")
            print(f"   - Near misses avoided: {total_near_misses}")
            print(f"   - Emergency vehicle yields: {total_emergency_stops}")
        
        if non_v2v_vehicles:
            total_collisions = sum(v.collision_count for v in non_v2v_vehicles)
            print(f"\n✗  Non-V2V Vehicles ({len(non_v2v_vehicles)}):")
            print(f"   - Collisions: {total_collisions}")
            print(f"   - No collision avoidance")
            print(f"   - No emergency vehicle awareness")
        
        print("=" * 80)

if __name__ == '__main__':
    # Run simulation with mixed traffic
    # You can adjust these numbers to see different scenarios
    simulator = TrafficSimulator(
        num_v2v_vehicles=8,      # Smart vehicles with V2V
        num_non_v2v_vehicles=8,  # Legacy vehicles without V2V
        num_emergency=2          # Emergency vehicles
    )
    simulator.start_simulation()
