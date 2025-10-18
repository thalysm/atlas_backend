from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ...application.use_cases.reminder_use_cases import ReminderUseCases
from ...infrastructure.repositories.reminder_repository import ReminderRepository
from ...core.database import get_database
from ..dependencies import get_current_user_id
from ..schemas.reminder_schemas import CreateReminderRequest, ReminderResponse, UpdateReminderRequest

router = APIRouter(prefix="/reminders", tags=["Reminders"])

def get_reminder_use_cases() -> ReminderUseCases:
    db = get_database()
    repo = ReminderRepository(db)
    return ReminderUseCases(repo)

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    request: CreateReminderRequest,
    user_id: str = Depends(get_current_user_id),
    use_cases: ReminderUseCases = Depends(get_reminder_use_cases),
):
    # Validação básica para frequency_details
    if request.frequency == 'weekly' and not isinstance(request.frequency_details, list):
        raise HTTPException(status_code=400, detail="Weekly frequency requires a list of days (0-6).")
    if request.frequency == 'monthly' and not isinstance(request.frequency_details, int):
        raise HTTPException(status_code=400, detail="Monthly frequency requires a specific day of the month (1-31).")
    if request.frequency == 'daily' and request.frequency_details is not None:
         raise HTTPException(status_code=400, detail="Daily frequency does not require details.")

    reminder_id = await use_cases.create_reminder(
        user_id,
        request.title,
        request.time,
        request.frequency,
        request.frequency_details
    )
    return {"id": reminder_id}

@router.get("", response_model=List[ReminderResponse])
async def get_reminders(
    user_id: str = Depends(get_current_user_id),
    use_cases: ReminderUseCases = Depends(get_reminder_use_cases),
):
    return await use_cases.get_user_reminders(user_id)

@router.get("/today", response_model=List[ReminderResponse])
async def get_today_reminders(
    user_id: str = Depends(get_current_user_id),
    use_cases: ReminderUseCases = Depends(get_reminder_use_cases),
):
    return await use_cases.get_today_reminders(user_id)

@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    request: UpdateReminderRequest,
    user_id: str = Depends(get_current_user_id),
    use_cases: ReminderUseCases = Depends(get_reminder_use_cases),
):
    """Update an existing reminder"""
    # Validação para frequency_details (similar à criação, mas para campos opcionais)
    if request.frequency == 'weekly' and not isinstance(request.frequency_details, list):
         # Permitir limpar detalhes se a frequência mudar
        if request.frequency_details is not Ellipsis and request.frequency_details is not None:
             raise HTTPException(status_code=400, detail="Weekly frequency requires a list of days (0-6) or null.")
    if request.frequency == 'monthly' and not isinstance(request.frequency_details, int):
         if request.frequency_details is not Ellipsis and request.frequency_details is not None:
            raise HTTPException(status_code=400, detail="Monthly frequency requires a day (1-31) or null.")
    if request.frequency == 'daily' and request.frequency_details is not None and request.frequency_details is not Ellipsis:
         raise HTTPException(status_code=400, detail="Daily frequency does not require details.")

    try:
        # Passar Ellipsis como None explicitamente
        freq_details = request.frequency_details if request.frequency_details is not Ellipsis else None
        
        success = await use_cases.update_reminder(
            reminder_id,
            user_id,
            request.title,
            request.time,
            request.frequency,
            freq_details
        )
        if success:
             # Retorna o lembrete atualizado formatado
            updated_reminder_entity = await use_cases.reminder_repository.find_by_id(reminder_id)
            if updated_reminder_entity:
                 return use_cases._format_reminder(updated_reminder_entity)
            else:
                 # Caso raro onde a atualização sucede mas a busca falha
                 raise HTTPException(status_code=404, detail="Reminder updated but could not be retrieved")
        else:
             # Isso não deveria acontecer com update_one se não houver erro, mas por segurança
             raise HTTPException(status_code=400, detail="Could not update reminder")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
         # Logar o erro real aqui seria importante
         print(f"Error updating reminder: {e}")
         raise HTTPException(status_code=500, detail="Internal server error while updating reminder.")

@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id),
    use_cases: ReminderUseCases = Depends(get_reminder_use_cases),
):
    try:
        await use_cases.delete_reminder(reminder_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{reminder_id}/toggle", response_model=dict)
async def toggle_reminder(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id),
    use_cases: ReminderUseCases = Depends(get_reminder_use_cases),
):
    try:
        await use_cases.toggle_today_completion(reminder_id, user_id)
        return {"message": "Reminder updated"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))