from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError

from database import Base, SessionLocal, engine
from models import ParkingSlot
from schemas import ParkingSlotCreate

Base.metadata.create_all(bind=engine)

app = FastAPI()


def response_format(status_code, message, error, data, path):
    return {
        "statusCode": status_code,
        "message": message,
        "error": error,
        "data": data,
        "path": path,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/parking-slots", status_code=status.HTTP_201_CREATED)
def create_slot(slot: ParkingSlotCreate):

    db = SessionLocal()

    try:

        new_slot = ParkingSlot(
            slot_code=slot.slot_code,
            zone_name=slot.zone_name,
            max_weight=slot.max_weight
        )

        db.add(new_slot)
        db.commit()
        db.refresh(new_slot)

        return response_format(
            201,
            "Thêm vị trí đỗ xe thành công",
            None,
            {
                "id": new_slot.id,
                "slot_code": new_slot.slot_code,
                "zone_name": new_slot.zone_name,
                "max_weight": new_slot.max_weight,
                "is_available": new_slot.is_available
            },
            "/parking-slots"
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Slot code already exists"
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

    finally:
        db.close()


@app.get("/parking-slots")
def get_all_slots():

    db = SessionLocal()

    try:

        slots = db.query(ParkingSlot).all()

        data = []

        for slot in slots:
            data.append({
                "id": slot.id,
                "slot_code": slot.slot_code,
                "zone_name": slot.zone_name,
                "max_weight": slot.max_weight,
                "is_available": slot.is_available
            })

        return response_format(
            200,
            "Lấy danh sách vị trí đỗ xe thành công",
            None,
            data,
            "/parking-slots"
        )

    finally:
        db.close()


@app.get("/parking-slots/{slot_id}")
def get_slot(slot_id: int):

    db = SessionLocal()

    try:

        slot = db.query(ParkingSlot).filter(
            ParkingSlot.id == slot_id
        ).first()

        if slot is None:
            raise HTTPException(
                status_code=404,
                detail="Parking slot not found"
            )

        return response_format(
            200,
            "Lấy chi tiết vị trí đỗ xe thành công",
            None,
            {
                "id": slot.id,
                "slot_code": slot.slot_code,
                "zone_name": slot.zone_name,
                "max_weight": slot.max_weight,
                "is_available": slot.is_available
            },
            f"/parking-slots/{slot_id}"
        )

    finally:
        db.close()