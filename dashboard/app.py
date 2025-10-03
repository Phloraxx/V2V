import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="V2V Traffic Management Dashboard", layout="wide", page_icon="s")

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .v2v-badge {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .non-v2v-badge {
        background-color: #f44336;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .emergency-badge {
        background-color: #ff9800;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Server URL
SERVER_URL = "https://v2v.mulearnscet.in"

# Dashboard Title
st.title("��� V2V Traffic Management System Dashboard")
st.markdown("**Comparing V2V-Enabled vs Non-V2V Vehicles**")
st.markdown("---")

# Sidebar controls
st.sidebar.header("⚙️ Dashboard Controls")
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 2)
show_comparison = st.sidebar.checkbox("Show Detailed Comparison", value=True)
show_events = st.sidebar.checkbox("Show Recent Events", value=True)

# Auto-refresh component - updates data without page reload
st_autorefresh(interval=refresh_rate * 1000, limit=None, key="data_refresh")

@st.cache_data(ttl=1)
def fetch_vehicles():
    """Fetch vehicle data from server"""
    try:
        response = requests.get(f"{SERVER_URL}/api/vehicles", timeout=5)
        return response.json()
    except:
        return {'all_vehicles': [], 'v2v_vehicles': [], 'non_v2v_vehicles': [], 
                'total_count': 0, 'v2v_count': 0, 'non_v2v_count': 0}

@st.cache_data(ttl=1)
def fetch_comparison():
    """Fetch comparison metrics"""
    try:
        response = requests.get(f"{SERVER_URL}/api/comparison", timeout=5)
        return response.json()
    except:
        return None

# Fetch data once
vehicle_data = fetch_vehicles()
comparison_data = fetch_comparison()

all_vehicles = vehicle_data.get('all_vehicles', [])
v2v_vehicles = vehicle_data.get('v2v_vehicles', [])
non_v2v_vehicles = vehicle_data.get('non_v2v_vehicles', [])

# Display main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("��� Total Vehicles", vehicle_data.get('total_count', 0))

with col2:
    v2v_count = vehicle_data.get('v2v_count', 0)
    st.metric("✅ V2V-Enabled", v2v_count, 
             delta="Smart" if v2v_count > 0 else None,
             delta_color="normal")

with col3:
    non_v2v_count = vehicle_data.get('non_v2v_count', 0)
    st.metric("❌ Non-V2V", non_v2v_count,
             delta="Legacy" if non_v2v_count > 0 else None,
             delta_color="inverse")

with col4:
    emergency_count = len([v for v in all_vehicles if v.get('type') == 'emergency'])
    st.metric("��� Emergency", emergency_count,
             delta="Priority" if emergency_count > 0 else None,
             delta_color="off")

# Comparison metrics
if show_comparison and comparison_data:
    st.markdown("### ��� V2V vs Non-V2V Comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ V2V-Enabled Vehicles")
        v2v_metrics = comparison_data.get('v2v_enabled', {})
        subcol1, subcol2, subcol3 = st.columns(3)
        with subcol1:
            st.metric("Avg Speed", f"{v2v_metrics.get('average_speed', 0):.1f} km/h")
        with subcol2:
            st.metric("Efficiency", f"{v2v_metrics.get('traffic_flow_efficiency', 0):.1f}%")
        with subcol3:
            st.metric("Accidents Prevented", v2v_metrics.get('accidents_prevented', 0))
        subcol1, subcol2, subcol3 = st.columns(3)
        with subcol1:
            st.metric("Near Misses", v2v_metrics.get('near_misses', 0))
        with subcol2:
            st.metric("Emergency Stops", v2v_metrics.get('stops_for_emergency', 0))
        with subcol3:
            st.metric("Active", v2v_metrics.get('total_vehicles', 0))
    with col2:
        st.markdown("#### ❌ Non-V2V Vehicles")
        non_v2v_metrics = comparison_data.get('non_v2v', {})
        subcol1, subcol2, subcol3 = st.columns(3)
        with subcol1:
            st.metric("Avg Speed", f"{non_v2v_metrics.get('average_speed', 0):.1f} km/h")
        with subcol2:
            st.metric("Efficiency", f"{non_v2v_metrics.get('traffic_flow_efficiency', 0):.1f}%")
        with subcol3:
            st.metric("Accidents", non_v2v_metrics.get('accidents', 0), delta_color="inverse")
        subcol1, subcol2, subcol3 = st.columns(3)
        with subcol1:
            st.metric("Near Misses", non_v2v_metrics.get('near_misses', 0))
        with subcol2:
            st.metric("Emergency Conflicts", non_v2v_metrics.get('emergency_conflicts', 0), delta_color="inverse")
        with subcol3:
            st.metric("Active", non_v2v_metrics.get('total_vehicles', 0))
    # Improvements
    improvements = comparison_data.get('improvements', {})
    st.markdown("### ��� Performance Improvements (V2V vs Non-V2V)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        speed_imp = improvements.get('speed_increase_percent', 0)
        st.metric("Speed Increase", f"{speed_imp:+.1f}%",
                 delta="Better" if speed_imp > 0 else "Worse",
                 delta_color="normal" if speed_imp > 0 else "inverse")
    with col2:
        eff_imp = improvements.get('efficiency_increase_percent', 0)
        st.metric("Efficiency Gain", f"{eff_imp:+.1f}%",
                 delta="Better" if eff_imp > 0 else "Worse",
                 delta_color="normal" if eff_imp > 0 else "inverse")
    with col3:
        prevented = improvements.get('accidents_prevented', 0)
        occurred = improvements.get('accidents_occurred', 0)
        st.metric("Safety", f"{prevented} prevented vs {occurred} occurred",
                 delta=f"{prevented - occurred:+d}")
    with col4:
        emergency_better = improvements.get('emergency_response_better', False)
        st.metric("Emergency Response", "✅ Better" if emergency_better else "❌ Same",
                 delta="V2V Advantage" if emergency_better else None)
    st.markdown("---")

# Create map visualization
if all_vehicles:
    # Enhanced header with gradient styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; 
                border-radius: 10px; 
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: white; margin: 0; text-align: center;">
            🗺️ Real-time Vehicle Tracking Map
        </h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; text-align: center; font-size: 14px;">
            Live positions and status of all vehicles in the network
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Prepare data for plotting with enhanced tracking
    vehicle_ids = []
    x_coords = []
    y_coords = []
    speeds = []
    types = []
    v2v_status = []
    
    for v in all_vehicles:
        vehicle_ids.append(v.get('id', 'Unknown'))
        x_coords.append(v['location']['x'])
        y_coords.append(v['location']['y'])
        speeds.append(v['speed'])
        types.append(v.get('type', 'normal'))
        v2v_status.append(v.get('v2v_enabled', False))
    
    # Create enhanced scatter plot with Plotly
    fig = go.Figure()
    
    # Add emergency vehicles with pulsing star effect
    emergency_mask = [t == 'emergency' for t in types]
    if any(emergency_mask):
        emergency_x = [x for x, m in zip(x_coords, emergency_mask) if m]
        emergency_y = [y for y, m in zip(y_coords, emergency_mask) if m]
        emergency_speeds = [s for s, m in zip(speeds, emergency_mask) if m]
        
        fig.add_trace(go.Scatter(
            x=emergency_x,
            y=emergency_y,
            mode='markers+text',
            name='🚑 Emergency Vehicle',
            marker=dict(
                size=35,
                color='#FF0000',
                symbol='square',
                line=dict(width=3, color='#FFD700'),
                opacity=1
            ),
            text=['�'] * len(emergency_x),
            textfont=dict(size=24, color='white'),
            textposition="middle center",
            hovertemplate='<b style="color: #FF0000;">� EMERGENCY VEHICLE 🚨</b><br>' +
                         'Speed: %{customdata:.1f} km/h<br>' +
                         'Position: (%{x:.0f}m, Lane %{y:.0f}m)<br>' +
                         '<i>Priority Response Active - All vehicles yield</i><extra></extra>',
            customdata=emergency_speeds
        ))
    
    # Add V2V vehicles with AI car icon
    v2v_normal_mask = [v and t != 'emergency' for v, t in zip(v2v_status, types)]
    if any(v2v_normal_mask):
        v2v_x = [x for x, m in zip(x_coords, v2v_normal_mask) if m]
        v2v_y = [y for y, m in zip(y_coords, v2v_normal_mask) if m]
        v2v_speeds = [s for s, m in zip(speeds, v2v_normal_mask) if m]
        
        fig.add_trace(go.Scatter(
            x=v2v_x,
            y=v2v_y,
            mode='markers+text',
            name='🤖 AI-Enabled Vehicle',
            marker=dict(
                size=28,
                color=v2v_speeds,
                colorscale=[[0, '#1E88E5'], [0.5, '#42A5F5'], [1, '#90CAF9']],
                showscale=True,
                colorbar=dict(
                    title="Speed<br>(km/h)",
                    thickness=15,
                    len=0.5,
                    x=1.15,
                    bgcolor='rgba(255,255,255,0.9)',
                    borderwidth=1,
                    bordercolor='#CCCCCC'
                ),
                symbol='square',
                line=dict(width=2, color='#0D47A1'),
                opacity=0.95
            ),
            text=['🚗'] * len(v2v_x),
            textfont=dict(size=20, color='white'),
            textposition="middle center",
            hovertemplate='<b style="color: #1E88E5;">🤖 AI-Enabled Vehicle</b><br>' +
                         'Speed: %{marker.color:.1f} km/h<br>' +
                         'Position: (%{x:.0f}m, Lane %{y:.0f}m)<br>' +
                         '<i>✓ V2V Connected | ✓ Auto-Collision Avoidance</i><extra></extra>'
        ))
    
    # Add Non-V2V vehicles (legacy cars)
    non_v2v_mask = [not v and t != 'emergency' for v, t in zip(v2v_status, types)]
    if any(non_v2v_mask):
        non_v2v_x = [x for x, m in zip(x_coords, non_v2v_mask) if m]
        non_v2v_y = [y for y, m in zip(y_coords, non_v2v_mask) if m]
        non_v2v_speeds = [s for s, m in zip(speeds, non_v2v_mask) if m]
        
        fig.add_trace(go.Scatter(
            x=non_v2v_x,
            y=non_v2v_y,
            mode='markers+text',
            name='🚙 Legacy Vehicle',
            marker=dict(
                size=24,
                color='#757575',
                symbol='square',
                line=dict(width=2, color='#424242'),
                opacity=0.75
            ),
            text=['🚙'] * len(non_v2v_x),
            textfont=dict(size=18, color='white'),
            textposition="middle center",
            hovertemplate='<b style="color: #757575;">🚙 Legacy Vehicle</b><br>' +
                         'Speed: %{customdata:.1f} km/h<br>' +
                         'Position: (%{x:.0f}m, Lane %{y:.0f}m)<br>' +
                         '<i>⚠️ No V2V Communication | Manual Control</i><extra></extra>',
            customdata=non_v2v_speeds
        ))
    
    # Add road and lane markings
    if x_coords and y_coords:
        x_min, x_max = min(x_coords) - 100, max(x_coords) + 100
        y_min, y_max = min(y_coords) - 100, max(y_coords) + 100
        
        # Draw main road (asphalt background)
        fig.add_shape(
            type="rect",
            x0=x_min, y0=y_min,
            x1=x_max, y1=y_max,
            fillcolor="#2C3E50",  # Dark asphalt color
            line=dict(width=0),
            layer="below"
        )
        
        # Draw road edges (yellow lines)
        fig.add_shape(
            type="line",
            x0=x_min, y0=y_min,
            x1=x_max, y1=y_min,
            line=dict(color="#FFD700", width=4),
            layer="below"
        )
        fig.add_shape(
            type="line",
            x0=x_min, y0=y_max,
            x1=x_max, y1=y_max,
            line=dict(color="#FFD700", width=4),
            layer="below"
        )
        
        # Calculate lane divisions (4 lanes)
        num_lanes = 4
        lane_height = (y_max - y_min) / num_lanes
        
        # Draw lane dividers (white dashed lines)
        for i in range(1, num_lanes):
            y_pos = y_min + (i * lane_height)
            # Create dashed effect with multiple short lines
            dash_length = 40
            gap_length = 30
            x_pos = x_min
            while x_pos < x_max:
                fig.add_shape(
                    type="line",
                    x0=x_pos, y0=y_pos,
                    x1=min(x_pos + dash_length, x_max), y1=y_pos,
                    line=dict(color="white", width=3, dash="solid"),
                    layer="below"
                )
                x_pos += dash_length + gap_length
    
    # Enhanced layout with professional styling
    fig.update_layout(
        title=dict(
            text=f"<b>🛣️ Highway Traffic Monitor - {len(all_vehicles)} Vehicles</b>",
            font=dict(size=16, color='#333'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text="<b>Distance Along Road (meters)</b>", font=dict(size=14, color='#555')),
            showgrid=False,
            zeroline=False,
            showline=False
        ),
        yaxis=dict(
            title=dict(text="<b>Lanes</b>", font=dict(size=14, color='#555')),
            showgrid=False,
            zeroline=False,
            showline=False
        ),
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#CCCCCC",
            borderwidth=2,
            font=dict(size=12)
        ),
        hovermode='closest',
        plot_bgcolor='#34495E',  # Darker background for contrast
        paper_bgcolor='white',
        margin=dict(l=50, r=50, t=80, b=50),
        font=dict(family="Arial, sans-serif")
    )
    
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d']
    })
    
    # Speed distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Speed Distribution")
        
        # Create histogram
        fig_speed = go.Figure()
        
        if v2v_vehicles:
            v2v_speeds = [v['speed'] for v in v2v_vehicles]
            fig_speed.add_trace(go.Histogram(
                x=v2v_speeds,
                name='V2V-Enabled',
                marker_color='blue',
                opacity=0.7
            ))
        
        if non_v2v_vehicles:
            non_v2v_speeds = [v['speed'] for v in non_v2v_vehicles]
            fig_speed.add_trace(go.Histogram(
                x=non_v2v_speeds,
                name='Non-V2V',
                marker_color='gray',
                opacity=0.7
            ))
        
        fig_speed.update_layout(
            barmode='overlay',
            xaxis_title='Speed (km/h)',
            yaxis_title='Count',
            height=300
        )
        
        st.plotly_chart(fig_speed, use_container_width=True)
    
    with col2:
        st.markdown("#### Traffic Flow Efficiency")
        
        if comparison_data:
            categories = ['V2V-Enabled', 'Non-V2V']
            efficiency_values = [
                comparison_data.get('v2v_enabled', {}).get('traffic_flow_efficiency', 0),
                comparison_data.get('non_v2v', {}).get('traffic_flow_efficiency', 0)
            ]
            
            fig_eff = go.Figure(data=[
                go.Bar(
                    x=categories,
                    y=efficiency_values,
                    marker_color=['blue', 'gray'],
                    text=[f"{v:.1f}%" for v in efficiency_values],
                    textposition='auto'
                )
            ])
            
            fig_eff.update_layout(
                yaxis_title='Efficiency (%)',
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig_eff, use_container_width=True)
    
    # Vehicle table
    st.markdown("### ��� Vehicle Details")
    
    # Create DataFrame
    df_data = []
    for v in all_vehicles:
        vtype = v.get('type', 'normal')
        is_v2v = v.get('v2v_enabled', False)
        
        if vtype == 'emergency':
            type_label = "��� Emergency"
        elif is_v2v:
            type_label = "✅ V2V"
        else:
            type_label = "❌ Non-V2V"
        
        df_data.append({
            'Type': type_label,
            'Speed (km/h)': f"{v['speed']:.1f}",
            'X Position': f"{v['location']['x']:.0f}m",
            'Y Position': f"{v['location']['y']:.0f}m",
            'Status': v.get('status', 'active').upper()
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, height=300)

else:
    st.warning("⚠️ No vehicles connected. Start the simulation to see data.")
    st.info("��� Run: `python vehicles/vehicle_simulator.py`")

# Recent events
if show_events and comparison_data:
    st.markdown("### ��� Recent Events")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Collision Events")
        collision_history = comparison_data.get('collision_history', [])
        if collision_history:
            for event in collision_history[-5:]:
                severity = event.get('severity', 'unknown')
                if severity == 'avoided':
                    st.success(f"✅ Collision avoided between {event.get('vehicle1')} and {event.get('vehicle2')}")
                else:
                    st.error(f"⚠️ {severity}: {event.get('vehicle1')} and {event.get('vehicle2')}")
        else:
            st.info("No collision events recorded")
    
    with col2:
        st.markdown("#### Emergency Events")
        emergency_events = comparison_data.get('emergency_events', [])
        if emergency_events:
            for event in emergency_events[-5:]:
                st.warning(f"��� Emergency vehicle {event.get('vehicle_id')} - {event.get('v2v_aware_count')} V2V vehicles alerted")
        else:
            st.info("No emergency events recorded")

# Footer with refresh info
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refreshing every {refresh_rate}s")
