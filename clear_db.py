from app.database import SessionLocal
from app.models import ParkingEntry

db = SessionLocal()

# Διαγραφή ΟΛΩΝ των εγγραφών
db.query(ParkingEntry).delete(synchronize_session='fetch')  # fetch για να ενημερώσει σωστά τη session
db.commit()
db.close()

print("Η βάση έχει καθαριστεί πλήρως!")
