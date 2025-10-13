"""
Maintenance Tracking Service
Track CNG kit maintenance, service reminders, and vehicle health
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from models.cng_calculator import db
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text


class MaintenanceRecord(db.Model):
    """Track maintenance history"""
    __tablename__ = 'maintenance_records'
    
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    service_type = Column(String(100), nullable=False)  # cng_kit_check, full_service, etc.
    service_date = Column(DateTime, nullable=False)
    odometer_reading = Column(Float)
    cost = Column(Float)
    service_center = Column(String(200))
    notes = Column(Text)
    next_service_km = Column(Float)
    next_service_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class MaintenanceReminder(db.Model):
    """Track upcoming maintenance reminders"""
    __tablename__ = 'maintenance_reminders'
    
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    reminder_type = Column(String(100), nullable=False)
    due_date = Column(DateTime)
    due_odometer = Column(Float)
    is_completed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class MaintenanceService:
    """Service for managing vehicle and CNG kit maintenance"""
    
    # CNG Kit specific maintenance intervals
    CNG_MAINTENANCE_INTERVALS = {
        'pressure_test': {
            'interval_months': 3,
            'interval_km': 5000,
            'cost_estimate': 500,
            'description': 'CNG cylinder pressure test'
        },
        'valve_check': {
            'interval_months': 6,
            'interval_km': 10000,
            'cost_estimate': 800,
            'description': 'CNG valve and regulator check'
        },
        'full_inspection': {
            'interval_months': 12,
            'interval_km': 15000,
            'cost_estimate': 2000,
            'description': 'Complete CNG kit inspection'
        },
        'cylinder_recertification': {
            'interval_months': 36,
            'interval_km': None,
            'cost_estimate': 5000,
            'description': 'CNG cylinder hydro test (mandatory every 3 years)'
        }
    }
    
    def add_maintenance_record(
        self,
        vehicle_id: int,
        service_type: str,
        service_date: datetime,
        cost: float,
        odometer_reading: Optional[float] = None,
        service_center: Optional[str] = None,
        notes: Optional[str] = None
    ) -> MaintenanceRecord:
        """Add a new maintenance record"""
        
        # Calculate next service
        next_service = self._calculate_next_service(
            service_type,
            service_date,
            odometer_reading
        )
        
        record = MaintenanceRecord(
            vehicle_id=vehicle_id,
            service_type=service_type,
            service_date=service_date,
            cost=cost,
            odometer_reading=odometer_reading,
            service_center=service_center,
            notes=notes,
            next_service_date=next_service['date'],
            next_service_km=next_service['km']
        )
        
        db.session.add(record)
        
        # Create reminder for next service
        if next_service['date'] or next_service['km']:
            self.create_reminder(
                vehicle_id,
                service_type,
                next_service['date'],
                next_service['km']
            )
        
        db.session.commit()
        return record
    
    def create_reminder(
        self,
        vehicle_id: int,
        reminder_type: str,
        due_date: Optional[datetime] = None,
        due_odometer: Optional[float] = None
    ) -> MaintenanceReminder:
        """Create a maintenance reminder"""
        
        # Deactivate existing reminders of same type
        existing = MaintenanceReminder.query.filter_by(
            vehicle_id=vehicle_id,
            reminder_type=reminder_type,
            is_completed=False
        ).all()
        
        for reminder in existing:
            reminder.is_active = False
        
        # Create new reminder
        reminder = MaintenanceReminder(
            vehicle_id=vehicle_id,
            reminder_type=reminder_type,
            due_date=due_date,
            due_odometer=due_odometer
        )
        
        db.session.add(reminder)
        db.session.commit()
        return reminder
    
    def get_upcoming_maintenance(
        self,
        vehicle_id: int,
        days_ahead: int = 30,
        current_odometer: Optional[float] = None
    ) -> List[Dict]:
        """Get upcoming maintenance for a vehicle"""
        
        reminders = MaintenanceReminder.query.filter_by(
            vehicle_id=vehicle_id,
            is_completed=False,
            is_active=True
        ).all()
        
        upcoming = []
        now = datetime.utcnow()
        future_date = now + timedelta(days=days_ahead)
        
        for reminder in reminders:
            is_upcoming = False
            urgency = 'normal'
            
            # Check date-based reminder
            if reminder.due_date:
                if reminder.due_date <= future_date:
                    is_upcoming = True
                    days_until = (reminder.due_date - now).days
                    if days_until <= 7:
                        urgency = 'urgent'
                    elif days_until <= 14:
                        urgency = 'soon'
            
            # Check odometer-based reminder
            if current_odometer and reminder.due_odometer:
                km_until = reminder.due_odometer - current_odometer
                if km_until <= 1000:
                    is_upcoming = True
                    if km_until <= 200:
                        urgency = 'urgent'
                    elif km_until <= 500:
                        urgency = 'soon'
            
            if is_upcoming:
                maintenance_info = self.CNG_MAINTENANCE_INTERVALS.get(
                    reminder.reminder_type,
                    {}
                )
                
                upcoming.append({
                    'id': reminder.id,
                    'type': reminder.reminder_type,
                    'description': maintenance_info.get('description', reminder.reminder_type),
                    'due_date': reminder.due_date.isoformat() if reminder.due_date else None,
                    'due_odometer': reminder.due_odometer,
                    'urgency': urgency,
                    'estimated_cost': maintenance_info.get('cost_estimate', 0),
                    'days_until': (reminder.due_date - now).days if reminder.due_date else None,
                    'km_until': km_until if current_odometer and reminder.due_odometer else None
                })
        
        # Sort by urgency
        urgency_order = {'urgent': 0, 'soon': 1, 'normal': 2}
        upcoming.sort(key=lambda x: urgency_order.get(x['urgency'], 3))
        
        return upcoming
    
    def get_maintenance_history(
        self,
        vehicle_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """Get maintenance history for a vehicle"""
        
        records = MaintenanceRecord.query.filter_by(
            vehicle_id=vehicle_id
        ).order_by(
            MaintenanceRecord.service_date.desc()
        ).limit(limit).all()
        
        history = []
        for record in records:
            history.append({
                'id': record.id,
                'service_type': record.service_type,
                'service_date': record.service_date.isoformat(),
                'cost': record.cost,
                'odometer_reading': record.odometer_reading,
                'service_center': record.service_center,
                'notes': record.notes,
                'next_service_date': record.next_service_date.isoformat() if record.next_service_date else None,
                'next_service_km': record.next_service_km
            })
        
        return history
    
    def calculate_maintenance_cost_projection(
        self,
        vehicle_id: int,
        months_ahead: int = 12
    ) -> Dict:
        """Project maintenance costs for upcoming period"""
        
        from models.cng_calculator import Vehicle
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            raise ValueError("Vehicle not found")
        
        projected_costs = []
        total_cost = 0
        
        # Get upcoming maintenance
        upcoming = self.get_upcoming_maintenance(vehicle_id, days_ahead=months_ahead * 30)
        
        for maintenance in upcoming:
            cost = maintenance['estimated_cost']
            total_cost += cost
            projected_costs.append({
                'type': maintenance['type'],
                'description': maintenance['description'],
                'due_date': maintenance['due_date'],
                'estimated_cost': cost
            })
        
        # Add routine maintenance estimates
        if vehicle.is_cng_converted:
            # CNG specific costs
            routine_cng_cost = self._estimate_routine_cng_maintenance(months_ahead)
            total_cost += routine_cng_cost
            projected_costs.append({
                'type': 'routine_cng',
                'description': 'Routine CNG maintenance',
                'estimated_cost': routine_cng_cost
            })
        
        # Regular vehicle maintenance
        routine_cost = self._estimate_routine_vehicle_maintenance(months_ahead)
        total_cost += routine_cost
        projected_costs.append({
            'type': 'routine_vehicle',
            'description': 'Regular vehicle service',
            'estimated_cost': routine_cost
        })
        
        return {
            'vehicle_id': vehicle_id,
            'projection_months': months_ahead,
            'projected_items': projected_costs,
            'total_estimated_cost': round(total_cost, 2),
            'monthly_average': round(total_cost / months_ahead, 2)
        }
    
    def mark_reminder_completed(
        self,
        reminder_id: int,
        completed_date: Optional[datetime] = None
    ):
        """Mark a reminder as completed"""
        reminder = MaintenanceReminder.query.get(reminder_id)
        if reminder:
            reminder.is_completed = True
            reminder.completed_at = completed_date or datetime.utcnow()
            db.session.commit()
    
    def get_maintenance_statistics(
        self,
        vehicle_id: int
    ) -> Dict:
        """Get maintenance statistics for a vehicle"""
        
        records = MaintenanceRecord.query.filter_by(
            vehicle_id=vehicle_id
        ).all()
        
        if not records:
            return {
                'total_records': 0,
                'total_spent': 0,
                'average_cost': 0,
                'last_service_date': None
            }
        
        total_spent = sum(r.cost for r in records if r.cost)
        last_service = max(records, key=lambda x: x.service_date)
        
        # Calculate by service type
        by_type = {}
        for record in records:
            if record.service_type not in by_type:
                by_type[record.service_type] = {
                    'count': 0,
                    'total_cost': 0
                }
            by_type[record.service_type]['count'] += 1
            by_type[record.service_type]['total_cost'] += record.cost or 0
        
        return {
            'total_records': len(records),
            'total_spent': round(total_spent, 2),
            'average_cost': round(total_spent / len(records), 2),
            'last_service_date': last_service.service_date.isoformat(),
            'by_service_type': by_type
        }
    
    def _calculate_next_service(
        self,
        service_type: str,
        service_date: datetime,
        odometer_reading: Optional[float]
    ) -> Dict:
        """Calculate next service date and km"""
        
        interval = self.CNG_MAINTENANCE_INTERVALS.get(service_type)
        
        next_date = None
        next_km = None
        
        if interval:
            if interval['interval_months']:
                next_date = service_date + timedelta(days=interval['interval_months'] * 30)
            
            if interval['interval_km'] and odometer_reading:
                next_km = odometer_reading + interval['interval_km']
        
        return {
            'date': next_date,
            'km': next_km
        }
    
    def _estimate_routine_cng_maintenance(self, months: int) -> float:
        """Estimate routine CNG maintenance costs"""
        # Average monthly CNG maintenance
        monthly_cost = 300  # Approximate
        return monthly_cost * months
    
    def _estimate_routine_vehicle_maintenance(self, months: int) -> float:
        """Estimate routine vehicle maintenance costs"""
        # Average monthly vehicle maintenance
        monthly_cost = 500  # Approximate
        return monthly_cost * months
